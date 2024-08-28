from zarr_libraries.tensorstore.tensorstore_zarr import Tensorstore
from zarr_libraries.common import folder_size_in_bytes
from pathlib import Path
import shutil
import numpy as np
import pytest


def test_getting_data_path_from_tensorstore():
    tensorstore = Tensorstore()
    
    expected_path = str((Path(__file__).parent / "../zarr_libraries/example_data/tensorstore_data/test.zarr").resolve())
    assert tensorstore.data_path == expected_path
    

@pytest.mark.parametrize(
    ("shape", "chunks"),
    [
        ([256, 256, 256], [64, 64, 64]),
        ([64, 128, 256], [32, 64, 64]),
    ]
)   
def test_tensorstore_writes_correct_amount_of_data(shape: list, chunks: list):
    tensorstore = Tensorstore()
    
    zarr_data = np.random.randint(low=0, high=256, size=shape, dtype=np.uint8)
    tensorstore.write_zarr(shape=shape, chunks=chunks, zarr_data=zarr_data)
    expected_size = np.prod(shape)
    
    # the actual size can be larger but can never be smaller that expected size
    assert folder_size_in_bytes(tensorstore.data_path) >= expected_size
    shutil.rmtree(tensorstore.data_path)    
    

@pytest.mark.parametrize(
    ("shape", "chunks"),
    [
        ([256, 256, 256], [64, 64, 64]),
        ([64, 128, 256], [32, 64, 64]),
    ]
)  
def test_zarr_python_append_writes_correct_amount_of_data(shape: list, chunks: list):
    tensorstore = Tensorstore()
    
    zarr_data = np.random.randint(low=0, high=256, size=shape, dtype=np.uint8)
    tensorstore.append_zarr(shape=shape, chunks=chunks, new_shape=shape, zarr_data=zarr_data, multiplier=1)
    expected_size = np.prod(shape)
    
    # checking the size of the first append
    assert folder_size_in_bytes(tensorstore.data_path) >= expected_size
    
    new_shape = [shape[0] * (2), *shape[1:]]
    new_data = np.random.randint(low=0, high=256, size=shape, dtype=np.uint8)
    tensorstore.append_zarr(shape=shape, chunks=chunks, new_shape=new_shape, zarr_data=new_data, multiplier=2)
    expected_size = np.prod(new_shape)
    
    # changing the shape and comparing the expected size after the second append
    assert folder_size_in_bytes(tensorstore.data_path) >= expected_size
    shutil.rmtree(tensorstore.data_path)
    