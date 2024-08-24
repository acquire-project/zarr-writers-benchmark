from build.pyCppZarr import *
from pathlib import Path
import numpy as np


class Cpp_Zarr:
    def __init__(self) -> None:
        self.__path_to_data = str((Path(__file__).parent / "../example_data/cpp_zarr_data/test.zarr").resolve())
        
    
    def write_zarr(self, shape: list, chunks: list, zarr_data: np.ndarray[np.uint8]) -> int:
        return write_zarr(self.get_data_path(), chunks, shape)

  
    def get_data_path(self) -> str:
        return self.__path_to_data
        