#include "parallelwritezarr.h"
#include "zarr.h"
#include <chrono>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <time.h>
#include <vector>

#include <iostream>

namespace py = pybind11;
using namespace std;
using namespace std::chrono;

float write_zarr(string path, vector<uint64_t> chunks, vector<uint64_t> shape) {
  // starting and ending coordinates of where to write the data
  const vector<uint64_t> startCoords{0, 0, 0};
  const vector<uint64_t> endCoords = shape;
  const vector<uint64_t> writeShape({endCoords[0] - startCoords[0],
                                     endCoords[1] - startCoords[1],
                                     endCoords[2] - startCoords[2]});

  // create the data that will be added to the zarr folder
  size_t arrSize = writeShape[0] * writeShape[1] * writeShape[2];
  void *zarrArr = malloc(arrSize * sizeof(uint8_t));
  srand((unsigned int)time(NULL));
  for (size_t i = 0; i < arrSize; i++) {
    ((uint8_t *)zarrArr)[i] = (uint8_t)(rand() % (UINT8_MAX + 1));
  }

  // creat zarr object and set metadata
  zarr zarrObject;
  zarrObject.set_fileName(path);
  zarrObject.set_dtype("<u1");
  zarrObject.set_shape(writeShape);
  zarrObject.set_chunks(chunks);
  zarrObject.set_fill_value(1);
  zarrObject.set_order("C");
  zarrObject.set_dimension_separator("/");
  zarrObject.set_clevel((uint64_t)1);
  zarrObject.set_chunkInfo(startCoords, endCoords);
  zarrObject.write_zarray();

  // create zarr files and benchmark time
  auto begin_time = high_resolution_clock::now();
  parallelWriteZarr(zarrObject, zarrArr, startCoords, endCoords, writeShape, 8,
                    true, false);
  duration<float, ratio<1>> duration =
      high_resolution_clock::now() - begin_time;

  free(zarrArr);

  return duration.count();
}

PYBIND11_MODULE(pyCppZarr, handle) { handle.def("write_zarr", &write_zarr); }
