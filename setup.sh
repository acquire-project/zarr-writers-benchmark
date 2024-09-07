#!/bin/bash

BUILD_DIR="build"

# check if the directory exists
if [ -d "$BUILD_DIR" ]; then
  echo "Directory '$BUILD_DIR' exists. Deleting it..."
  rm -rf "$BUILD_DIR"
else
  echo "Directory '$BUILD_DIR' does not exist. No need to delete."
fi

# build cpp code 
cmake --preset=default || { echo "Failed to run cmake '$BUILD_DIR'"; exit 1; }
cmake --build build || { echo "Failed to build"; exit 1; }