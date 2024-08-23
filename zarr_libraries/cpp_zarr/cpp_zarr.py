from build.pyCppZarr import *
from zarr_libraries import folder_size
from pathlib import Path
import matplotlib.axes
import numpy as np
import shutil


class Cpp_Zarr:
    def __init__(self, shape: list, chunks: list) -> None:
        self.abs_path_to_data = str((Path(__file__).parent / "../example_data/cpp_zarr_data").resolve())
        self.shape = shape
        self.chunks = chunks
    
    
    def __continuous_write(self, result_path: str, append_dim_size: int, step: int) -> tuple[list, list]:
        file_sizes = []
        bandwidths = []
        
        for i in range(0, append_dim_size, step):
            new_shape = (self.shape[0] * (i + 1), *self.shape[1:])  # modify the append dimension, unpack the rest
            
            # write zarr files and store total time taken 
            total_time = write_zarr(result_path, self.chunks, new_shape)

            # print info to the terminal 
            print(f"Write #{i + 1}\nCpp Zarr -> creating zarr : {total_time} seconds")
            print(f"The zarr folder is of size {folder_size(result_path)}\n\n")
            
            size = np.prod(new_shape) # 3d array filled with 1 byte ints so multiplication gives accurate size in bytes
            file_sizes.append(size * 10**-9) # converts bytes to GB
            bandwidths.append((size * 10**-9) / total_time) # GB/s
            shutil.rmtree(result_path)
            
        return file_sizes, bandwidths
    
    
    def continuous_write_test(self, graph: matplotlib.axes._axes.Axes, 
                              avg_graph: matplotlib.axes._axes.Axes, 
                              append_dim_size: int, step: int) -> float:
        # calls continuous write function and graphs results
        print("\n\n--------Cpp Zarr Stress Test--------\n\n")
        file_sizes, bandwidths = self.__continuous_write(
            result_path = self.abs_path_to_data + "/stressTest.zarr",
            append_dim_size = append_dim_size,
            step = step
            )
        print("--------------------------------------------------------------\n\n")
        graph.plot(file_sizes, bandwidths, label="Cpp Zarr", marker='o')
        avg_graph.bar("Cpp Zarr", np.average(bandwidths))
        return float(np.average(bandwidths))

        