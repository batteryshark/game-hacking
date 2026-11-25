# game-hacking

Console and PC game hacking: file-format tools, script disassemblers, a
translation patch workflow and an emulator patch. Most of it was written
between 2013 and 2017 while taking a specific game apart, and each folder is a
separate small project.

No game files are in this repository. Every tool here works on files from a
copy of the game that you supply.

## Entries

| Entry | Target | What it does | Technique | Status |
|---|---|---|---|---|
| [`chdssf`](chdssf/) | SSF (Sega Saturn emulator, Windows) | Lets SSF boot a CHD disc image without a virtual drive | DLL injection, import-table hooks, a small emulated SCSI drive | Builds with 32-bit MinGW. Needs a `libchd.dll` that is not included. |
| [`clock-tower`](clock-tower/) | Clock Tower, Japanese Windows release | Disassembles the game script, dumps the text and writes it back with every scene offset corrected | Bytecode reverse engineering, text injection | Works. Python 3, round-trip tested. |
| [`ys-celceta`](ys-celceta/) | Ys: Memories of Celceta, PC | Script unpacker, disassembler and assembler, text-table compilers, texture and archive extractors | Bytecode reverse engineering, LZSS decompression | Python 2.7 as written. Not run since. |
| [`culdcept`](culdcept/) | Culdcept, Dreamcast and PS2 | Unpacks the data archives, decodes hidden cards, dumps cards, sprites and maps | Container carving, a hand-broken delta cipher, pixel-format conversion | Three scripts tested on Python 3. The rest is Python 2.7 and needs an LH5 decompressor that is not included. |
| [`castlevania`](castlevania/) | Castlevania: Lords of Shadow 1/2 and Mirror of Fate, PC | Extracts `.packed` archives; extracts and rebuilds `.pack` archives | Archive format reverse engineering | Works on Python 3 against archives built to the documented layout. Not re-run on game files. |
| [`dosbox-loader`](dosbox-loader/) | DOS and Windows 98 games under DOSBox-X | Keeps a clean OS image, one layer per installed game and a throwaway layer for saves | Differencing VHD images | Python 3. Needs DOSBox-X and your own base images. |
| [`keep-clicking-and-nobody-explodes`](keep-clicking-and-nobody-explodes/) | Keep Talking and Nobody Explodes | Browser page for the expert: tracks the bomb's details and solves the standard modules | Plain HTML and JavaScript | Works. Open `index.html`. |
| [`small-tools`](small-tools/) | Darkstone, I Wanna Be the Boshy, Project Zomboid | An archive extractor, a save-file decryptor and a quick-save helper | One file each | Two tested on Python 3. The third is Windows-only and untested here. |

Each folder has its own README with usage, what you should see and the limits.

## Write-ups

Three of these have a longer write-up on my blog:

- [Hacking Clocktower - The First Fear](https://batteryshark.github.io/2014/08/07/hacking-clocktower-the-first-fear.html)
- [Culdcept Series](https://batteryshark.github.io/2013/11/12/culdcept-series.html)
- [Hacking 'I Wanna be the Boshy' Game Saves](https://batteryshark.github.io/2014/10/03/hacking-i-wanna-be-the-boshy-game-saves.html)

## Requirements

- Python 3 for the tested tools. `castlevania/BFPKTool.py` also needs
  `pycryptodome` for encrypted archives.
- Python 2.7 for `ys-celceta` and most of `culdcept`. They also want `Pillow`
  for anything that writes an image.
- A 32-bit MinGW toolchain and CMake for `chdssf`.

## License

MIT — see [LICENSE](LICENSE). `dosbox-loader` carries its own copy. The
bundled jQuery, jQuery UI and D3 files in `keep-clicking-and-nobody-explodes`
remain under their own licences.
