import tensorstore as ts
import time
import shutil
import numpy as np
from zarr_libraries import folder_size
from pathlib import Path
import matplotlib.axes


class Tensorstore:
    def __init__(self, shape: list, chunks: list) -> None:
        self.abs_path_to_data = str((Path(__file__).parent / "../example_data/tensorstore_data").resolve()) 
        self.shape = shape
        self.chunks = chunks      
        
    
    def __continuous_write(self, result_path: str, append_dim_size: int, step: int) -> tuple[list, list]:
        file_sizes = []
        bandwidths = []
        
        for i in range(0, append_dim_size, step):
            new_shape = [self.shape[0] * (i + 1), *self.shape[1:]]  # modify the append dimension, unpack the rest
            
            # The metadata for the zarr folder that is to be created (specifications)
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
            
            # populate the data for the zarr folder with new shape and create the folder itself 
            zarr_data = np.random.randint(low=0, high=256, size=new_shape, dtype=np.uint8)
            zarr_create = ts.open(zarr_spec, create=True, delete_existing=True).result()  
            
            # timing the writing of the data to the zarr folder in seconds
            t = time.perf_counter()
            zarr_create[...].write(zarr_data).result()
            total_time = time.perf_counter() - t
            
            # prints info to the terminal
            print(f"Write #{i + 1}\nTensorStore -> creating zarr : {total_time} seconds")
            folder_size(result_path)
            
            size = np.prod(new_shape) # 3d array filled with 1 byte ints so multiplication gives accurate size in bytes
            file_sizes.append(size * 10**-9) # converts bytes to GB
            bandwidths.append((size * 10**-9) / total_time) # GB/s
            
        shutil.rmtree(result_path) # clean up by deleting zarr folder
        return file_sizes, bandwidths 
    
    
    def __continuous_append(self, result_path: str, append_dim_size: int) -> tuple[list, list]:
        write_number = []
        bandwidths = []
        
        # The metadata for the zarr folder that is to be created (specifications)
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
        
        # create and write initial data
        zarr_data = np.random.randint(low=0, high=256, size=self.shape, dtype=np.uint8)
        zarr_create = ts.open(zarr_spec, create=True, delete_existing=True).result()
        zarr_create[...].write(zarr_data).result()  
        
        for i in range(2, append_dim_size + 1):
            new_shape = [self.shape[0] * i, *self.shape[1:]]  # modify the append dimension, unpack the rest
            zarr_data = np.random.randint(low=0, high=256, size=self.shape, dtype=np.uint8)
            
            # use resize function in tensorstore to dynamically resize the zarr folder that we created 
            # timing the writing of the data to the back of the zarr folder in seconds
            t = time.perf_counter()
            zarr_create = zarr_create.resize(exclusive_max=new_shape).result()
            zarr_create[(self.shape[0] * (i - 1)):, :, :].write(zarr_data).result()
            total_time = time.perf_counter() - t
                
            # print info to the terminal
            print(f"Write #{i}\nTensorStore -> appending zarr : {total_time} seconds")
            folder_size(result_path)
            
            size = np.prod(self.shape) # 3d array filled with 1 byte ints so multiplication gives accurate size in bytes
            write_number.append(i) # append the write number
            bandwidths.append((size * 10**-9) / total_time) # GB/s
        
        shutil.rmtree(result_path)
        return write_number, bandwidths
        
    
    def continuous_write_test(self, graph: matplotlib.axes._axes.Axes, avg_graph: matplotlib.axes._axes.Axes, append_dim_size: int, step: int) -> None:
        # calls continuous write function and graphs results
        print("\n\n--------Tensorstore Stress Test--------\n\n")
        file_sizes, bandwidths = self.__continuous_write(
            result_path = self.abs_path_to_data + "/stressTest.zarr",
            append_dim_size = append_dim_size,
            step = step
            )
        print("--------------------------------------------------------------\n\n")
        graph.plot(file_sizes, bandwidths, label="TensorStore", marker='o')
        avg_graph.bar("TensorStore", np.average(bandwidths))


    def continuous_append_test(self, graph: matplotlib.axes._axes.Axes, avg_graph: matplotlib.axes._axes.Axes, append_dim_size: int) -> None:
        # calls continuous append function and graphs results
        print("\n\n--------Tensorstore Stress Test--------\n\n")
        write_number, bandwidths = self.__continuous_append(
            result_path = self.abs_path_to_data + "/stressTestAppend.zarr",
            append_dim_size = append_dim_size
            )
        print("--------------------------------------------------------------\n\n")
        graph.plot(write_number, bandwidths, label="TensorStore")
        avg_graph.bar("TensorStore", np.average(bandwidths))
        
        