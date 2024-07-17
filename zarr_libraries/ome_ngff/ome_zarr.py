import numpy as np
import zarr 
import time
import shutil
from zarr_libraries import folder_size
from ome_zarr.io import parse_url
from ome_zarr.writer import write_image
from pathlib import Path
import matplotlib.axes


class Ome_Zarr:
    def __init__(self, shape: list, chunks: list) -> None:
        self.abs_path_to_data = str((Path(__file__).parent / "../example_data/ome_zarr_data").resolve())
        self.shape = shape
        self.chunks = chunks
    
    
    def __continuous_write(self, result_path: str, append_dim_size: int) -> tuple[list, list]:
        file_sizes = []
        bandwidths = []
        
        for i in range(10, append_dim_size + 1, 10):
            new_shape = (self.shape[0] * i, *self.shape[1:])  # modify the append dimension, unpack the rest
            
            # create zarr folder with new shape and initialize data for the folder 
            store = parse_url(result_path, mode="w").store
            root = zarr.group(store=store)
            zarr_data = np.random.randint(low=0, high=256, size=new_shape, dtype=np.uint8)

            # timing the writing of the data to the zarr folder
            t = time.perf_counter()
            write_image(image=zarr_data, group=root, axes="tyx", storage_options=dict(chunks=(self.chunks)))
            total_time = time.perf_counter() - t

            # print info to the terminal 
            print(f"Write #{i}\nOME-Zarr -> creating zarr : {total_time} seconds")
            folder_size(result_path)
            
            size = np.prod(new_shape) # 3d array filled with 1 byte ints so multiplication gives accurate size in bytes
            file_sizes.append(size * 10**-9) # converts bytes to GB
            bandwidths.append((size * 10**-9) / total_time) # GB/s
            shutil.rmtree(result_path)
            
        return file_sizes, bandwidths
    
    
    def __continuous_append(self, result_path: str, append_dim_size: int) -> tuple[list, list]:
        write_number = []
        bandwidths = []
        
        # create and write initial data
        store = parse_url(result_path, mode="w").store
        root = zarr.group(store=store)
        
        zarr_data = np.random.randint(low=0, high=256, size=self.shape, dtype=np.uint8)
        write_image(image=zarr_data, group=root, axes="tyx", storage_options=dict(chunks=self.chunks))
        shutil.rmtree(result_path)
        
        for i in range(2, append_dim_size + 1):
            # create a new numpy array of size "shape" and attach it to the back of our original array
            new_data = np.random.randint(low=0, high=256, size=self.shape, dtype=np.uint8)
            zarr_data = np.concatenate((zarr_data, new_data), axis=0)
            
            # timing the writing of the data to the zarr folder
            t = time.perf_counter()
            write_image(image=zarr_data, group=root, axes="tyx", storage_options=dict(chunks=self.chunks))
            total_time = time.perf_counter() - t
            
            # print info to the terminal 
            print(f"Write #{i}\nOME-Zarr -> append zarr : {total_time} seconds")
            folder_size(result_path)
            
            size = np.prod(self.shape) # 3d array filled with 1 byte ints so multiplication gives accurate size in bytes
            write_number.append(i) # converts bytes to GB
            bandwidths.append((size * 10**-9) / total_time) # GB/s
            shutil.rmtree(result_path) # clean up by deleting zarr folder, must be done every iteration of loop or ome will throw a fit
        
        return write_number, bandwidths  
    
    
    def continuous_write_test(self, graph: matplotlib.axes._axes.Axes, append_dim_size: int) -> None:
        # calls continuous write function and graphs results
        print("\n\n--------OME-Zarr Stress Test--------\n\n")
        file_sizes, bandwidths = self.__continuous_write(
            result_path = self.abs_path_to_data + "/stressTest.zarr",
            append_dim_size = append_dim_size
            )
        print("--------------------------------------------------------------\n\n")
        graph.plot(file_sizes, bandwidths, label="OME-Zarr")
        
        
    def continuous_append_test(self, graph: matplotlib.axes._axes.Axes, append_dim_size: int) -> None:
        # calls continuous append function and graphs results
        print("\n\n--------Ome-Zarr Append Stress Test--------\n\n")
        write_number, bandwidths = self.__continuous_append(
            result_path = self.abs_path_to_data + "/stressTestAppend.zarr",
            append_dim_size = append_dim_size
            )
        print("--------------------------------------------------------------\n\n")
        graph.plot(write_number, bandwidths, label="OME-Zarr")
        
        