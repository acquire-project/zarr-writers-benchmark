import numpy as np
import zarr 
import time
import shutil
from zarr_libraries import folder_size
from ome_zarr.io import parse_url
from ome_zarr.writer import write_image


def continuous_write(result_path: str, append_dim_size: int) -> tuple[list, list]:
    file_sizes = []
    bandwidths = []
    
    for i in range(1, append_dim_size + 1):
        store = parse_url(result_path, mode="w").store
        root = zarr.group(store=store)
        
        t = time.perf_counter()
        zarr_data = np.random.randint(low=0, high=256, size=((64 * i), 1080, 1920), dtype=np.uint8)
        write_image(image=zarr_data, group=root, axes="tyx", storage_options=dict(chunks=(64, 540, 960)))
        total_time = time.perf_counter() - t

        print(f"Write #{i}\nOME-Zarr -> creating zarr : {total_time} seconds")
        size = folder_size(result_path)
        file_sizes.append(size * 10**-9) # converts bytes to GB
        bandwidths.append((size * 10**-9) / total_time) # GB/s
        shutil.rmtree(result_path)
        
    return file_sizes, bandwidths


def continuous_write_append(result_path: str, append_dim_size: int) -> tuple[list, list]:
    file_sizes = []
    bandwidths = []
    total_time = 0
    
    store = parse_url(result_path, mode="w").store
    root = zarr.group(store=store)
    
    t = time.perf_counter()
    zarr_data = np.random.randint(low=0, high=256, size=(64, 1080, 1920), dtype=np.uint8)
    write_image(image=zarr_data, group=root, axes="tyx", storage_options=dict(chunks=(64, 540, 960)))
    total_time += time.perf_counter() - t
    shutil.rmtree(result_path)
    
    for i in range(2, append_dim_size + 1):
        t = time.perf_counter()
        new_data = np.random.randint(low=0, high=256, size=((64 * i), 1080, 1920), dtype=np.uint)
        zarr_data = np.concatenate((zarr_data, new_data), axis=0)
        write_image(image=zarr_data, group=root, axes="tyx", storage_options=dict(chunks=(64, 540, 960)))
        total_time += time.perf_counter() - t
        
        print(f"Write #{i}\nOME-Zarr -> append zarr : {total_time} seconds")
        size = folder_size(result_path)
        file_sizes.append(size * 10**-9) # converts bytes to GB
        bandwidths.append((size * 10**-9) / total_time) # GB/s
        shutil.rmtree(result_path)
    
    return file_sizes, bandwidths  
