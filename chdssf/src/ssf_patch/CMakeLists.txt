set(SSF_PATCH_SOURCES
    chd_helper.h
    fs.c
    fs.h
    global.c
    global.h
    main.c
    main.h
    sptd.c
    sptd.h
)

add_library(ssf_patch SHARED ${SSF_PATCH_SOURCES})
set_target_properties(ssf_patch PROPERTIES PREFIX "")
chdssf_configure_win32_target(ssf_patch)
target_link_libraries(ssf_patch PRIVATE shell32)
