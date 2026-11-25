cmake_minimum_required(VERSION 3.20)
project(CHDSSF LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

if(NOT WIN32)
    message(FATAL_ERROR "CHDSSF is a Win32 process patch for SSF and only builds for Windows targets.")
endif()

function(chdssf_configure_win32_target target_name)
    target_compile_features(${target_name} PRIVATE c_std_11)

    if(MINGW)
        target_compile_options(${target_name} PRIVATE -m32)
        target_link_options(${target_name} PRIVATE -m32)
    endif()

    if(NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
        message(WARNING
            "${target_name} is expected to be built with a 32-bit Windows toolchain. "
            "Use the MSYS2 mingw32 compiler or a Win32 generator.")
    endif()
endfunction()

add_executable(SSFLoader src/loader/main.c)
chdssf_configure_win32_target(SSFLoader)

add_subdirectory(src/ssf_patch)
