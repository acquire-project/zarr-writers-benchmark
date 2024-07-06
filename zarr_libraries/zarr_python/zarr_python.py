import zarr 
import numpy as np
import time 
from zarr_libraries import folder_size

def continuous_write(result_path: str, append_dim_size: int) -> tuple[list, list]:
    file_sizes = []
    bandwidths = []
    
    for i in range(1, append_dim_size + 1):
        zarr_create = zarr.open(
            result_path,  
            mode="w", 
            shape=((64 * i), 1080, 1920), 
            chunks=(64, 540, 960), 
            dtype="u1"
            )
        
        t = time.perf_counter()
        zarr_data = np.random.randint(low=0, high=256, size=((64 * i), 1080, 1920), dtype=np.uint8)
        zarr_create[...] = zarr_data
        total_time = time.perf_counter() - t

        print(f"Write #{i}\nzarr-python -> creating zarr : {total_time} seconds")
        size = folder_size(result_path)
        file_sizes.append(size * 10**-9) # converts bytes to GB
        bandwidths.append((size * 10**-9) / total_time) # GB/s
        
    return file_sizes, bandwidths


def continuous_write_append(result_path: str, append_dim_size: int) -> tuple[list, list]:
    file_sizes = []
    bandwidths = []
    
    t = time.perf_counter()
    zarr_data = np.random.randint(low=0, high=256, size=(64, 1080, 1920), dtype=np.uint8)
    zarr_create = zarr.open(
            result_path,  
            mode="w", 
            shape=(64, 1080, 1920), 
            chunks=(64, 540, 960), 
            dtype="u1"
            )
    zarr_create[...] = zarr_data
    total_time = time.perf_counter() - t
    
    for i in range(2, append_dim_size + 1):
        t = time.perf_counter()
        zarr_create.append(np.random.randint(low=0, high=256, size=(64, 1080, 1920), dtype=np.uint8))
        total_time += time.perf_counter() - t
        
        print(f"Write #{i}\nzarr-python -> appending zarr : {total_time} seconds")
        size = folder_size(result_path)
        file_sizes.append(size * 10**-9) # converts bytes to GB
        bandwidths.append((size * 10**-9) / total_time) # GB/s
        
    return file_sizes, bandwidths
