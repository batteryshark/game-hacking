"""
DOSBox-X Game Layer Toolkit - VHD Utilities
"""
import subprocess
import tempfile
import os
from pathlib import Path
from .config import DOSBOX_APP

def create_differencing_vhd(parent_path: Path, child_path: Path) -> bool:
    """
    Create a differencing VHD using DOSBox-X's VHDMAKE command.
    
    This works by launching DOSBox-X with a minimal autoexec that runs VHDMAKE
    and then exits.
    """
    parent_path = Path(parent_path).resolve()
    child_path = Path(child_path).resolve()
    
    if not parent_path.exists():
        raise FileNotFoundError(f"Parent VHD not found: {parent_path}")
    
    if child_path.exists():
        raise FileExistsError(f"Child VHD already exists: {child_path}")
    
    # Ensure parent directory exists
    child_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create a temporary config file for DOSBox-X
    conf_content = f"""[sdl]
fullscreen = false
autolock = false

[dosbox]
fastbioslogo = true
startbanner = false

[autoexec]
VHDMAKE -link "{parent_path}" "{child_path}"
EXIT
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        f.write(conf_content)
        temp_conf = f.name
    
    try:
        # Run DOSBox-X with the temporary config
        result = subprocess.run(
            [str(DOSBOX_APP), "-conf", temp_conf],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Check if the child VHD was created
        if child_path.exists():
            print(f"✓ Created differencing VHD: {child_path.name}")
            return True
        else:
            print(f"✗ Failed to create VHD. DOSBox output:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    finally:
        os.unlink(temp_conf)


def generate_autoexec(
    c_drive_vhd: Path,
    d_drive_folder: Path = None,
    cd_image: Path = None,
    boot: bool = True
) -> str:
    """
    Generate the [autoexec] section for a DOSBox-X config.
    """
    lines = []
    
    # Mount C: drive VHD
    lines.append(f'IMGMOUNT c "{c_drive_vhd}"')
    
    # Mount D: folder if specified
    if d_drive_folder:
        lines.append(f'MOUNT d "{d_drive_folder}" -nocachedir')
    
    # Mount CD image if specified
    if cd_image:
        lines.append(f'IMGMOUNT e "{cd_image}" -t cdrom -ide 2m')
    
    # Boot Windows
    if boot:
        lines.append('BOOT -l c')

    return '\n'.join(lines)
