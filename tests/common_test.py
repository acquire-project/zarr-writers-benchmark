from zarr_libraries.common import folder_size_in_bytes, formatted_folder_size
import os 
import pytest
from tempfile import TemporaryDirectory


@pytest.fixture
def temp_dir():
    with TemporaryDirectory() as temp_dir:
        yield temp_dir


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
def test_folder_size_in_bytes(temp_dir, num_mb: int):
    mb_in_bytes = 1048576
    MBs = num_mb * mb_in_bytes
    
    # creating a test file of size variable size 
    with open(temp_dir + "/test.bin", "wb") as f:
        f.write(os.urandom(MBs))
        
    # custom tolerance of 4096 bytes which is about 0.00390625 MB's
    assert abs(folder_size_in_bytes(temp_dir) - MBs) <= 4096
    

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
def test_formatted_folder_size(temp_dir, num_mb: int):
    mb_in_bytes = 1048576
    MBs = num_mb * mb_in_bytes     

    # creating a test file of size variable size 
    with open(temp_dir + "/test.bin", "wb") as f:
        f.write(os.urandom(MBs))
        
    # checking if the formatted size w/o the decimal values is equal to expected
    assert formatted_folder_size(temp_dir).split(".")[0] == str(num_mb)
    