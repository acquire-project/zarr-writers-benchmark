import zarr 
import numpy as np
import time 
import shutil
import zarr.storage
from zarr_libraries import folder_size
from pathlib import Path
import matplotlib.axes
from numcodecs import Blosc


class Zarr_Python:
    def __init__(self, shape: list, chunks: list) -> None:
        self.abs_path_to_data = str((Path(__file__).parent / "../example_data/zarr_python_data").resolve())
        self.shape = shape
        self.chunks = chunks
        self.compressor = Blosc(cname="lz4", clevel=1)

    
    def __continuous_write(self, result_path: str, append_dim_size: int, step: int) -> tuple[list, list]:
        file_sizes = []
        bandwidths = []
        
        for i in range(0, append_dim_size, step):
            new_shape = (self.shape[0] * (i + 1), *self.shape[1:])  # modify the append dimension, unpack the rest
            
            # create zarr folder with new shape and initialize the data
            zarr_create = zarr.open(
                result_path,  
                mode="w", 
                shape=new_shape,   
                chunks=self.chunks, 
                dtype="u1",
                compressor=self.compressor
                )
            zarr_data = np.random.randint(low=0, high=256, size=new_shape, dtype=np.uint8)

            # timing the data written to the zarr folder in seconds
            t = time.perf_counter()
            zarr_create[...] = zarr_data
            total_time = time.perf_counter() - t

            # prints info to the terminal
            print(f"Write #{i + 1}\nzarr-python -> creating zarr : {total_time} seconds")
            folder_size(result_path)
            
            size = np.prod(new_shape) # 3d array filled with 1 byte ints so multiplication gives accurate size in bytes
            file_sizes.append(size * 10**-9) # converts bytes to GB
            bandwidths.append((size * 10**-9) / total_time) # GB/s
            shutil.rmtree(result_path) # clean up by deleting created zarr folder   

        return file_sizes, bandwidths
    
    
    def __continuous_append(self, result_path: str, append_dim_size: int) -> tuple[list, list]:
        write_number = []
        bandwidths = []
        
        # create zarr folder and fill with initial data 
        zarr_data = np.random.randint(low=0, high=256, size=self.shape, dtype=np.uint8)
        zarr_create = zarr.open(
                result_path,  
                mode="w", 
                shape=self.shape, 
                chunks=self.chunks, 
                dtype="u1",
                compressor=self.compressor
                )
        zarr_create[...] = zarr_data
        
        for i in range(2, append_dim_size + 1):
            # timing the data getting appended to the back of the zarr folder 
            t = time.perf_counter()
            zarr_create.append(np.random.randint(low=0, high=256, size=self.shape, dtype=np.uint8))
            total_time = time.perf_counter() - t
            
            # prints info to the terminal 
            print(f"Write #{i}\nzarr-python -> appending zarr : {total_time} seconds")
            folder_size(result_path)
            
            size = np.prod(self.shape) # 3d array filled with 1 byte ints so multiplication gives accurate size in bytes
            write_number.append(i) # appends the current write number 
            bandwidths.append((size * 10**-9) / total_time) # GB/s
            
        shutil.rmtree(result_path) # clean up by deleting zarr folder
        return write_number, bandwidths


    def continuous_write_test(self, graph: matplotlib.axes._axes.Axes, 
                              avg_graph: matplotlib.axes._axes.Axes, 
                              append_dim_size: int, step: int) -> int:
        # calls continuous write function and graphs results
        print("\n\n--------Zarr-Python Stress Test--------\n\n")
        file_sizes, bandwidths = self.__continuous_write(
            result_path = self.abs_path_to_data + "/stressTest.zarr",
            append_dim_size = append_dim_size,
            step = step
            )
        print("--------------------------------------------------------------\n\n")
        graph.plot(file_sizes, bandwidths, label="Zarr-Python", marker='o')
        avg_graph.bar("Zarr-Python", np.average(bandwidths))
        return np.average(bandwidths)


    def continuous_append_test(self, graph: matplotlib.axes._axes.Axes, 
                               avg_graph: matplotlib.axes._axes.Axes, 
                               append_dim_size: int) -> int:
        # calls continuous append function and graphs results
        print("\n\n--------Zarr-Python Append Stress Test--------\n\n")
        write_number, bandwidths = self.__continuous_append(
            result_path = self.abs_path_to_data + "/stressTestAppend.zarr",
            append_dim_size = append_dim_size
            )
        print("--------------------------------------------------------------\n\n")
        graph.plot(write_number, bandwidths, label="Zarr-Python")
        avg_graph.bar("Zarr-Python", np.average(bandwidths))
        return np.average(bandwidths)
        
        