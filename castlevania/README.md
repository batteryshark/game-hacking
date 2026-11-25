# Castlevania archive tools

Two small tools for the archive formats MercurySteam used in the PC releases
of Castlevania: Lords of Shadow, Lords of Shadow 2 and Mirror of Fate.

## What is inside

| File | Game | What it does |
|---|---|---|
| `BFPKTool.py` | Lords of Shadow 1 and 2 | Extracts `.packed` (BFPK) archives. |
| `packtool.py` | Mirror of Fate | Extracts `.pack` archives and builds them from a folder. |

## BFPK

A BFPK file starts with the magic `BFPK`, a version byte and a variant byte.
The file table follows: for each file a length-prefixed path, its size, its
offset and, in unencrypted tables, a deleted flag. The tool handles these
storage types:

| Version | Storage |
|---|---|
| 0 | Raw |
| 1 | Each file is one zlib stream |
| 2 | Each file is a run of zlib chunks |
| 3 | zlib, with the file table AES-256-CBC encrypted |
| 2, variant 0 | Raw, with the file table encrypted |

```sh
python3 BFPKTool.py d data.packed     # -> data/...
```

Files are written to a folder named after the archive. Entries flagged as
deleted are listed but skipped.

The key for encrypted tables is not in this repository. Supply it as 64 hex
digits in the `BFPK_V3_KEY` environment variable. Encrypted archives also need
`pycryptodome`.

## .pack

A `.pack` file is three 32-bit values (table size plus 8, data size, file
count), then one 1032-byte entry per file (a 1024-byte path, start offset, end
offset), then the data.

```sh
python3 packtool.py d data.pack       # -> data/...
python3 packtool.py c data            # -> data.pack in the current folder
```

## Status and limits

- Both were written in 2014 for Python 2 and ported to Python 3 for this
  repository.
- Checked in November 2026 on Python 3.9 with archives built by a test script
  to the layouts above: all five BFPK storage types extract correctly (the
  encrypted ones with a random test key), and a folder packed with
  `packtool.py` extracts back identical. Neither tool was re-run on real game
  archives.
- `BFPKTool.py` cannot create archives. That half was never written.
- `packtool.py` does not add any alignment padding when it builds a pack. The
  original note says the game might want some. A rebuilt pack was not tested
  in the game here.

No game files are included.
