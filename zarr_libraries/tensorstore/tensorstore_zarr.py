import tensorstore as ts
import time
import shutil
import numpy as np
from zarr_libraries import folder_size
from pathlib import Path
import matplotlib.pyplot as plt


class Tensorstore:
    def __init__(self, shape: list, chunks: list) -> None:
        self.abs_path_to_data = str((Path(__file__).parent / "../example_data/tensorstore_data").resolve()) 
        self.shape = shape
        self.chunks = chunks      
        
    
    def __continuous_write(self, result_path: str, append_dim_size: int) -> tuple[list, list]:
        file_sizes = []
        bandwidths = []
        
        for i in range(0, append_dim_size + 1, 10):
            new_shape = [self.shape[0] * i, *self.shape[1:]]  # modify the append dimension, unpack the rest
            
            zarr_spec = {
                'driver': 'zarr',
                'dtype': 'uint8',
                'kvstore': {
                    'driver': 'file',
                    'path': result_path,
                },
                'metadata': {
                    'chunks': self.chunks,
                    'dimension_separator': '/',
                    'dtype': '|u1',
                    'fill_value': 0,
                    'filters': None,
                    'order': 'C',
                    'shape': new_shape,
                    'zarr_format': 2,
                }
            }
            
            zarr_data = np.random.randint(low=0, high=256, size=new_shape, dtype=np.uint8)
            zarr_create = ts.open(zarr_spec, create=True, delete_existing=True).result()
            
            t = time.perf_counter()
            zarr_create[...].write(zarr_data).result()
            total_time = time.perf_counter() - t
            
            print(f"Write #{i}\nTensorStore -> creating zarr : {total_time} seconds")
            folder_size(result_path)
            size = np.prod(new_shape)
            file_sizes.append(size * 10**-9) # converts bytes to GB
            bandwidths.append((size * 10**-9) / total_time) # GB/s
            
        return file_sizes, bandwidths 
    
    
    def __continuous_append(self, result_path: str, append_dim_size: int) -> tuple[list, list]:
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
                'chunks': self.chunks,
                'dimension_separator': '/',
                'dtype': '|u1',
                'fill_value': 0,
                'filters': None,
                'order': 'C',
                'shape': self.shape,
                'zarr_format': 2,
            }
        }
        t = time.perf_counter()
        zarr_data = np.random.randint(low=0, high=256, size=self.shape, dtype=np.uint8)
        zarr_create = ts.open(zarr_spec, create=True, delete_existing=True).result()
        zarr_create[...].write(zarr_data).result()
        total_time += (time.perf_counter() - t)    
        
        for i in range(2, append_dim_size + 1):
            new_shape = [self.shape[0] * i, *self.shape[1:]]  # modify the append dimension, unpack the rest
            
            t = time.perf_counter()
            zarr_create = zarr_create.resize(exclusive_max=new_shape).result()
            zarr_data = np.random.randint(low=0, high=256, size=self.shape, dtype=np.uint8)
            zarr_create[(self.shape[0] * (i - 1)):, :, :].write(zarr_data).result()
            total_time += time.perf_counter() - t
                
            print(f"Write #{i}\nTensorStore -> appending zarr : {total_time} seconds")
            size = folder_size(result_path)
            file_sizes.append(size * 10**-9) # converts bytes to GB
            bandwidths.append((size * 10**-9) / total_time) # GB/s
        
        shutil.rmtree(result_path)
        return file_sizes, bandwidths


    def __create_zarr(self, folder_path: str, zarr_spec: dict, zarr_data: np.ndarray) -> None:
        zarr_spec['kvstore']['path'] = folder_path
        t = time.perf_counter()
        zarr_create = ts.open(zarr_spec, create=True, delete_existing=True).result()
        zarr_create[...].write(zarr_data).result()
        print(f"TensorStore -> creating zarr : {time.perf_counter() - t} seconds")
        
        
    def _copy_zarr(self, source_path: str, result_path: str) -> None:
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
        self.__create_zarr(result_path, zarr_spec=zarr_spec, zarr_data=zarr_data)
        
    
    def continuous_write_test(self, append_dim_size: int) -> None:
        print("\n\n--------Tensorstore Stress Test--------\n\n")
        file_sizes, bandwidths = self.__continuous_write(
            result_path = self.abs_path_to_data + "/stressTest.zarr",
            append_dim_size = append_dim_size
            )
        print("--------------------------------------------------------------\n\n")
        plt.plot(file_sizes, bandwidths, label="tensorstore writes")


    def continuous_append_test(self, append_dim_size: int) -> None:
        print("\n\n--------Tensorstore Stress Test--------\n\n")
        file_sizes, bandwidths = self.__continuous_append(
            result_path = self.abs_path_to_data + "/stressTestAppend.zarr",
            append_dim_size = append_dim_size
            )
        print("--------------------------------------------------------------\n\n")
        plt.plot(file_sizes, bandwidths, label="tensorstore append")
        
        