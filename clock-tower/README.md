# Clock Tower script tools

Tools for the script of the Japanese Windows release of Clock Tower (Human
Entertainment): a disassembler for the scene bytecode, a text dumper and a
text injector that keeps the scene table valid after strings change length.

## Why this exists

The Windows version has better audio and an FMV intro, but it was only ever
released in Japanese. All dialogue and scene logic lives in two files,
`SCE/CT.ADO` and `SCE/CT.ADT`, in a custom bytecode. These tools are what came
out of working that format out far enough to replace the text. The full story
is in the write-up:
[Hacking Clocktower - The First Fear](https://batteryshark.github.io/2014/08/07/hacking-clocktower-the-first-fear.html).

## What is inside

| File | What it does |
|---|---|
| `adodis.py` | Disassembles `CT.ADO` into one line per instruction, split into scenes. Knows 132 opcodes, 104 of them by name. |
| `cttd.py` | Dumps every `MSGOUT` string to a tab-separated text file: offset, original byte length, text. |
| `ctti.py` | Reads the edited dump, writes a new `CT.ADO` with the new strings and a new `CT.ADT` with every scene offset shifted to match. |
| `notes.txt` | Working notes on the format from the time. |

## The format, briefly

- `CT.ADO` starts with a 256-byte header. After that it is a stream of
  instructions. Each one is a 16-bit little-endian opcode in the `0xFFxx`
  range followed by its operands.
- A scene starts with opcode `0xFF00`. `CT.ADT` is a table of 32-bit offsets,
  one per scene, pointing at those starts.
- ADT offsets are not plain file offsets. Every `0x8000` bytes of ADO data
  takes `0x10000` of ADT address space, so the upper half of each entry has to
  be halved to get the real position. Get that wrong by one byte and scenes
  stop resolving.
- Text is opcode `0xFF33` (`MSGOUT`): two 16-bit values, then a Shift-JIS
  string. The game stores a `0x00` after every single-byte character, and a
  line break is `0x0A 0x00`.
- The executable accepts a `NOREG` option that skips the registry lookup for
  the data directory and uses the game folder, which makes testing a patched
  copy easier.

## Use

Python 3, standard library only. Copy `CT.ADO` and `CT.ADT` out of the game's
`SCE` folder and keep the originals.

```sh
python3 adodis.py CT.ADO CT.ADT > script.txt     # disassemble
python3 cttd.py CT.ADO ct_txt.txt                # dump the text
# edit the third column of ct_txt.txt and save it as ct_txt_proc.txt
python3 ctti.py CT.ADO CT.ADT ct_txt_proc.txt new_CT.ADO new_CT.ADT
```

Then put the two new files back in `SCE` under their original names. Without
arguments the scripts use the file names from the original workflow
(`CT_J.ADO` and `CT_J.ADT` in, `CT.ADO` and `CT.ADT` out).

The dump is Shift-JIS, so open it in an editor that can read and save that
encoding. Leave the first two columns alone: the injector uses them to find
each string and to work out how far everything after it moves. `[NEWLINE]`
marks a line break.

## What you should see

`adodis.py` prints a listing like this:

```text
#----SCENE 0 (Offset 0x100)
RETN
JMP 23
ALLEND 19
#----SCENE 1 (Offset 0x10a)
RETN
JMP 8
```

`cttd.py` writes one line per string, 510 of them for the full script.

## Status and limits

- Checked in November 2026 on Python 3.9 against one copy of the script
  files. Dumping the text and injecting it back unchanged reproduces both
  files byte for byte. Lengthening one string moves every later scene offset
  by the right amount, and all 1,200 table entries still point at a scene
  start.
- Not re-tested in the game itself since the original work.
- Written for Python 2 in 2014 and ported to Python 3 for this repository.
- 28 opcodes are still unnamed, and several operand layouts are guesses. The
  disassembler skips ahead one byte when it meets something it cannot parse,
  so a listing can lose sync for a few instructions.
- The dumper finds strings by scanning for the `MSGOUT` opcode bytes. That
  worked for this script, but it is a scan, not a parse.
- There is no line-length check. Text that is too long for the message box
  will run off it.

No game files or translated script are included.
