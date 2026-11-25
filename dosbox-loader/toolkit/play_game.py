#!/usr/bin/env python3
"""
Play a game with an auto-created save layer.

Usage:
    python play_game.py <game_name> [--fresh]
    
Example:
    python play_game.py rpg95
    python play_game.py rpg95 --fresh   # Reset saves
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from toolkit.config import (
    get_game_dir, get_save_dir, DOSBOX_APP, GAMES_DIR, ensure_dirs, load_config_template,
    verify_dosbox
)
from toolkit.vhd_utils import create_differencing_vhd


def load_game_config(game_dir: Path) -> dict:
    """Load game.json config."""
    config_path = game_dir / "game.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Game config not found: {config_path}")
    with open(config_path) as f:
        return json.load(f)


def ensure_save_layer(game_name: str, game_dir: Path, fresh: bool = False) -> Path:
    """Ensure save layer VHD exists, creating if needed."""
    save_dir = get_save_dir(game_name)
    save_dir.mkdir(parents=True, exist_ok=True)
    
    save_vhd = save_dir / "session.vhd"
    game_vhd = game_dir / "game.vhd"
    
    if not game_vhd.exists():
        raise FileNotFoundError(f"Game VHD not found: {game_vhd}")
    
    # Delete old save if fresh requested
    if fresh and save_vhd.exists():
        print(f"Removing old save layer...")
        save_vhd.unlink()
    
    # Create save layer if doesn't exist
    if not save_vhd.exists():
        print(f"Creating save layer...")
        if not create_differencing_vhd(game_vhd, save_vhd):
            raise RuntimeError("Failed to create save layer")
    
    return save_vhd


def generate_play_conf(game_name: str, save_vhd: Path, game_dir: Path, cd_image: Path = None) -> Path:
    """Generate DOSBox-X config file for playing."""
    template = load_config_template()
    
    # Build autoexec section
    autoexec_lines = [
        f'IMGMOUNT c "{save_vhd}"',
        f'MOUNT d "{game_dir}" -nocachedir',
    ]
    if cd_image:
        autoexec_lines.append(f'IMGMOUNT e "{cd_image}" -t cdrom -ide 2m')
    autoexec_lines.append('BOOT -l c')
    
    # Fill template
    config_content = template.format(
        title=game_name,
        c_drive_vhd=str(save_vhd),
        d_drive_folder=str(game_dir),
        cd_image=str(cd_image) if cd_image else "",
        autoexec='\n'.join(autoexec_lines)
    )
    
    # Write config file to save dir
    save_dir = save_vhd.parent
    conf_path = save_dir / "play.conf"
    conf_path.write_text(config_content)
    return conf_path


def launch_game(game_name: str, save_vhd: Path, game_dir: Path, cd_image: Path = None):
    """Launch DOSBox-X to play the game."""
    
    # Generate play config
    conf_path = generate_play_conf(game_name, save_vhd, game_dir, cd_image)
    
    print(f"\n" + "="*60)
    print(f"PLAYING: {game_name}")
    print("="*60)
    print(f"Save VHD: {save_vhd}")
    print(f"D: drive: {game_dir}")
    if cd_image:
        print(f"E: drive: {cd_image}")
    print(f"Config: {conf_path}")
    print("="*60 + "\n")
    
    subprocess.run([str(DOSBOX_APP), "-conf", str(conf_path)])


def list_games():
    """List all available games."""
    if not GAMES_DIR.exists():
        print("No games found.")
        return
    
    games = [d.name for d in GAMES_DIR.iterdir() if d.is_dir() and (d / "game.json").exists()]
    
    if not games:
        print("No games found.")
        return
    
    print("Available games:")
    for game in sorted(games):
        config_path = GAMES_DIR / game / "game.json"
        try:
            with open(config_path) as f:
                config = json.load(f)
            cd_status = "📀" if config.get("cd_image") else "  "
            base_name = config.get("base_image_name", config.get("base_image_key", "?"))
            print(f"  {cd_status} {game} [{base_name}]")
        except:
            print(f"     {game} (config error)")


def main():
    parser = argparse.ArgumentParser(
        description="Play a game with an auto-created save layer"
    )
    parser.add_argument("game_name", nargs="?", help="Name of the game to play")
    parser.add_argument("--fresh", "-f", action="store_true",
                        help="Delete existing saves and start fresh")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List available games")
    
    args = parser.parse_args()
    
    if args.list or not args.game_name:
        list_games()
        return
    
    # Verify DOSBox-X is available before trying to play
    try:
        verify_dosbox()
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    ensure_dirs()
    
    # Get game directory
    game_dir = get_game_dir(args.game_name)
    if not game_dir.exists():
        print(f"✗ Game not found: {args.game_name}")
        print("  Available games:")
        list_games()
        sys.exit(1)
    
    # Load config
    try:
        config = load_game_config(game_dir)
    except FileNotFoundError as e:
        print(f"✗ {e}")
        sys.exit(1)
    
    # Ensure save layer
    try:
        save_vhd = ensure_save_layer(args.game_name, game_dir, fresh=args.fresh)
    except Exception as e:
        print(f"✗ Failed to prepare save layer: {e}")
        sys.exit(1)
    
    # Get CD image if configured
    cd_image = None
    if config.get("cd_image"):
        cd_image = game_dir / config["cd_image"]
        if not cd_image.exists():
            print(f"⚠ Warning: CD image not found: {cd_image}")
            cd_image = None
    
    # Launch!
    launch_game(args.game_name, save_vhd, game_dir, cd_image)


if __name__ == "__main__":
    main()
