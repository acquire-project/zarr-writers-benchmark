import zarr_libraries
from zarr_libraries.tensorstore import tensorstore_zarr
from zarr_libraries.acquire import acquire_zarr

# acquire basic benchmark
acquire_data_path = "zarr_libraries/example_data/"
acquire_zarr.setup_camera("simulated: radial sin", acquire_data_path + "radialSin.zarr")
acquire_zarr.setup_dimensions(
    x_array_size=1920,
    x_chunk_size=960,
    y_array_size=1080,
    y_chunk_size=540,
    t_array_size=0,
    t_chunk_size=64
)
acquire_zarr.create_zarr()
zarr_libraries.folder_size(acquire_data_path + "radialSin.zarr/0")
#zarr_libraries.view_zarr(acquire_data_path + "radialSin.zarr/0")

# tensorstore basic benchmark
tensorstore_data_path = "zarr_libraries/example_data/"
tensorstore_zarr.copy_zarr(tensorstore_data_path + "radialSinTs.zarr/0", tensorstore_data_path + "radialSinTsCreate.zarr")
zarr_libraries.folder_size(tensorstore_data_path + "radialSinTsCreate.zarr")
#zarr_libraries.view_zarr(tensorstore_data_path + "radialSinTsCreate.zarr")