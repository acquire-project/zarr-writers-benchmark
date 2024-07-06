from pathlib import Path
import shutil 
import matplotlib.pyplot as plt 
import zarr_libraries
from zarr_libraries.tensorstore import tensorstore_zarr
from zarr_libraries.acquire import acquire_zarr
from zarr_libraries.zarr_python import zarr_python


abs_path_to_data = str(Path(__file__).parent / "zarr_libraries/example_data/")
frame_multipliers = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
    12, 13, 14, 15, 16, 17, 18, 19, 20,
    25, 30, 35, 40, 45, 50, 60, 70, 80
]


def acquire_radialSin_test() -> None:
    print("\nRadial sin Zarr data\n---------------------\n")
    
    for i, multiplier in enumerate(frame_multipliers):
        if i == 5: break
        acquire_zarr.setup_camera(
            sim_type = "simulated: uniform random", 
            folder_path = abs_path_to_data + f"/acquire_data/radialSin{multiplier}.zarr", 
            max_frames = 64 * multiplier
            )
        print(f"Acquire Folder {multiplier}")
        acquire_zarr.setup_dimensions(
            x_array_size=1920,
            x_chunk_size=960,
            y_array_size=1080,
            y_chunk_size=540,
            t_array_size=0,
            t_chunk_size=64
            )
        acquire_zarr.create_zarr()
        zarr_libraries.folder_size(folder_path = abs_path_to_data + f"/acquire_data/radialSin{multiplier}.zarr/0")
        shutil.rmtree(abs_path_to_data + f"/acquire_data/radialSin{multiplier}.zarr")

    print("--------------------------------------------------------------\n\n")
    
#acquire_radialSin_test()


def tensorstore_radialSin_copy_test() -> None:
    print("\nRadial sin Zarr data\n---------------------\n")
    
    for index, multiplier in enumerate(frame_multipliers):
        print(f"TensorStore Folder {multiplier}")
        tensorstore_zarr.copy_zarr(
            source_path = abs_path_to_data + f"/tensorstore_data/radialSinTs{multiplier}.zarr", 
            result_path = abs_path_to_data + f"/tensorstore_data/radialSinTs{multiplier}.zarr"
            )
        zarr_libraries.folder_size(folder_path = abs_path_to_data + f"/tensorstore_data/radialSinTs{multiplier}.zarr")
        
    print("--------------------------------------------------------------\n\n")
    
#tensorstore_radialSin_copy_test()


def tensorstore_continuous_write_test(append_dim_size: int) -> None:
    print("\n\n--------Tensorstore Stress Test--------\n\n")
    file_sizes, bandwidths = tensorstore_zarr.continuous_write(
        result_path = abs_path_to_data + "/tensorstore_data/stressTest.zarr",
        append_dim_size = append_dim_size
        )
    print("--------------------------------------------------------------\n\n")
    plt.plot(file_sizes, bandwidths, label="tensorstore writes")
    
#tensorstore_continuous_write_test(30)


def tensorstore_continuous_append_test(append_dim_size: int) -> None:
    print("\n\n--------Tensorstore Stress Test--------\n\n")
    file_sizes, bandwidths = tensorstore_zarr.continuous_write_append(
        result_path = abs_path_to_data + "/tensorstore_data/stressTestAppend.zarr",
        append_dim_size = append_dim_size
        )
    print("--------------------------------------------------------------\n\n")
    plt.plot(file_sizes, bandwidths, label="tensorstore append")
    
tensorstore_continuous_append_test(200)


def zarr_python_continuous_write_test(append_dim_size: int) -> None:
    print("\n\n--------Zarr-Python Stress Test--------\n\n")
    file_sizes, bandwidths = zarr_python.continuous_write(
        result_path = abs_path_to_data + "/zarr_python_data/stressTest.zarr",
        append_dim_size = append_dim_size
        )
    print("--------------------------------------------------------------\n\n")
    plt.plot(file_sizes, bandwidths, label="zarr-python writes")
    
#zarr_python_continuous_write_test(30)


def zarr_python_continuous_append_test(append_dim_size: int) -> None:
    print("\n\n--------Zarr-Python Append Stress Test--------\n\n")
    file_sizes, bandwidths = zarr_python.continuous_write_append(
        result_path = abs_path_to_data + "/zarr_python_data/stressTestAppend.zarr",
        append_dim_size = append_dim_size
        )
    print("--------------------------------------------------------------\n\n")
    plt.plot(file_sizes, bandwidths, label="zarr-python append")
    
zarr_python_continuous_append_test(200)

plt.legend()
plt.xlabel("Data Size (GB)")
plt.ylabel("Bandwidth (GBps)")
plt.show()
