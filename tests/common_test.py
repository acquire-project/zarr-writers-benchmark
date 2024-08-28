from zarr_libraries.common import folder_size_in_bytes, formatted_folder_size
from pathlib import Path
import os
import shutil 
import pytest


@pytest.mark.parametrize(
    ("num_mb"),
    [
        (1),
        (10),
        (50),
        (100),
        (500),
        (750)
    ]
)
def test_folder_size_in_bytes(num_mb: int):
    MBs = num_mb * 1048576
    test_data_path = str((Path(__file__).parent / "test_data"))
    
    # prevents error from making a dir that already exists (unlikely)
    if not Path(test_data_path).exists():
        os.mkdir(str((Path(__file__).parent / "test_data")))
    
    # creating a test file of size 50 MB
    with open(test_data_path + "/test.bin", "wb") as f:
        f.write(os.urandom(MBs))
        
    # custom tolerance of 4096 bytes which is about 0.00390625 MB's
    assert abs(folder_size_in_bytes(test_data_path) - MBs) <= 4096
    shutil.rmtree(test_data_path)
    
        