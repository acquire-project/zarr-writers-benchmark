import zarr 
import numpy as np
import time 
import shutil
from zarr_libraries import folder_size
import matplotlib.pyplot as plt
from pathlib import Path


class Zarr_Python:
    def __init__(self, shape: list, chunks: list) -> None:
        self.abs_path_to_data = str((Path(__file__).parent / "../example_data/zarr_python_data").resolve())
        self.shape = shape
        self.chunks = chunks

    
    def __continuous_write(self, result_path: str, append_dim_size: int) -> tuple[list, list]:
        file_sizes = []
        bandwidths = []
        
        for i in range(1, append_dim_size + 1):
            new_shape = (self.shape[0] * i, *self.shape[1:])  # modify the append dimension, unpack the rest
            
            zarr_create = zarr.open(
                result_path,  
                mode="w", 
                shape=new_shape,   
                chunks=self.chunks, 
                dtype="u1"
                )
            
            t = time.perf_counter()
            zarr_data = np.random.randint(low=0, high=256, size=new_shape, dtype=np.uint8)
            zarr_create[...] = zarr_data
            total_time = time.perf_counter() - t

            print(f"Write #{i}\nzarr-python -> creating zarr : {total_time} seconds")
            size = folder_size(result_path)
            file_sizes.append(size * 10**-9) # converts bytes to GB
            bandwidths.append((size * 10**-9) / total_time) # GB/s
            
        return file_sizes, bandwidths
    
    
    def __continuous_append(self, result_path: str, append_dim_size: int) -> tuple[list, list]:
        file_sizes = []
        bandwidths = []
        
        t = time.perf_counter()
        zarr_data = np.random.randint(low=0, high=256, size=self.shape, dtype=np.uint8)
        zarr_create = zarr.open(
                result_path,  
                mode="w", 
                shape=self.shape, 
                chunks=self.chunks, 
                dtype="u1"
                )
        zarr_create[...] = zarr_data
        total_time = time.perf_counter() - t
        
        for i in range(2, append_dim_size + 1):
            t = time.perf_counter()
            zarr_create.append(np.random.randint(low=0, high=256, size=self.shape, dtype=np.uint8))
            total_time += time.perf_counter() - t
            
            print(f"Write #{i}\nzarr-python -> appending zarr : {total_time} seconds")
            size = folder_size(result_path)
            file_sizes.append(size * 10**-9) # converts bytes to GB
            bandwidths.append((size * 10**-9) / total_time) # GB/s
            
        shutil.rmtree(result_path)
        return file_sizes, bandwidths


    def continuous_write_test(self, append_dim_size: int) -> None:
        print("\n\n--------Zarr-Python Stress Test--------\n\n")
        file_sizes, bandwidths = self.__continuous_write(
            result_path = self.abs_path_to_data + "/stressTest.zarr",
            append_dim_size = append_dim_size
            )
        print("--------------------------------------------------------------\n\n")
        plt.plot(file_sizes, bandwidths, label="zarr-python writes")
    

    def continuous_append_test(self, append_dim_size: int) -> None:
        print("\n\n--------Zarr-Python Append Stress Test--------\n\n")
        file_sizes, bandwidths = self.__continuous_append(
            result_path = self.abs_path_to_data + "/stressTestAppend.zarr",
            append_dim_size = append_dim_size
            )
        print("--------------------------------------------------------------\n\n")
        plt.plot(file_sizes, bandwidths, label="zarr-python append")
        
        