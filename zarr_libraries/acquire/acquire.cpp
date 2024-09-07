#include "zarr.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <time.h>
#include <chrono>
#include <cstdio>
#include <vector>

#define SIZED(str) str, sizeof(str)

namespace py = pybind11;
using namespace std::chrono;
using namespace std;

float write_zarr(string path, vector<uint64_t> chunks, vector<uint64_t> shape)
{
    Zarr_set_log_level(LogLevel_Debug);

    ZarrStreamSettings *settings = ZarrStreamSettings_create();
    ZarrStreamSettings_set_store_path(settings, path.c_str(), sizeof(path.c_str()));
    ZarrStreamSettings_set_data_type(settings, ZarrDataType_uint8);

    ZarrStreamSettings_set_compressor(settings, ZarrCompressor_Blosc1);
    ZarrStreamSettings_set_compression_codec(settings,
                                             ZarrCompressionCodec_BloscLZ4);
    ZarrStreamSettings_set_compression_level(settings, 1);
    ZarrStreamSettings_set_compression_shuffle(settings, 1);

    ZarrStreamSettings_reserve_dimensions(settings, 3);
    ZarrStreamSettings_set_dimension(settings,
                                     0,
                                     SIZED("t"),
                                     ZarrDimensionType_Time,
                                     shape[0],
                                     chunks[0], // chunk size; could be whatever you want here
                                     0);
    ZarrStreamSettings_set_dimension(settings,
                                     1,
                                     SIZED("y"),
                                     ZarrDimensionType_Space,
                                     shape[1],
                                     chunks[1], // chunk size; could be whatever you want here
                                     0);
    ZarrStreamSettings_set_dimension(settings,
                                     2,
                                     SIZED("x"),
                                     ZarrDimensionType_Space,
                                     shape[2],
                                     chunks[2], // chunk size; could be whatever you want here
                                     0);

    ZarrStream *stream = ZarrStream_create(settings, ZarrVersion_2);

    // acquire
    const size_t chunk_size = shape[0] * shape[1] * shape[2];
    std::vector<uint8_t> chunk(chunk_size); // one chunk's worth of data, fill this however you want

    // filling with random data
    for (uint8_t &val : chunk)
    {
        val = (uint8_t)(rand() % (UINT8_MAX + 1));
    }

    // write out a single chunk. Wrap this in a for loop to write out as many chunks as you want
    size_t bytes_written;

    auto begin_time = high_resolution_clock::now();
    ZarrError status = ZarrStream_append(stream, chunk.data(), chunk_size * sizeof(uint8_t), &bytes_written);
    duration<float, ratio<1>> duration = high_resolution_clock::now() - begin_time;

    if (status != ZarrError_Success)
    {
        printf("Error: %s\n", Zarr_get_error_message(status));
        return 1;
    }

    if (bytes_written != chunk_size * sizeof(uint8_t))
    {
        printf("Error: wrote %zu bytes, expected %zu\n", bytes_written, chunk_size * sizeof(uint8_t));
        return 1;
    }

    // cleanup
    ZarrStream_destroy(stream);

    return duration.count();
}

PYBIND11_MODULE(pyAcquire, handle)
{
    handle.def("write_zarr", &write_zarr);
}
