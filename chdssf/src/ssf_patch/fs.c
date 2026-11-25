// Filesystem Related Operations.

#include "global.h"
#include "sptd.h"
#include "fs.h"
// Hardcoded FS Patch Offset Constants
#define DEVICE_PATH "\\\\.\\"

#define SCSI_PASSTHROUGH_DIRECT 0x4D014
#define SCSI_HANDLE ((HANDLE)(UINT_PTR)0xB00BD001)

static int is_init_removable = 0;

// CreateFileA Hook
HANDLE __stdcall rfx_CreateFileA(LPCSTR lpFileName, DWORD dwDesiredAccess, DWORD dwShareMode, LPSECURITY_ATTRIBUTES lpSecurityAttributes, DWORD dwCreationDisposition, DWORD dwFlagsAndAttributes, HANDLE hTemplateFile){
    OutputDebugStringA("CreateFileA");
    OutputDebugStringA(lpFileName);

    if(strstr(lpFileName,DEVICE_PATH)!= 0){
        OutputDebugStringA("Optical Device Open Called.");
        return SCSI_HANDLE;
    }
    return CreateFileA(lpFileName,dwDesiredAccess,dwShareMode,lpSecurityAttributes,dwCreationDisposition,dwFlagsAndAttributes,hTemplateFile);
}

BOOL __stdcall rfx_CloseHandle(HANDLE hObject){
    if(hObject == SCSI_HANDLE){
        OutputDebugStringA("Closing Virtual SPTD Handle");
        return TRUE;
    }
    return CloseHandle(hObject);
}

BOOL __stdcall rfx_DeviceIoControl(HANDLE hDevice, DWORD dwIoControlCode, LPVOID lpInBuffer, DWORD nInBufferSize, LPVOID lpOutBuffer, DWORD nOutBufferSize, LPDWORD lpBytesReturned, LPOVERLAPPED lpOverlapped){
    if(hDevice == SCSI_HANDLE && dwIoControlCode == SCSI_PASSTHROUGH_DIRECT){
        return sptd_ioctl(hDevice,dwIoControlCode,lpInBuffer,nInBufferSize,lpOutBuffer,nOutBufferSize,lpBytesReturned,lpOverlapped);
    }
    return DeviceIoControl(hDevice,dwIoControlCode,lpInBuffer,nInBufferSize,lpOutBuffer,nOutBufferSize,lpBytesReturned,lpOverlapped);
}

// Return removable once, and that's it.
unsigned int __stdcall rfx_GetDriveTypeA(LPCSTR lpRootPathName){
    (void) lpRootPathName;

    if(is_init_removable == 0){
        is_init_removable = 1;
        return 5;
    }

    return 3;
}

// Startup Routine
void patch_fs(){
    // Save root patch
    // Various file hooks
    Hook_IAT_Name("KERNEL32.dll","CreateFileA",(uintptr_t)&rfx_CreateFileA);
    Hook_IAT_Name("KERNEL32.dll","DeviceIoControl",(uintptr_t)&rfx_DeviceIoControl);
    Hook_IAT_Name("KERNEL32.dll","GetDriveTypeA",(uintptr_t)&rfx_GetDriveTypeA);
    Hook_IAT_Name("KERNEL32.dll","CloseHandle",(uintptr_t)&rfx_CloseHandle);
}
