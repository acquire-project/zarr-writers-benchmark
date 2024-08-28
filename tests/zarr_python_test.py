from zarr_libraries.zarr_python.zarr_python import Zarr_Python
from zarr_libraries.common import folder_size_in_bytes
from pathlib import Path
import shutil
import numpy as np
import pytest


def test_getting_data_path_from_zarr_python():
    zarr_python = Zarr_Python()
    
    expected_path = str((Path(__file__).parent / "../zarr_libraries/example_data/zarr_python_data/test.zarr").resolve())
    assert zarr_python.data_path == expected_path
    

@pytest.mark.parametrize(
    ("shape", "chunks"),
    [
        ([256, 256, 256], [64, 64, 64]),
        ([64, 128, 256], [32, 64, 64]),
    ]
)   
def test_zarr_python_writes_correct_amount_of_data(shape: list, chunks: list):
    zarr_python = Zarr_Python()
    
    zarr_data = np.random.randint(low=0, high=256, size=shape, dtype=np.uint8)
    zarr_python.write_zarr(shape=shape, chunks=chunks, zarr_data=zarr_data)
    expected_size = np.prod(shape)
    
    assert folder_size_in_bytes(zarr_python.data_path) >= expected_size
    shutil.rmtree(zarr_python.data_path)    
    

@pytest.mark.parametrize(
    ("shape", "chunks"),
    [
        ([256, 256, 256], [64, 64, 64]),
        ([64, 128, 256], [32, 64, 64]),
    ]
)
def test_zarr_python_append_writes_correct_amount_of_data(shape: list, chunks: list):
    zarr_python = Zarr_Python()
    
    zarr_data = np.random.randint(low=0, high=256, size=shape, dtype=np.uint8)
    zarr_python.append_zarr(shape=shape, chunks=chunks, zarr_data=zarr_data)
    expected_size = np.prod(shape)
    
    assert folder_size_in_bytes(zarr_python.data_path) >= expected_size
    
    new_shape = [shape[0] * (2), *shape[1:]]
    new_data = np.random.randint(low=0, high=256, size=shape, dtype=np.uint8)
    zarr_python.append_zarr(shape=shape, chunks=chunks, zarr_data=new_data)
    expected_size = np.prod(new_shape)
    
    assert folder_size_in_bytes(zarr_python.data_path) >= expected_size
    shutil.rmtree(zarr_python.data_path)
