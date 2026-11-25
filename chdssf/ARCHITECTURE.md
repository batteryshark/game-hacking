# Architecture

## System Map

```mermaid
flowchart LR
    User["User runs SSFLoader.exe game.chd"]
    Loader["src/loader\ncreates SSF.exe suspended"]
    Inject["remote LoadLibraryA(\"ssf_patch.dll\") shellcode"]
    Patch["src/ssf_patch\nDllMain installs hooks"]
    Win32["SSF Win32 API calls\nCreateFileA / DeviceIoControl / GetDriveTypeA"]
    SPTD["virtual SPTD/SCSI responder"]
    Libchd["libchd.dll"]
    CHD["Saturn CHD image"]

    User --> Loader --> Inject --> Patch
    Patch --> Win32 --> SPTD --> Libchd --> CHD
```

## Components

`src/loader/main.c` is the process launcher. It resolves `SSF.exe` and
`ssf_patch.dll` relative to the current directory, starts SSF suspended, writes
the DLL path and a small `LoadLibraryA` shellcode stub into the SSF process, and
then resumes the SSF main thread.

`src/ssf_patch/main.c` is the injected DLL entrypoint. On process attach it
initializes CHD/SPTD state and installs filesystem/device hooks.

`src/ssf_patch/global.c` contains memory patch and import-address-table hook
helpers. The active hooks replace SSF's imported `KERNEL32.dll` functions by
name.

`src/ssf_patch/fs.c` is the Win32 API shim. It detects attempts to open optical
device paths, returns a sentinel handle, and routes SCSI pass-through
`DeviceIoControl` calls into the virtual SPTD layer.

`src/ssf_patch/sptd.c` translates the subset of SCSI commands SSF needs into
TOC and sector reads from `libchd.dll`.

`src/ssf_patch/chd_helper.h` is a local copy of the CHD/CD-ROM structures needed
to interpret `libchd.dll` results.

## Runtime Flow

1. The user runs `SSFLoader.exe path\to\disc.chd`.
2. The loader starts `SSF.exe` in a suspended state.
3. The loader writes the absolute path to `ssf_patch.dll` into SSF memory.
4. The loader writes shellcode that calls `LoadLibraryA` with that DLL path.
5. The loader changes the suspended thread's `Eip` to the shellcode and resumes
   the thread.
6. `ssf_patch.dll` loads inside SSF, reads the CHD path from SSF's command line,
   and opens it through `libchd.dll`.
7. The patch replaces selected SSF imports from `KERNEL32.dll`.
8. When SSF opens or queries an optical drive, the patch returns a virtual
   handle and answers SCSI pass-through commands from CHD data.

## Load-Bearing Weirdness

- The command line passed to `SSF.exe` still names `SSFLoader.exe`. This lets
  the injected DLL read the CHD path as `argv[1]` inside SSF.
- The loader waits before freeing remote memory because the injected shellcode
  runs after the target thread resumes. The wait is crude, but removing it
  breaks the injection.
- `CHDDriveVirtual` is the virtual INQUIRY vendor/device string SSF sees.
- Audio sectors may be byte-swapped on read. The original note says Archive.org
  Saturn CHD audio was endian-reversed for the tested images.
- The SCSI command set is intentionally tiny: only the commands SSF appeared to
  need were implemented.

## External Dependencies

- `SSF.exe`: not included.
- `libchd.dll`: not included, and its source is not in this repository.
- Windows `KERNEL32.dll` and `SHELL32.dll`.

## Known Risks

- Runtime behavior is tied to 32-bit Windows process internals.
- The project has no automated tests. Meaningful validation requires SSF and a
  known-good Saturn CHD.
- The `libchd.dll` ABI was recovered from usage and export names, not headers.
- The patch assumes SSF imports the hooked APIs by name from `KERNEL32.dll`.
- Direct IAT patching and remote-thread context editing can be blocked by
  security software.
