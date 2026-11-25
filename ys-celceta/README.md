# Ys: Memories of Celceta tools

Scripts for taking apart and rebuilding the data of the PC release of Ys:
Memories of Celceta: event scripts, text tables, textures and archives. They
were written to support a translation of that release.

## What is inside

**Event scripts**

| File | What it does |
|---|---|
| `script_unpack.py` | Splits a `YS7_SCP` script container into one `.bin` per function. |
| `script_disasm.py` | Disassembles a function into a tab-separated listing, with labels for branch targets. |
| `script_asm.py` | Assembles a listing back into a function and fixes up the branch offsets. |
| `script_pack.py` | Rebuilds the container from a folder of functions. |
| `opcodes.py` | The instruction set: a table of 457 opcodes and operand types, with their encoders and decoders. |
| `dpostproc.py`, `flags.py` | Replace numeric flag and work-variable ids with their names in a listing. |
| `test_dec.py` | Round-trip check: disassembles and reassembles every function in a folder and stops at the first one that does not come back byte-identical. |
| `dis_all_scripts.py`, `script_batch_asm.py`, `repack_all_script.py` | Run the steps above over a whole folder. |

**Text tables**

| File | What it does |
|---|---|
| `tbb.py` | Extracts a `.tbb` string table to text, decompressing it if needed. |
| `item_compiler.py`, `status_compiler.py`, `menudef_compiler.py` | Build `item.tbb`, `status.tbb` and the menu definition table from edited text. |
| `item_to_tsv.py`, `status_to_tsv.py` | Turn the one-field-per-line text into rows for a spreadsheet. |
| `text_inserter.py` | Applies a translation sheet (file, line number, new text) to the extracted text files, checking each replacement line before it writes. |

**Textures and archives**

| File | What it does |
|---|---|
| `flz.py`, `flzss.py` | Falcom's chunked LZSS decompression. |
| `itp_extract.py`, `itp_extract_all.py` | Convert paletted `.itp` textures to PNG. |
| `texi_cvrt.py` | Pulls the `.itp` out of a `TEXI` wrapper. |
| `it3dump.py` | Splits an `.it3` model file into its tagged chunks. |
| `evb_extract.py` | Decompresses an event box file. |
| `datfile.py` | Extracts a `.dat` archive (16-byte names, offset and size). |
| `arbdiff.py` | Lists the `.arb` map files that differ between two folders, ignoring the header. |

## Workflow

For scripts:

```sh
python script_unpack.py map.bin          # -> map/<function>.bin
python script_disasm.py map/func.bin     # -> map/func.csv
# edit the listing
python script_asm.py map/func.csv        # -> map/func.bin
python script_pack.py map                # -> map.bin
```

A listing is one instruction per line: the name, then its operands, separated
by tabs. Branches end in `GOTO_<n>` and their targets appear as `LABEL_<n>`
lines, so code can be inserted without recalculating offsets by hand.

Before trusting an edit, run `python test_dec.py <folder>` on untouched
functions. Anything the tables do not describe exactly shows up there as a
mismatch.

## String table layout

A plain `.tbb` table is a 12-byte header, the strings, then an offset table:

```text
0x00  uint32  table id
0x04  uint32  size of the offset table, divided by 16 (by 128 for item.tbb)
0x08  uint32  size of the string data
0x0C  ...     null-terminated strings
...   uint32  one offset per string, padded to a 16-byte boundary
```

Larger tables are stored compressed and `tbb.py` runs them through `flz.py`
first.

## Requirements

Python 2.7. `Pillow` for the texture converter.

## Status and limits

- These are Python 2 scripts and are here as written. They were not run when
  this repository was tidied in November 2026: there was no Python 2 and no
  copy of the game to test against.
- Several scripts have input file names or folder names fixed at the top
  (`item.tsv`, `script/`, `gfx/`). Read a script before running it.
- Some entries in `opcodes.py` are marked as guesses in their comments.
- `itp_extract.py` handles two 32-bit paletted `.itp` variants. The others
  were converted with a separate tool that is not included.
- The script container is tagged `YS7_SCP`, so the format is evidently
  shared with Ys Seven. Nothing here was tested on any other game.

## Credits

`flzss.py` is a Python reimplementation of `x2_data_uncomp` by EsperKnight.

No game files or translated text are included.
