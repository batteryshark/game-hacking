"""
DOSBox-X Game Layer Toolkit - Configuration
"""
import os
import sys
import json
from pathlib import Path

# Base directory (where this toolkit lives)
TOOLKIT_DIR = Path(__file__).parent.resolve()
ROOT_DIR = TOOLKIT_DIR.parent

# Directory structure
BASE_IMAGES_DIR = ROOT_DIR / "base_images"
GAMES_DIR = ROOT_DIR / "games"
SAVES_DIR = ROOT_DIR / "saves"
TEMPLATES_DIR = TOOLKIT_DIR / "templates"

# User config file for overrides
USER_CONFIG_FILE = ROOT_DIR / "config.json"


def _get_platform_dosbox_paths() -> list:
    """Get platform-specific default DOSBox-X paths to search."""
    if sys.platform == 'darwin':  # macOS
        return [
            Path("/Applications/dosbox-x.app/Contents/MacOS/dosbox-x"),
            Path.home() / "Applications/dosbox-x.app/Contents/MacOS/dosbox-x",
            ROOT_DIR / "dosbox-x.app/Contents/MacOS/dosbox-x",
        ]
    elif sys.platform == 'win32':  # Windows
        return [
            Path(os.environ.get('PROGRAMFILES', 'C:/Program Files')) / "DOSBox-X" / "dosbox-x.exe",
            Path(os.environ.get('PROGRAMFILES(X86)', 'C:/Program Files (x86)')) / "DOSBox-X" / "dosbox-x.exe",
            Path(os.environ.get('LOCALAPPDATA', '')) / "DOSBox-X" / "dosbox-x.exe",
            Path("C:/DOSBox-X/dosbox-x.exe"),
            ROOT_DIR / "dosbox-x.exe",
        ]
    else:  # Linux and others
        return [
            Path("/usr/bin/dosbox-x"),
            Path("/usr/local/bin/dosbox-x"),
            Path.home() / ".local/bin/dosbox-x",
            ROOT_DIR / "dosbox-x",
        ]


def _find_dosbox() -> Path:
    """Find DOSBox-X executable, checking user config first, then platform defaults."""
    # Check environment variable first
    env_path = os.environ.get('DOSBOX_X_PATH')
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p
    
    # Check user config file
    if USER_CONFIG_FILE.exists():
        try:
            with open(USER_CONFIG_FILE) as f:
                user_config = json.load(f)
            if 'dosbox_path' in user_config:
                p = Path(user_config['dosbox_path'])
                if p.exists():
                    return p
        except (json.JSONDecodeError, IOError):
            pass
    
    # Search platform-specific default locations
    for path in _get_platform_dosbox_paths():
        if path.exists():
            return path
    
    # Return first default path (will fail later with helpful error)
    return _get_platform_dosbox_paths()[0]


DOSBOX_APP = _find_dosbox()


def verify_dosbox() -> bool:
    """Check if DOSBox-X is available. Raises RuntimeError with helpful message if not."""
    if DOSBOX_APP.exists():
        return True
    
    paths_checked = _get_platform_dosbox_paths()
    paths_str = '\n  '.join(str(p) for p in paths_checked)
    
    raise RuntimeError(
        f"DOSBox-X not found!\n\n"
        f"Searched:\n  {paths_str}\n\n"
        f"Options to fix:\n"
        f"  1. Set DOSBOX_X_PATH environment variable\n"
        f"  2. Create {USER_CONFIG_FILE} with: {{\"dosbox_path\": \"/path/to/dosbox-x\"}}\n"
        f"  3. Install DOSBox-X to a standard location"
    )


def load_base_images() -> dict:
    """Load base images configuration from JSON file."""
    config_path = BASE_IMAGES_DIR / "base_images.json"
    if not config_path.exists():
        return {}
    with open(config_path) as f:
        return json.load(f)


def get_base_image_keys() -> list:
    """Get list of available base image keys."""
    return list(load_base_images().keys())


def get_base_image_path(key: str) -> Path:
    """Get full path to a base image by key."""
    images = load_base_images()
    if key not in images:
        available = list(images.keys())
        raise ValueError(f"Unknown base image: {key}. Available: {available}")
    return BASE_IMAGES_DIR / images[key]["file"]


def get_base_image_info(key: str) -> dict:
    """Get info about a base image."""
    images = load_base_images()
    if key not in images:
        return None
    return images[key]


def get_game_dir(game_name: str) -> Path:
    """Get the directory for a game."""
    return GAMES_DIR / game_name


def get_save_dir(game_name: str) -> Path:
    """Get the saves directory for a game."""
    return SAVES_DIR / game_name


def ensure_dirs():
    """Ensure all required directories exist."""
    BASE_IMAGES_DIR.mkdir(exist_ok=True)
    GAMES_DIR.mkdir(exist_ok=True)
    SAVES_DIR.mkdir(exist_ok=True)


def load_config_template() -> str:
    """Load the DOSBox-X config template."""
    template_path = TEMPLATES_DIR / "game.conf.template"
    if template_path.exists():
        return template_path.read_text()
    # Fallback minimal template
    return """[sdl]
fullscreen = false
autolock = true

[dosbox]
title = {title}
memsize = 64

[cpu]
cputype = pentium_mmx
cycles = max

[autoexec]
{autoexec}
"""
