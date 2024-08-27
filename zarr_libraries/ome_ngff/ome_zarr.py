import numpy as np
import zarr 
import time
from ome_zarr.io import parse_url
from ome_zarr.writer import write_image
from pathlib import Path


class Ome_Zarr:
    def __init__(self) -> None:
        self.__path_to_data = str((Path(__file__).parent / "../example_data/ome_zarr_data/test.zarr").resolve())
    
    
    @property
    def data_path(self) -> str:
        return self.__path_to_data 
    
    
    def write_zarr(self, chunks: list, zarr_data: np.ndarray) -> float:
        # create zarr folder with new shape and initialize data for the folder 
        store = parse_url(self.data_path, mode="w").store
        root = zarr.group(store=store)

        # timing the data written to the zarr folder in seconds
        t = time.perf_counter()
        write_image(image=zarr_data, group=root, axes="tyx", storage_options=dict(chunks=(chunks)))
        total_time = time.perf_counter() - t
        
        return total_time
        