import numpy as np
import zarr 
import time
import shutil
from zarr_libraries import folder_size
from ome_zarr.io import parse_url
from ome_zarr.writer import write_image
from pathlib import Path
import matplotlib.pyplot as plt
import sys


class Ome_Zarr:
    def __init__(self, shape: list, chunks: list) -> None:
        self.abs_path_to_data = str((Path(__file__).parent / "../example_data/ome_zarr_data").resolve())
        self.shape = shape
        self.chunks = chunks
    
    
    def __continuous_write(self, result_path: str, append_dim_size: int) -> tuple[list, list]:
        file_sizes = []
        bandwidths = []
        
        for i in range(1, append_dim_size + 1):
            new_shape = (self.shape[0] * i, *self.shape[1:])  # modify the append dimension, unpack the rest
            
            store = parse_url(result_path, mode="w").store
            root = zarr.group(store=store)
            
            t = time.perf_counter()
            zarr_data = np.random.randint(low=0, high=256, size=new_shape, dtype=np.uint8)
            write_image(image=zarr_data, group=root, axes="tyx", storage_options=dict(chunks=self.chunks))
            total_time = time.perf_counter() - t

            print(f"Write #{i}\nOME-Zarr -> creating zarr : {total_time} seconds")
            size = folder_size(result_path)
            file_sizes.append(size * 10**-9) # converts bytes to GB
            bandwidths.append((size * 10**-9) / total_time) # GB/s
            shutil.rmtree(result_path)
            
        return file_sizes, bandwidths
    
    
    def __continuous_append(self, result_path: str, append_dim_size: int) -> tuple[list, list]:
        file_sizes = []
        bandwidths = []
        total_time = 0
        
        store = parse_url(result_path, mode="w").store
        root = zarr.group(store=store)
        
        t = time.perf_counter()
        zarr_data = np.random.randint(low=0, high=256, size=self.shape, dtype=np.uint8)
        write_image(image=zarr_data, group=root, axes="tyx", storage_options=dict(chunks=self.chunks))
        total_time += time.perf_counter() - t
        shutil.rmtree(result_path)
        
        for i in range(2, append_dim_size + 1):
            t = time.perf_counter()
            new_data = np.random.randint(low=0, high=256, size=self.shape, dtype=np.uint8)
            zarr_data = np.concatenate((zarr_data, new_data), axis=0)
            write_image(image=zarr_data, group=root, axes="tyx", storage_options=dict(chunks=self.chunks))
            total_time += time.perf_counter() - t
            
            print(f"Write #{i}\nOME-Zarr -> append zarr : {total_time} seconds")
            size = folder_size(result_path)
            file_sizes.append(size * 10**-9) # converts bytes to GB
            bandwidths.append((size * 10**-9) / total_time) # GB/s
            shutil.rmtree(result_path)
        
        return file_sizes, bandwidths  
    
    
    def continuous_write_test(self, append_dim_size: int) -> None:
        print("\n\n--------OME-Zarr Stress Test--------\n\n")
        file_sizes, bandwidths = self.__continuous_write(
            result_path = self.abs_path_to_data + "/stressTest.zarr",
            append_dim_size = append_dim_size
            )
        print("--------------------------------------------------------------\n\n")
        plt.plot(file_sizes, bandwidths, label="ome-zarr writes")
        
        
    def continuous_append_test(self, append_dim_size: int) -> None:
        print("\n\n--------Ome-Zarr Append Stress Test--------\n\n")
        file_sizes, bandwidths = self.__continuous_append(
            result_path = self.abs_path_to_data + "/stressTestAppend.zarr",
            append_dim_size = append_dim_size
            )
        print("--------------------------------------------------------------\n\n")
        plt.plot(file_sizes, bandwidths, label="ome-zarr append")
        
        