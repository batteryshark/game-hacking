/*
 * Loader stub for injecting the virtual SPTD patch into SSF.
 */
#define WIN32_LEAN_AND_MEAN

#include <windows.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PATH_BUFFER_SIZE 4096
#define LOAD_LIBRARY_SHELLCODE_SIZE 22
#define REMOTE_PATCH_WAIT_MS 8000

static char inject_dll_path[PATH_BUFFER_SIZE];
static char full_exe_path[PATH_BUFFER_SIZE];

static void print_last_error(const char *action)
{
    fprintf(stderr, "%s failed with Win32 error %lu\n", action, GetLastError());
}

static BOOL create_load_library_shellcode(
    DWORD return_address,
    DWORD dll_path_address,
    unsigned char **shellcode,
    int *shellcode_size)
{
    HMODULE kernel32 = GetModuleHandleA("kernel32.dll");
    FARPROC load_library = kernel32 == NULL ? NULL : GetProcAddress(kernel32, "LoadLibraryA");

    if (load_library == NULL) {
        return FALSE;
    }

    unsigned char *return_bytes = (unsigned char *) &return_address;
    unsigned char *path_bytes = (unsigned char *) &dll_path_address;
    DWORD load_library_address = (DWORD) (ULONG_PTR) load_library;
    unsigned char *api_bytes = (unsigned char *) &load_library_address;

    unsigned char stub[] = {
        0x68, return_bytes[0], return_bytes[1], return_bytes[2], return_bytes[3],
        0x9C,
        0x60,
        0x68, path_bytes[0], path_bytes[1], path_bytes[2], path_bytes[3],
        0xB8, api_bytes[0], api_bytes[1], api_bytes[2], api_bytes[3],
        0xFF, 0xD0,
        0x61,
        0x9D,
        0xC3
    };

    *shellcode_size = LOAD_LIBRARY_SHELLCODE_SIZE;
    *shellcode = malloc(LOAD_LIBRARY_SHELLCODE_SIZE);
    if (*shellcode == NULL) {
        return FALSE;
    }

    memcpy(*shellcode, stub, LOAD_LIBRARY_SHELLCODE_SIZE);
    return TRUE;
}

int main(int argc, char *argv[])
{
    (void) argv;

    if (argc < 2) {
        fprintf(stderr, "Usage: SSFLoader.exe <path-to-disc.chd>\n");
        return 2;
    }

    if (GetFullPathNameA("ssf_patch.dll", PATH_BUFFER_SIZE, inject_dll_path, NULL) == 0) {
        print_last_error("Resolving ssf_patch.dll");
        return 1;
    }

    if (GetFullPathNameA("SSF.exe", PATH_BUFFER_SIZE, full_exe_path, NULL) == 0) {
        print_last_error("Resolving SSF.exe");
        return 1;
    }

    PROCESS_INFORMATION process_info;
    STARTUPINFOA startup_info;
    LPSTR command_line = GetCommandLineA();

    ZeroMemory(&startup_info, sizeof(startup_info));
    ZeroMemory(&process_info, sizeof(process_info));
    startup_info.cb = sizeof(startup_info);

    if (!CreateProcessA(
            full_exe_path,
            command_line,
            NULL,
            NULL,
            FALSE,
            CREATE_SUSPENDED,
            NULL,
            NULL,
            &startup_info,
            &process_info)) {
        print_last_error("Starting SSF.exe");
        return 1;
    }

    size_t dll_path_size = strlen(inject_dll_path) + 1;
    LPVOID remote_dll_path = VirtualAllocEx(
        process_info.hProcess,
        NULL,
        dll_path_size,
        MEM_COMMIT,
        PAGE_READWRITE);
    if (remote_dll_path == NULL) {
        print_last_error("Allocating remote DLL path");
        return 1;
    }

    CONTEXT context;
    ZeroMemory(&context, sizeof(context));
    context.ContextFlags = CONTEXT_CONTROL;

    if (!GetThreadContext(process_info.hThread, &context)) {
        print_last_error("Reading SSF thread context");
        return 1;
    }

    unsigned char *shellcode = NULL;
    int shellcode_size = 0;
    if (!create_load_library_shellcode(
            context.Eip,
            (DWORD) (ULONG_PTR) remote_dll_path,
            &shellcode,
            &shellcode_size)) {
        print_last_error("Creating LoadLibrary shellcode");
        return 1;
    }

    LPVOID remote_shellcode = VirtualAllocEx(
        process_info.hProcess,
        NULL,
        shellcode_size,
        MEM_COMMIT,
        PAGE_EXECUTE_READWRITE);
    if (remote_shellcode == NULL) {
        print_last_error("Allocating remote shellcode");
        free(shellcode);
        return 1;
    }

    if (!WriteProcessMemory(process_info.hProcess, remote_dll_path, inject_dll_path, dll_path_size, NULL)) {
        print_last_error("Writing DLL path into SSF");
        free(shellcode);
        return 1;
    }

    if (!WriteProcessMemory(process_info.hProcess, remote_shellcode, shellcode, shellcode_size, NULL)) {
        print_last_error("Writing shellcode into SSF");
        free(shellcode);
        return 1;
    }

    context.Eip = (DWORD) (ULONG_PTR) remote_shellcode;
    context.ContextFlags = CONTEXT_CONTROL;
    if (!SetThreadContext(process_info.hThread, &context)) {
        print_last_error("Redirecting SSF thread context");
        free(shellcode);
        return 1;
    }

    if (ResumeThread(process_info.hThread) == (DWORD) -1) {
        print_last_error("Resuming SSF");
        free(shellcode);
        return 1;
    }

    Sleep(REMOTE_PATCH_WAIT_MS);

    VirtualFreeEx(process_info.hProcess, remote_dll_path, dll_path_size, MEM_DECOMMIT);
    VirtualFreeEx(process_info.hProcess, remote_shellcode, shellcode_size, MEM_DECOMMIT);
    CloseHandle(process_info.hThread);
    CloseHandle(process_info.hProcess);
    free(shellcode);

    return 0;
}
