from pathlib import Path
import shutil 
import zarr_libraries
from zarr_libraries.tensorstore import tensorstore_zarr
from zarr_libraries.acquire import acquire_zarr


abs_path_to_data = str(Path(__file__).parent / "zarr_libraries/example_data/")

print("\nRadial sin Zarr data\n---------------------\n")
# acquire 
for i in range(1, 1):
    acquire_zarr.setup_camera("simulated: radial sin", abs_path_to_data + f"/acquire_data/radialSin{i}.zarr", max_frames=64*i)
    print(f"Acquire Folder {i}")
    acquire_zarr.setup_dimensions(
        x_array_size=1920,
        x_chunk_size=960,
        y_array_size=1080,
        y_chunk_size=540,
        t_array_size=0,
        t_chunk_size=64
    )
    acquire_zarr.create_zarr()
    zarr_libraries.folder_size(abs_path_to_data + f"/acquire_data/radialSin{i}.zarr/0")
    shutil.rmtree(abs_path_to_data + f"/acquire_data/radialSin{i}.zarr")

print("--------------------------------------------------------------\n\n")

# tensorstore
for i in range(1, 11):
    print(f"TensorStore Folder {i}")
    tensorstore_zarr.copy_zarr(abs_path_to_data + f"/tensorstore_data/radialSinTs{i}.zarr", abs_path_to_data + f"/tensorstore_data/radialSinTs{i}.zarr")
    zarr_libraries.folder_size(abs_path_to_data + f"/tensorstore_data/radialSinTs{i}.zarr")

print("--------------------------------------------------------------\n\n")

'''
print("\nUniform random Zarr data\n-------------------------")
#acquire 
abs_path_to_data = "zarr_libraries/example_data/"
acquire_zarr.setup_camera("simulated: uniform random", abs_path_to_data + "uniformRandom.zarr", max_frames=64)
acquire_zarr.setup_dimensions(
    x_array_size=1920,
    x_chunk_size=960,
    y_array_size=1080,
    y_chunk_size=540,
    t_array_size=0,
    t_chunk_size=64
)
acquire_zarr.create_zarr()
zarr_libraries.folder_size(abs_path_to_data + "uniformRandom.zarr/0")
#zarr_libraries.view_zarr(abs_path_to_data + "uniformRandom.zarr/0")

# tensorstore
tensorstore_zarr.copy_zarr(abs_path_to_data + "uniformRandomTs.zarr", abs_path_to_data + "uniformRandomTs.zarr")
zarr_libraries.folder_size(abs_path_to_data + "uniformRandomTs.zarr")
'''
