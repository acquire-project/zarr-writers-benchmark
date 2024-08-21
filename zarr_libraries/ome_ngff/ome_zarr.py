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
    
    
    def __continuous_write(self, result_path: str, append_dim_size: int, step: int) -> tuple[list, list]:
        file_sizes = []
        bandwidths = []
        
        for i in range(0, append_dim_size, step):
            new_shape = (self.shape[0] * (i + 1), *self.shape[1:])  # modify the append dimension, unpack the rest
            
            # create zarr folder with new shape and initialize data for the folder 
            store = parse_url(result_path, mode="w").store
            root = zarr.group(store=store)
            zarr_data = np.random.randint(low=0, high=256, size=new_shape, dtype=np.uint8)

            # timing the writing of the data to the zarr folder
            t = time.perf_counter()
            write_image(image=zarr_data, group=root, axes="tyx", storage_options=dict(chunks=(self.chunks)))
            total_time = time.perf_counter() - t

            # print info to the terminal 
            print(f"Write #{i + 1}\nOME-Zarr -> creating zarr : {total_time} seconds")
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
        print("\n\n--------OME-Zarr Stress Test--------\n\n")
        file_sizes, bandwidths = self.__continuous_write(
            result_path = self.abs_path_to_data + "/stressTest.zarr",
            append_dim_size = append_dim_size,
            step = step
            )
        print("--------------------------------------------------------------\n\n")
        graph.plot(file_sizes, bandwidths, label="OME-Zarr", marker='o')
        avg_graph.bar("OME-Zarr", np.average(bandwidths))
        return float(np.average(bandwidths))

        