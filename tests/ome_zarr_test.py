from zarr_libraries.ome_ngff.ome_zarr import Ome_Zarr
from zarr_libraries.common import folder_size_in_bytes
from pathlib import Path
import numpy as np
import shutil
import pytest


def test_getting_data_path_from_ome_zarr():
    ome_zarr = Ome_Zarr()
    
    expected_path = str((Path(__file__).parent / "../zarr_libraries/example_data/ome_zarr_data/test.zarr").resolve())
    assert ome_zarr.data_path == expected_path


@pytest.mark.parametrize(
    ("shape", "chunks"),
    [
        ([256, 256, 256], [64, 64, 64]),
        ([64, 128, 256], [32, 64, 64]),
    ]
)
def test_ome_zarr_writes_correct_amount_of_data(shape: list, chunks: list):
    ome_zarr = Ome_Zarr()
    
    zarr_data = np.random.randint(low=0, high=256, size=shape, dtype=np.uint8)
    ome_zarr.write_zarr(chunks=chunks, zarr_data=zarr_data)
    expected_size = np.prod(shape)
    
    # the actual size can be larger but can never be smaller that expected size
    assert folder_size_in_bytes(ome_zarr.data_path) >= expected_size
    shutil.rmtree(ome_zarr.data_path)
    