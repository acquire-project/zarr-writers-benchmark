from build.pyAcquireZarr import *

from pathlib import Path
import numpy as np


class Acquire_Zarr:
    def __init__(self) -> None:
        self.__path_to_data = str(
            (
                Path(__file__).parent / "../example_data/acquire_zarr_data/test.zarr"
            ).resolve()
        )

    @property
    def data_path(self) -> str:
        return self.__path_to_data

    def append_zarr(self, shape: list, chunks: list, zarr_data: np.ndarray) -> float:
        return append_zarr(self.data_path, chunks, shape, zarr_data)

    def write_zarr(self, shape: list, chunks: list) -> float:
        return write_zarr(self.data_path, chunks, shape)
