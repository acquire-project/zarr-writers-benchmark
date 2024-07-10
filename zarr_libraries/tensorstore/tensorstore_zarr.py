import tensorstore as ts
import time
import shutil
import numpy as np
from zarr_libraries import folder_size


def continuous_write(result_path: str, append_dim_size: int) -> tuple[list, list]:
    file_sizes = []
    bandwidths = []
    
    for i in range(1, append_dim_size + 1):
        zarr_spec = {
            'driver': 'zarr',
            'dtype': 'uint8',
            'kvstore': {
                'driver': 'file',
                'path': result_path,
            },
            'metadata': {
                'chunks': [64, 540, 960],
                'dimension_separator': '/',
                'dtype': '|u1',
                'fill_value': 0,
                'filters': None,
                'order': 'C',
                'shape': [(64 * i), 1080, 1920],
                'zarr_format': 2,
            }
        }
        
        t = time.perf_counter()
        zarr_data = np.random.randint(low=0, high=256, size=((64 * i), 1080, 1920), dtype=np.uint8)
        zarr_create = ts.open(zarr_spec, create=True, delete_existing=True).result()
        zarr_create[...].write(zarr_data).result()
        total_time = time.perf_counter() - t
        
        print(f"Write #{i}\nTensorStore -> creating zarr : {total_time} seconds")
        size = folder_size(result_path)
        file_sizes.append(size * 10**-9) # converts bytes to GB
        bandwidths.append((size * 10**-9) / total_time) # GB/s
        
    return file_sizes, bandwidths    
    

def continuous_write_append(result_path: str, append_dim_size: int) -> tuple[list, list]:
    file_sizes = []
    bandwidths = []
    total_time = 0
    
    zarr_spec = {
        'driver': 'zarr',
        'dtype': 'uint8',
        'kvstore': {
            'driver': 'file',
            'path': result_path,
        },
        'metadata': {
            'chunks': [64, 540, 960],
            'dimension_separator': '/',
            'dtype': '|u1',
            'fill_value': 0,
            'filters': None,
            'order': 'C',
            'shape': [64, 1080, 1920],
            'zarr_format': 2,
        }
    }
    t = time.perf_counter()
    zarr_data = np.random.randint(low=0, high=256, size=(64, 1080, 1920), dtype=np.uint8)
    zarr_create = ts.open(zarr_spec, create=True, delete_existing=True).result()
    zarr_create[...].write(zarr_data).result()
    total_time += (time.perf_counter() - t)    
    
    for i in range(2, append_dim_size + 1):
        t = time.perf_counter()
        zarr_create = zarr_create.resize(exclusive_max=((64 * i), 1080, 1920)).result()
        zarr_data = np.random.randint(low=0, high=256, size=(64, 1080, 1920), dtype=np.uint8)
        zarr_create[(64 * (i - 1)):, :, :].write(zarr_data).result()
        total_time += time.perf_counter() - t
            
        print(f"Write #{i}\nTensorStore -> appending zarr : {total_time} seconds")
        size = folder_size(result_path)
        file_sizes.append(size * 10**-9) # converts bytes to GB
        bandwidths.append((size * 10**-9) / total_time) # GB/s
      
    shutil.rmtree(result_path)
    return file_sizes, bandwidths


def copy_zarr(source_path: str, result_path: str) -> None:
    # copying data from source 
    zarr_store = ts.open(
        {
            'driver': 'zarr',
            'kvstore': {
                'driver': 'file',
                'path': source_path
            }
        },
        open=True
    ).result()
    zarr_data = zarr_store.read().result().copy()
    zarr_spec = zarr_store.spec().to_json()
  
    # writing data to the new folder
    create_zarr(result_path, zarr_spec=zarr_spec, zarr_data=zarr_data)


def create_zarr(folder_path: str, zarr_spec: dict, zarr_data: np.ndarray) -> None:
    zarr_spec['kvstore']['path'] = folder_path
    t = time.perf_counter()
    zarr_create = ts.open(zarr_spec, create=True, delete_existing=True).result()
    zarr_create[...].write(zarr_data).result()
    print(f"TensorStore -> creating zarr : {time.perf_counter() - t} seconds")
        