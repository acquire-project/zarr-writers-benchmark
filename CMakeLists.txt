cmake_minimum_required(VERSION 3.15)
project(cpp-zarr)
cmake_policy(SET CMP0057 NEW)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Find libraries and packages
find_library(cppZarrLib cppZarr REQUIRED)
find_package(blosc CONFIG REQUIRED)
find_package(miniocpp CONFIG REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 CONFIG REQUIRED)

# Set up acquire-zarr to link against
set(azlib "${CMAKE_CURRENT_LIST_DIR}/zarr_libraries/acquire/lib/libacquire-zarr.so")

# Setting include directories for cpp-zarr
include_directories(/usr/local/include)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/zarr_libraries/acquire/include)

# Define pybind11 modules
pybind11_add_module(pyCppZarr zarr_libraries/cpp_zarr/cpp_zarr.cpp)
target_link_libraries(pyCppZarr PRIVATE ${cppZarrLib})

pybind11_add_module(pyAcquire zarr_libraries/acquire/acquire.cpp)

# target_include_directories(pyAcquire PRIVATE ${CMAKE_CURRENT_LIST_DIR}/zarr_libraries/acquire/include)
target_link_libraries(pyAcquire PRIVATE miniocpp::miniocpp blosc_static ${azlib})
