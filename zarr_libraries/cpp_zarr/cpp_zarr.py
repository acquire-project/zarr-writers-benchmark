from build.pyCppZarr import *
from pathlib import Path
import numpy as np


class Cpp_Zarr:
    def __init__(self) -> None:
        self.__path_to_data = str((Path(__file__).parent / "../example_data/cpp_zarr_data/test.zarr").resolve())
        
        
    @property
    def data_path(self) -> str:
        return self.__path_to_data
    
    
    def write_zarr(self, shape: list, chunks: list) -> float:
        return write_zarr(self.data_path, chunks, shape)
    