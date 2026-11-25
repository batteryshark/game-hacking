#!/usr/bin/env python3
"""
Create a new game layer from a base Windows 98 image.

Usage:
    python create_game_layer.py <game_name> --base <base_key> [--cd <path>]
    
Example:
    python create_game_layer.py rpg95 --base win98se_jp --cd ../Rpg95.cue
"""
import argparse
import json
import shutil
import subprocess
import sys
import os
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from toolkit.config import (
    get_base_image_path, get_base_image_keys, get_base_image_info,
    get_game_dir, GAMES_DIR, DOSBOX_APP, ensure_dirs, load_config_template,
    verify_dosbox
)
from toolkit.vhd_utils import create_differencing_vhd


def create_game_config(game_dir: Path, game_name: str, base_key: str, cd_path: Path = None) -> dict:
    """Create and save game.json config file."""
    base_info = get_base_image_info(base_key)
    
    config = {
        "name": game_name,
        "base_image_key": base_key,
        "base_image_name": base_info.get("name", base_key) if base_info else base_key,
        "cd_image": None,
        "notes": ""
    }
    
    if cd_path:
        # Copy CD image to game's cd/ folder
        cd_dir = game_dir / "cd"
        cd_dir.mkdir(exist_ok=True)
        
        cd_src = Path(cd_path).resolve()
        cd_dest = cd_dir / cd_src.name
        
        if not cd_dest.exists():
            print(f"Copying CD image: {cd_src.name}")
            shutil.copy2(cd_src, cd_dest)
            
            # Also copy .bin file if it's a .cue
            if cd_src.suffix.lower() == '.cue':
                bin_src = cd_src.with_suffix('.bin')
                if bin_src.exists():
                    print(f"Copying CD data: {bin_src.name}")
                    shutil.copy2(bin_src, cd_dir / bin_src.name)
        
        config["cd_image"] = f"cd/{cd_src.name}"
    
    # Save config
    config_path = game_dir / "game.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Created game config: {config_path.name}")
    return config


def generate_game_conf(game_dir: Path, game_name: str, vhd_path: Path, cd_image: Path = None):
    """Generate DOSBox-X config file for this game."""
    template = load_config_template()
    
    # Build autoexec section
    autoexec_lines = [
        f'IMGMOUNT c "{vhd_path}"',
        f'MOUNT d "{game_dir}" -nocachedir',
    ]
    if cd_image:
        autoexec_lines.append(f'IMGMOUNT e "{cd_image}" -t cdrom -ide 2m')
    autoexec_lines.append('BOOT -l c')
    
    # Fill template
    config_content = template.format(
        title=game_name,
        c_drive_vhd=str(vhd_path),
        d_drive_folder=str(game_dir),
        cd_image=str(cd_image) if cd_image else "",
        autoexec='\n'.join(autoexec_lines)
    )
    
    # Write config file
    conf_path = game_dir / "dosbox.conf"
    conf_path.write_text(config_content)
    print(f"✓ Created DOSBox config: {conf_path.name}")
    return conf_path


def launch_install_mode(game_dir: Path, base_vhd: Path, cd_image: Path = None):
    """Launch DOSBox-X in install mode for the user to install the game."""
    
    game_vhd = game_dir / "game.vhd"
    
    # Create the differencing VHD from base
    print(f"\nCreating game layer VHD...")
    if not create_differencing_vhd(base_vhd, game_vhd):
        print("✗ Failed to create game VHD")
        return False
    
    # Generate config file
    conf_path = generate_game_conf(game_dir, f"Installing: {game_dir.name}", game_vhd, cd_image)
    
    print(f"\n" + "="*60)
    print("INSTALL MODE")
    print("="*60)
    print(f"Game VHD: {game_vhd}")
    print(f"D: drive: {game_dir} (for file transfers)")
    if cd_image:
        print(f"E: drive: {cd_image} (CD-ROM)")
    print()
    print("Windows 98 will now boot. Install your game, then shut down.")
    print("="*60 + "\n")
    
    try:
        subprocess.run([str(DOSBOX_APP), "-conf", str(conf_path)])
        
        # Update config title after install
        generate_game_conf(game_dir, game_dir.name, game_vhd, cd_image)
        
        print("\n✓ Installation session complete")
        return True
    except Exception as e:
        print(f"✗ Error launching DOSBox-X: {e}")
        return False


def list_base_images():
    """List available base images."""
    from toolkit.config import load_base_images, BASE_IMAGES_DIR
    
    images = load_base_images()
    if not images:
        print(f"No base images configured. Add them to: {BASE_IMAGES_DIR / 'base_images.json'}")
        return
    
    print("Available base images:")
    for key, info in images.items():
        file_path = BASE_IMAGES_DIR / info["file"]
        exists = "✓" if file_path.exists() else "✗"
        print(f"  {exists} {key}: {info.get('name', 'Unknown')}")
        if info.get("description"):
            print(f"      {info['description']}")


def main():
    parser = argparse.ArgumentParser(
        description="Create a new game layer from a base Windows 98 image"
    )
    parser.add_argument("game_name", nargs="?", help="Name for the game (used as folder name)")
    parser.add_argument("--base", "-b", help="Base image key (run with --list-bases to see available)")
    parser.add_argument("--cd", "-c", help="Path to CD image (.cue or .iso)")
    parser.add_argument("--skip-install", action="store_true",
                        help="Create layer without launching install mode")
    parser.add_argument("--list-bases", "-l", action="store_true",
                        help="List available base images")
    
    args = parser.parse_args()
    
    if args.list_bases:
        list_base_images()
        return
    
    # Verify DOSBox-X is available (unless just listing)
    try:
        verify_dosbox()
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    if not args.game_name:
        parser.print_help()
        print("\nRun with --list-bases to see available base images")
        return
    
    if not args.base:
        print("Error: --base is required")
        print("\nAvailable base images:")
        list_base_images()
        sys.exit(1)
    
    ensure_dirs()
    
    # Check if game already exists
    game_dir = get_game_dir(args.game_name)
    if game_dir.exists():
        print(f"✗ Game already exists: {game_dir}")
        print("  Delete the folder first if you want to recreate it.")
        sys.exit(1)
    
    # Get base image path
    try:
        base_vhd = get_base_image_path(args.base)
    except ValueError as e:
        print(f"✗ {e}")
        sys.exit(1)
        
    if not base_vhd.exists():
        print(f"✗ Base image not found: {base_vhd}")
        sys.exit(1)
    
    # Create game directory
    game_dir.mkdir(parents=True)
    print(f"✓ Created game directory: {game_dir}")
    print(f"✓ Using base image: {base_vhd.name}")
    
    # Handle CD image
    cd_image = None
    if args.cd:
        cd_src = Path(args.cd).resolve()
        if not cd_src.exists():
            print(f"✗ CD image not found: {cd_src}")
            sys.exit(1)
        
        # Create config (this copies the CD)
        config = create_game_config(game_dir, args.game_name, args.base, cd_src)
        cd_image = game_dir / config["cd_image"]
    else:
        create_game_config(game_dir, args.game_name, args.base)
    
    # Launch install mode
    if not args.skip_install:
        launch_install_mode(game_dir, base_vhd, cd_image)
    else:
        # Still create the VHD and config
        game_vhd = game_dir / "game.vhd"
        create_differencing_vhd(base_vhd, game_vhd)
        generate_game_conf(game_dir, args.game_name, game_vhd, cd_image)
    
    print(f"\n✓ Game layer '{args.game_name}' is ready!")
    print(f"  Play with: python toolkit/play_game.py {args.game_name}")


if __name__ == "__main__":
    main()
