# CHDSSF

A Win32 patch that lets the SSF Sega Saturn emulator boot a CHD disc image
directly.

## Why this exists

When this was written, SSF read games from an optical drive. To run a disc
image you mounted it in a virtual drive first, and it could not read CHD, the
compressed format most Saturn sets are stored in. CHDSSF sits between SSF and
Windows and answers SSF's drive commands from the CHD file, so nothing has to
be mounted or converted.

## How it works

- `SSFLoader.exe` starts `SSF.exe` suspended, writes a short `LoadLibraryA`
  stub into it and points the main thread at the stub, which loads
  `ssf_patch.dll`.
- `ssf_patch.dll` replaces four of SSF's `KERNEL32.dll` imports: `CreateFileA`,
  `DeviceIoControl`, `GetDriveTypeA` and `CloseHandle`.
- When SSF opens a device path it gets a fake handle. SCSI pass-through
  requests on that handle are answered by a small emulated drive that reports
  itself as `CHDDriveVirtual`.
- The emulated drive handles the six commands SSF sends: TEST UNIT READY,
  REQUEST SENSE, INQUIRY, READ TOC, PREVENT/ALLOW MEDIUM REMOVAL and READ CD.
  Table-of-contents and sector data come from the CHD through `libchd.dll`.

[ARCHITECTURE.md](ARCHITECTURE.md) has the full flow and the assumptions that
matter if you change it.

## Layout

```text
src/loader/      SSFLoader.exe: starts SSF and injects the patch
src/ssf_patch/   ssf_patch.dll: import hooks and the emulated SCSI drive
ARCHITECTURE.md  runtime flow, assumptions and risks
```

## Build

The target is 32-bit Windows. With MSYS2 MinGW32 on Windows:

```powershell
cmake -S . -B build -G "MinGW Makefiles"
cmake --build build
```

Cross-compiling from macOS or Linux with mingw-w64 also works:

```sh
cmake -S . -B build -G Ninja -DCMAKE_SYSTEM_NAME=Windows \
      -DCMAKE_C_COMPILER=i686-w64-mingw32-gcc
cmake --build build
```

Output: `build/SSFLoader.exe` and `build/src/ssf_patch/ssf_patch.dll`, both
PE32.

## Run

1. Put `SSFLoader.exe`, `ssf_patch.dll` and `libchd.dll` next to `SSF.exe`.
2. Start it with a disc image:

   ```powershell
   .\SSFLoader.exe .\game.chd
   ```

3. In SSF the drive shows up as `CHDDriveVirtual`. If SSF starts without the
   disc, select that drive and choose `CD Close` from the Hardware menu.

The patch logs each command with `OutputDebugString`, so DebugView shows what
SSF asked for if a disc does not read.

## Status and limits

- Written in 2017 against the SSF build current then. It has not been tried
  on later builds.
- 32-bit only. The loader edits the thread's `Eip` and the stub assumes 4-byte
  addresses.
- `libchd.dll` is not in this repository. The patch expects a DLL exporting
  `libchd_cdrom_open`, `libchd_cdrom_get_toc` and `libchd_cdrom_read_data`,
  returning the track structures MAME's CHD CD-ROM code uses. Without that DLL
  the patch cannot read a disc.
- Audio sectors are byte-swapped on read, because the CHD sets it was tested
  with stored audio in the other byte order.
- Only the commands SSF was seen to send are implemented.
- The current source builds cleanly with mingw-w64 (checked November 2026).
  It has not been run against SSF since the original work.
- Injection and import patching look like malware to some security software.

## Credits

- SSF is by Shima. It is not included.
- The track and table-of-contents structures in `src/ssf_patch/chd_helper.h`
  follow MAME's `cdrom.h`.
