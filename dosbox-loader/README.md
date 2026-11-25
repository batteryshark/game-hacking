# DOSBox-X Game Layer Toolkit

Manage retro games using layered VHD images. Keep your Windows 98/DOS base installs pristine while easily resetting game saves.

## How It Works

```
base_images/win98se_base.vhd     ← Clean base OS (read-only)
        ↓ (differencing VHD)
games/mygame/game.vhd            ← Game installed here
        ↓ (differencing VHD)  
saves/mygame/session.vhd         ← Your saves (deletable)
```

Changes only go to the bottom layer. Delete `session.vhd` to reset saves.

## Requirements

- Python 3.6+
- [DOSBox-X](https://dosbox-x.com/)

## Installation

1. Clone this repository and work from the `dosbox-loader` folder
2. Install DOSBox-X
3. Configure DOSBox-X path (see below)
4. Add your base VHD images to `base_images/`

## DOSBox-X Configuration

The toolkit searches for DOSBox-X in platform-specific locations:

**macOS:**
- `/Applications/dosbox-x.app`
- `~/Applications/dosbox-x.app`

**Windows:**
- `C:\Program Files\DOSBox-X\dosbox-x.exe`
- `C:\Program Files (x86)\DOSBox-X\dosbox-x.exe`
- `%LOCALAPPDATA%\DOSBox-X\dosbox-x.exe`
- `C:\DOSBox-X\dosbox-x.exe`

**Linux:**
- `/usr/bin/dosbox-x`
- `/usr/local/bin/dosbox-x`
- `~/.local/bin/dosbox-x`

### Custom Path

If DOSBox-X is installed elsewhere, you have two options:

**Option 1: Environment variable**
```bash
export DOSBOX_X_PATH="/path/to/dosbox-x"
```

**Option 2: Config file**

Create `config.json` in the project root:
```json
{
    "dosbox_path": "/path/to/dosbox-x"
}
```

## Quick Start

```bash
# List available base images
python3 toolkit/create_game_layer.py --list-bases

# Create a new game layer
python3 toolkit/create_game_layer.py mygame --base win98se_en

# Create with CD image
python3 toolkit/create_game_layer.py mygame --base win98se_jp --cd /path/to/game.cue

# Play a game
python3 toolkit/play_game.py mygame

# Reset saves (fresh start)
python3 toolkit/play_game.py mygame --fresh

# List installed games
python3 toolkit/play_game.py --list
```

## Directory Structure

```
├── base_images/           
│   ├── base_images.json         # Register base images here
│   ├── base_images.example.json # Example config
│   └── *.vhd                    # Your base OS VHDs
├── games/<name>/     
│   ├── game.vhd              # Game layer (diff from base)
│   ├── game.json             # Game metadata
│   ├── dosbox.conf           # DOSBox config
│   └── cd/                   # CD images for this game
├── saves/<name>/     
│   ├── session.vhd           # Save layer (diff from game)
│   └── play.conf             # Runtime config
├── toolkit/               
│   ├── templates/game.conf.template
│   └── *.py
└── config.json               # Optional: custom DOSBox-X path
```

## Drive Layout in Windows

| Drive | Contents |
|-------|----------|
| C: | Windows + installed game |
| D: | Game folder on host (file transfer) |
| E: | CD-ROM (if configured) |

## Adding Base Images

1. Place your VHD in `base_images/`
2. Copy `base_images.example.json` to `base_images.json`
3. Edit to match your VHD files:

```json
{
    "win98se_en": {
        "file": "win98se_en_base.vhd",
        "name": "Windows 98 SE English",
        "description": "English Windows 98 Second Edition"
    },
    "dos622": {
        "file": "dos622_base.vhd",
        "name": "MS-DOS 6.22",
        "description": "Plain DOS for older games"
    }
}
```

## Customizing DOSBox Settings

- **Global template**: `toolkit/templates/game.conf.template`
- **Per-game config**: `games/<name>/dosbox.conf`

## Status and limits

- The layers are made by DOSBox-X itself: the toolkit starts it with a short
  config that runs `VHDMAKE -link`, so it needs a DOSBox-X build that has that
  command.
- Base images are not included. You supply your own installed DOS or
  Windows 98 VHD.
- A game layer depends on its base image and a save layer on its game layer.
  Change or move a parent and the layers above it stop working.
- Checked in November 2026 on Python 3.9 without DOSBox-X installed: the
  commands start, list base images and games, and report a missing DOSBox-X
  with the paths they searched. Creating a layer and booting it were not
  re-run.

## Credits

The DOSBox-X settings in `toolkit/templates/game.conf.template` are based on
eXo's Windows 98 configuration.

## License

MIT
