from zarr_libraries.cpp_zarr.cpp_zarr import *
from zarr_libraries.common import folder_size_in_bytes
from pathlib import Path
import shutil
import numpy as np
import pytest


def test_getting_data_path_from_cpp_zarr():
    cpp_zarr = Cpp_Zarr()
    
    expected_path = str((Path(__file__).parent / "../zarr_libraries/example_data/cpp_zarr_data/test.zarr").resolve())
    assert cpp_zarr.data_path == expected_path
    

@pytest.mark.parametrize(
    ("shape", "chunks"),
    [
        ([256, 256, 256], [64, 64, 64]),
        ([64, 128, 256], [32, 64, 64]),
    ]
)
def test_cpp_zarr_writes_correct_amount_of_data(shape: list, chunks: list):
    cpp_zarr = Cpp_Zarr()
    
    cpp_zarr.write_zarr(shape=shape, chunks=chunks)
    expected_size = np.prod(shape)
    
    assert folder_size_in_bytes(cpp_zarr.data_path) >= expected_size
    shutil.rmtree(cpp_zarr.data_path)    
    