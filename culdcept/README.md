# Culdcept data tools

Scripts and format notes from reverse engineering the data files of Culdcept
on the Dreamcast and PlayStation 2: the nested archives, the card records, the
sprites and the board maps.

## Why this exists

The game keeps its cards, sprites and maps in one large file with no names,
no directory and headerless compressed streams. Getting anything out meant
working out the container, then the compression, then each record type. The
write-up covers the container and the compression:
[Culdcept Series](https://batteryshark.github.io/2013/11/12/culdcept-series.html).

## What is inside

| File | What it does | State |
|---|---|---|
| `culdroot.py` | Splits a container whose table is (offset, size) pairs. Pass `b` as a second argument for big-endian tables. | Python 3, tested |
| `culddat.py` | Splits a container whose table is offsets only. | Python 3, tested |
| `card_decrypt.py` | Decodes the hidden cards. The comment at the top walks through how the cipher was worked out. | Python 3, tested |
| `card_parser.py` | Reads a card record and writes its stats as JSON, the card art and the sprite as PNG. | Python 2.7, not run |
| `sprcvrt.py` | Converts a sprite (16-colour or 256-colour palette, ARGB1555) to PNG. | Python 2.7, not run |
| `mapdump.py` | Decompresses a board map's 64x64 tiles and composites them into one PNG. | Python 2.7, not run |
| `card-format-notes.txt` | Field-by-field layout of a card record. | |
| `animation-format-notes.txt` | Partial notes on the sprite animation files. | |

## What was found

- **Containers nest.** The top-level file is a table of offsets and sizes
  followed by data, and many of the entries are containers again.
- **Compression is LH5 without the header.** Compressed entries start with
  `0x08` and go straight into the Huffman stream, so a normal LHA tool will
  not touch them until a header is put back.
- **Some cards are scrambled on top of that.** They are flagged with `0x09`
  instead of `0x08`. After decompression every 16-bit word is stored as the
  difference from the one before it, so adding each word to its predecessor
  recovers the record. The known stats of one hidden card were enough to spot
  the pattern.
- **Images are raw ARGB1555.** Card art is 256x320. Board maps are grids of
  separately compressed 64x64 tiles behind a table of offsets, with one extra
  padding column the game does not draw.

## Use

The three tested scripts need only Python 3:

```sh
python3 culdroot.py DATA.BIN          # -> DATA.part1.bin, DATA.part2.bin, ...
python3 culddat.py DATA.part7.bin     # -> DATA.part7.part00001.bin, ...
python3 card_decrypt.py card.bin      # -> card.dec
```

The other three are Python 2.7 and need `Pillow`. `card_parser.py` and
`mapdump.py` also call an external LH5 decompressor named `delha`, which reads
`in.tmp` and writes `out.tmp`. That program is not in this repository, so those
two scripts document the formats more than they run out of the box.

## Status and limits

- `culdroot.py`, `culddat.py` and `card_decrypt.py` were checked in November
  2026 on Python 3.9 with files built to the layouts above, not with game
  data.
- `card_parser.py`, `sprcvrt.py` and `mapdump.py` are as originally written and
  were not run: no Python 2, no `Pillow` and no `delha` on the machine used.
- Many card fields are still unknown. They are labelled `unk_` in the parser
  and `???` in the notes.
- The tools were written against the Dreamcast and PS2 releases. Nothing here
  handles the DS or later games.

No game files, card art or maps are included.
