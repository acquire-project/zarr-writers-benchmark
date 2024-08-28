import tensorstore as ts
import time
import numpy as np
from pathlib import Path


class Tensorstore:
    def __init__(self) -> None:
        self.__path_to_data = str((Path(__file__).parent / "../example_data/tensorstore_data/test.zarr").resolve())     
        
        
    @property
    def data_path(self) -> str:
        return self.__path_to_data 
        
   
    def write_zarr(self, shape: list, chunks: list, zarr_data: np.ndarray) -> float:
        # The metadata for the zarr folder that is to be created (specifications)
        zarr_spec = {
            'driver': 'zarr',
            'dtype': 'uint8',
            'kvstore': {
                'driver': 'file',
                'path': self.data_path,
            },
            'metadata': {
                'compressor': {
                    'id': 'blosc',
                    'cname': 'lz4',
                    'clevel': 1  
                },
                'chunks': chunks,
                'dimension_separator': '/',
                'dtype': '|u1',
                'fill_value': 0,
                'filters': None,
                'order': 'C',
                'shape': shape,
                'zarr_format': 2,
            }
        }
        
        zarr_create = ts.open(zarr_spec, create=True, delete_existing=True).result()  
            
        # timing the writing of the data to the zarr folder in seconds
        t = time.perf_counter()
        zarr_create[...].write(zarr_data).result()
        total_time = time.perf_counter() - t
        
        return total_time


    def append_zarr(self, shape: list, chunks: list, new_shape: list, zarr_data: np.ndarray, multiplier: int) -> float:
        # if there is no data to append to, create it
        if not Path(self.data_path).exists():
            return self.write_zarr(shape=shape, chunks=chunks, zarr_data=zarr_data)
        
        zarr_folder = ts.open(
            {
                'driver': 'zarr',
                'kvstore': {
                    'driver': 'file',
                    'path': self.data_path
                }
            },
            open=True
        ).result()
    
        # timing the appending of the data to the back of the zarr folder
        t = time.perf_counter()
        zarr_folder = zarr_folder.resize(exclusive_max=new_shape).result()
        zarr_folder[(shape[0] * (multiplier - 1)):, :, :].write(zarr_data).result()
        total_time = time.perf_counter() - t
        
        return total_time   
        