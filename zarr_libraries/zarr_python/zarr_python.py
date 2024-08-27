import zarr 
import numpy as np
import time 
import zarr.storage
from pathlib import Path
from numcodecs import Blosc


class Zarr_Python:
    def __init__(self) -> None:
        self.__path_to_data = str((Path(__file__).parent / "../example_data/zarr_python_data/test.zarr").resolve())
        self.__compressor = Blosc(cname="lz4", clevel=1)


    @property
    def data_path(self) -> str:
        return self.__path_to_data 

    
    def write_zarr(self, shape: list, chunks: list, zarr_data: np.ndarray) -> float:
        zarr_create = zarr.open(
            self.data_path,  
            mode="w", 
            shape=shape,   
            chunks=chunks, 
            dtype="u1",
            compressor=self.__compressor
            )

        # timing the data written to the zarr folder in seconds
        t = time.perf_counter()
        zarr_create[...] = zarr_data
        total_time = time.perf_counter() - t

        return total_time


    def append_zarr(self, shape: list, chunks: list, zarr_data: np.ndarray) -> float:
        # if there is no data to append to, create it
        if not Path(self.data_path).exists():
            return self.write_zarr(shape=shape, chunks=chunks, zarr_data=zarr_data)
 
        zarr_folder = zarr.open(self.data_path)
        
        # timing the data getting appended to the back of the zarr folder 
        t = time.perf_counter()
        zarr_folder.append(zarr_data)
        total_time = time.perf_counter() - t
        
        return total_time
         