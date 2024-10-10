find_path(ACQUIRE_ZARR_ROOT_DIR
        NAMES "include/zarr.types.h"
        PATHS
        $ENV{HOME}/.local
        DOC "Acquire-Zarr location"
        NO_CACHE
)

if (ACQUIRE_ZARR_ROOT_DIR)
    message(STATUS "Acquire-Zarr found: ${ACQUIRE_ZARR_ROOT_DIR}")

    set(lib acquire-zarr)
    add_library(${lib} STATIC IMPORTED GLOBAL)
    target_include_directories(${lib} INTERFACE ${ACQUIRE_ZARR_ROOT_DIR}/include)
    set_target_properties(${lib} PROPERTIES
            IMPORTED_LOCATION ${ACQUIRE_ZARR_ROOT_DIR}/lib/libacquire-zarr.so
    )
else ()
    message(FATAL_ERROR "Acquire-Zarr NOT FOUND")
endif ()