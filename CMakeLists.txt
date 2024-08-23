cmake_minimum_required(VERSION 3.2)
project(cpp-zarr)
cmake_policy(SET CMP0057 NEW)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# finding the cppZarr lib
find_library(cppZarrLib cppZarr REQUIRED)

# setting include dir for dependencies
include_directories(/usr/local/include)

# pybind11
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
include_directories(${Python3_INCLUDE_DIRS})

find_package(pybind11 REQUIRED)
include_directories(${pybind11_INCLUDE_DIR})

pybind11_add_module(pyCppZarr zarr_libraries/cpp_zarr/cpp_zarr.cpp)
target_link_libraries(pyCppZarr PRIVATE ${cppZarrLib})