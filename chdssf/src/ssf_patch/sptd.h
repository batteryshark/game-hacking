#ifndef SSF_PATCH_SPTD_H
#define SSF_PATCH_SPTD_H

#include <windows.h>

BOOL __stdcall sptd_ioctl(HANDLE hDevice, DWORD dwIoControlCode, LPVOID lpInBuffer, DWORD nInBufferSize, LPVOID lpOutBuffer, DWORD nOutBufferSize, LPDWORD lpBytesReturned, LPOVERLAPPED lpOverlapped);
void init_sptd(void);

#endif
