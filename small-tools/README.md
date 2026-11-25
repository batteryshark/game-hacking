# Small tools

Three single-file utilities, each for one game.

## `boshy_save_crypt.py` — I Wanna Be the Boshy

Decrypts and re-encrypts the game's save and options files. The game is built
on Multimedia Fusion 2 and stores its data through the INI++ extension, which
"encrypts" with plain RC4 and a short password. The write-up has the details:
[Hacking 'I Wanna be the Boshy' Game Saves](https://batteryshark.github.io/2014/10/03/hacking-i-wanna-be-the-boshy-game-saves.html).

```sh
python3 boshy_save_crypt.py save.ini    # -> save.ini.converted
```

RC4 is symmetric, so the same command turns an encrypted file into a readable
INI and an edited INI back into what the game expects. Checked in November
2026 against a published RC4 test vector and by converting a file there and
back. Not re-tested with the game.

## `darkstone_mtfextract.py` — Darkstone

Unpacks a Darkstone `.MTF` archive into the current folder. The format is a
file count, then for each file a length-prefixed name, an offset and a size.

```sh
python3 darkstone_mtfextract.py DATA.MTF
```

Checked in November 2026 with an archive built to that layout, not with game
data. Entries are copied out exactly as stored. If the game compresses some of
them, this does not undo it.

## `pz_saver.py` — Project Zomboid

Quick save and quick load by copying the save folder. Run it, pick a save
slot, and leave it running next to the game:

| Key | Action |
|---|---|
| F5 | Copy the save folder to `<slot>_BACKUP` |
| F7 | Replace the save folder with the backup |
| F12 | Quit |

```sh
python pz_saver.py
```

Windows only: it polls the keyboard through `User32.dll` and looks for saves
under `%USERPROFILE%\Zomboid\Saves`. It only knows the `Apocalypse` and
`Survivor` save folders. It copies the folder while the game is running and
nothing coordinates that with the game. Not run when this repository was
tidied, since that was done on a Mac.
