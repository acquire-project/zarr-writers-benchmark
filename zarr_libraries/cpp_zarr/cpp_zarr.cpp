#include <iostream>
#include <vector>
#include <filesystem>
#include <time.h>
#include "zarr.h"
#include "parallelwritezarr.h"
#include <pybind11/pybind11.h>

namespace py = pybind11;
using namespace std;

class Cpp_Zarr
{
public:
    Cpp_Zarr() = default;

    int write_zarr()
    {
        const vector<uint64_t> startCoords{0, 0, 0};
        const vector<uint64_t> endCoords{64, 1920, 1920};
        const vector<uint64_t> writeShape({endCoords[0] - startCoords[0],
                                           endCoords[1] - startCoords[1],
                                           endCoords[2] - startCoords[2]});

        // random data
        size_t arrSize = writeShape[0] * writeShape[1] * writeShape[2];
        void *zarrArr = malloc(arrSize * sizeof(uint8_t));
        srand((unsigned int)time(NULL));
        for (size_t i = 0; i < arrSize; i++)
        {
            ((uint8_t *)zarrArr)[i] = (uint8_t)(rand() % (UINT8_MAX + 1));
        }

        // creat zarr object
        zarr zarrObject;

        zarrObject.set_fileName("/home/chris/code/zarr-writers-benchmark/test.zarr");
        zarrObject.set_dtype("<u1");
        zarrObject.set_shape(writeShape);
        zarrObject.set_chunks({64, 256, 256});
        zarrObject.set_chunkInfo(startCoords, endCoords);
        zarrObject.set_fill_value(1);
        zarrObject.set_order("C");
        zarrObject.set_dimension_separator("/");
        zarrObject.write_zarray();

        parallelWriteZarr(zarrObject, zarrArr, startCoords, endCoords, writeShape, 8, true, false);

        free(zarrArr);

        return 0;
    }
};

PYBIND11_MODULE(pyCppZarr, handle)
{
    py::class_<Cpp_Zarr>(
        handle, "Cpp_Zarr")
        .def(py::init<>())
        .def("write_zarr", &Cpp_Zarr::write_zarr);
}
