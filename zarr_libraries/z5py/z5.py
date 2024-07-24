import z5py 
import numpy as np
from pathlib import Path
import time
from zarr_libraries import folder_size
import shutil
import matplotlib.axes

class Z5:
    def __init__(self, shape: list, chunks: list) -> None:
        self.abs_path_to_data = str((Path(__file__).parent / "../example_data/z5py_data").resolve()) 
        self.shape = shape
        self.chunks = chunks

    
    def __continuous_write(self, result_path: str, append_dim_size: int, step: int) -> tuple[list, list]:
        file_sizes = []
        bandwidths = []
        
        for i in range(0, append_dim_size, step):
            new_shape = [self.shape[0] * (i + 1), *self.shape[1:]]  # modify the append dimension, unpack the rest
            
            # create zarr folder with new shape and initialize the data to be written 
            zarr_create = z5py.File(result_path, use_zarr_format=True)
            ds = zarr_create.create_dataset('data', shape=new_shape, chunks=self.chunks, dtype='uint8')
            zarr_data = np.random.randint(low=0, high=256, size=new_shape, dtype=np.uint8)
            
            # timing the writing of the data to the zarr data set in seconds 
            t = time.perf_counter()
            ds[...] = zarr_data
            total_time = time.perf_counter() - t
            
            # prints info to the terminal
            print(f"Write #{i + 1}\nz5py -> creating zarr : {total_time} seconds")
            folder_size(result_path)
            
            size = np.prod(new_shape) # 3d array filled with 1 byte ints so multiplication gives accurate size in bytes
            file_sizes.append(size * 10**-9) # converts bytes to GB
            bandwidths.append((size * 10**-9) / total_time) # GB/s
            shutil.rmtree(result_path) # clean up by deleting zarr folder, must be done every iteration of loop or z5 will throw a fit
        
        return file_sizes, bandwidths
    

    def continuous_write_test(self, graph: matplotlib.axes._axes.Axes, avg_graph: matplotlib.axes._axes.Axes, append_dim_size: int, step: int) -> None:
        # calls continuous write function and graphs results
        print("\n\n--------z5py Stress Test--------\n\n")
        file_sizes, bandwidths = self.__continuous_write(
            result_path = self.abs_path_to_data + "/stressTest.zarr",
            append_dim_size = append_dim_size,
            step = step
            )
        print("--------------------------------------------------------------\n\n")
        graph.plot(file_sizes, bandwidths, label="z5py", marker='o')
        avg_graph.bar("z5py", np.average(bandwidths))

        