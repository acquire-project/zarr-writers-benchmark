#include "zarr.h"

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <chrono>

namespace py = pybind11;
namespace chrono = std::chrono;

namespace inner {
std::vector<uint64_t> chunks;
std::vector<uint64_t> shape;
ZarrStream *stream = nullptr;

float append_zarr(std::string path, std::vector<uint64_t> chunks,
                  std::vector<uint64_t> shape, std::vector<uint8_t> data) {
  auto *settings = ZarrStreamSettings_create();

  ZarrStreamSettings_set_store(settings, path.c_str(), path.size() + 1,
                               nullptr);

  ZarrStreamSettings_reserve_dimensions(settings, 3);
  ZarrDimensionProperties dim = {
      .name = "t",
      .bytes_of_name = sizeof("t"),
      .kind = ZarrDimensionType_Time,
      .array_size_px = static_cast<uint32_t>(shape[0]),
      .chunk_size_px = static_cast<uint32_t>(chunks[0]),
      .shard_size_chunks = 0};
  ZarrStreamSettings_set_dimension(settings, 0, &dim);

  dim = {.name = "y",
         .bytes_of_name = sizeof("y"),
         .kind = ZarrDimensionType_Space,
         .array_size_px = static_cast<uint32_t>(shape[1]),
         .chunk_size_px = static_cast<uint32_t>(chunks[1]),
         .shard_size_chunks = 0};
  ZarrStreamSettings_set_dimension(settings, 1, &dim);

  dim = {.name = "x",
         .bytes_of_name = sizeof("x"),
         .kind = ZarrDimensionType_Space,
         .array_size_px = static_cast<uint32_t>(shape[2]),
         .chunk_size_px = static_cast<uint32_t>(chunks[2]),
         .shard_size_chunks = 0};
  ZarrStreamSettings_set_dimension(settings, 2, &dim);

  auto *stream = ZarrStream_create(settings, ZarrVersion_2);

  auto begin_time = chrono::high_resolution_clock::now();
  size_t bytes_out;
  ZarrStream_append(stream, data.data(), data.size(), &bytes_out);
  chrono::duration<float, std::ratio<1>> duration =
      chrono::high_resolution_clock::now() - begin_time;

  ZarrStreamSettings_destroy(settings);

  return duration.count();
}
} // namespace inner

void reset_stream(const std::vector<uint64_t> &chunks,
                  const std::vector<uint64_t> &shape) {
  ZarrStream_destroy(inner::stream);
  inner::stream = nullptr;
  inner::chunks = chunks;
  inner::shape = shape;
}

float append_zarr(std::string path, std::vector<uint64_t> chunks,
                  std::vector<uint64_t> shape, py::array_t<uint8_t> data) {
  if (inner::chunks.empty() || inner::shape.empty() ||
      inner::chunks.size() != chunks.size() ||
      inner::shape.size() != shape.size()) {
    reset_stream(chunks, shape);
  } else {
    for (auto i = 0; i < chunks.size(); i++) {
      if (chunks[i] != inner::chunks[i] || shape[i] != inner::shape[i]) {
        reset_stream(chunks, shape);
        break;
      }
    }
  }

  if (!inner::stream) {
    auto *settings = ZarrStreamSettings_create();

    ZarrStreamSettings_set_store(settings, path.c_str(), path.size() + 1,
                                 nullptr);

    ZarrStreamSettings_reserve_dimensions(settings, 3);
    ZarrDimensionProperties dim = {
        .name = "t",
        .bytes_of_name = sizeof("t"),
        .kind = ZarrDimensionType_Time,
        .array_size_px = static_cast<uint32_t>(shape[0]),
        .chunk_size_px = static_cast<uint32_t>(chunks[0]),
        .shard_size_chunks = 0};
    ZarrStreamSettings_set_dimension(settings, 0, &dim);

    dim = {.name = "y",
           .bytes_of_name = sizeof("y"),
           .kind = ZarrDimensionType_Space,
           .array_size_px = static_cast<uint32_t>(shape[1]),
           .chunk_size_px = static_cast<uint32_t>(chunks[1]),
           .shard_size_chunks = 0};
    ZarrStreamSettings_set_dimension(settings, 1, &dim);

    dim = {.name = "x",
           .bytes_of_name = sizeof("x"),
           .kind = ZarrDimensionType_Space,
           .array_size_px = static_cast<uint32_t>(shape[2]),
           .chunk_size_px = static_cast<uint32_t>(chunks[2]),
           .shard_size_chunks = 0};
    ZarrStreamSettings_set_dimension(settings, 2, &dim);
    inner::stream = ZarrStream_create(settings, ZarrVersion_2);

    ZarrStreamSettings_destroy(settings);
  }

  auto begin_time = chrono::high_resolution_clock::now();
  size_t bytes_out;
  ZarrStream_append(inner::stream, data.data(), data.size(), &bytes_out);
  chrono::duration<float, std::ratio<1>> duration =
      chrono::high_resolution_clock::now() - begin_time;

  return duration.count();
}

float write_zarr(std::string path, std::vector<uint64_t> chunks,
                 std::vector<uint64_t> shape) {

  std::vector<uint8_t> data(shape[0] * shape[1] * shape[2]);
  srand((unsigned int)time(NULL));
  for (auto &elem : data) {
    elem = (uint8_t)(rand() % (UINT8_MAX + 1));
  }

  return inner::append_zarr(path, chunks, shape, data);
}

PYBIND11_MODULE(pyAcquireZarr, handle) {
  handle.def("append_zarr", &append_zarr);
  handle.def("write_zarr", &write_zarr);
}