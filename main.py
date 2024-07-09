from pathlib import Path
import shutil 
import matplotlib.pyplot as plt 
import zarr_libraries
from zarr_libraries.tensorstore import tensorstore_zarr
from zarr_libraries.acquire import acquire_zarr
from zarr_libraries.zarr_python import zarr_python
from zarr_libraries.ome_ngff import ome_zarr


abs_path_to_data = str(Path(__file__).parent / "zarr_libraries/example_data/")
frame_multipliers = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
    12, 13, 14, 15, 16, 17, 18, 19, 20,
    25, 30, 35, 40, 45, 50, 60, 70, 80, 100
]


def acquire_radialSin_test() -> None:
    print("\nRadial sin Zarr data\n---------------------\n")
    file_sizes = []
    bandwidths = []
    
    for i, multiplier in enumerate(frame_multipliers):
        if 1 < i < len(frame_multipliers) - 1: continue
        acquire_zarr.setup_camera(
            sim_type = "simulated: uniform random", 
            folder_path = abs_path_to_data + f"/acquire_data/radialSin{multiplier}.zarr", 
            max_frames = 64 * multiplier
            )
        print(f"Acquire Folder {multiplier}")
        acquire_zarr.setup_dimensions(
            x_array_size=1920,    # set to 1920      
            x_chunk_size=960,     # set to 960 
            y_array_size=1080,    # set to 1080
            y_chunk_size=540,     # set to 540
            t_array_size=0,       # set to 0
            t_chunk_size=64       # set to 64
            )
        time = acquire_zarr.create_zarr()
        size = zarr_libraries.folder_size(folder_path = abs_path_to_data + f"/acquire_data/radialSin{multiplier}.zarr/0")
        shutil.rmtree(abs_path_to_data + f"/acquire_data/radialSin{multiplier}.zarr")
        file_sizes.append(size * 10**-9)
        bandwidths.append(size * 10 **-9 / time)
        
    print("--------------------------------------------------------------\n\n")
    plt.plot(file_sizes, bandwidths, label="Acquire Writes")


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


def tensorstore_continuous_write_test(append_dim_size: int) -> None:
    print("\n\n--------Tensorstore Stress Test--------\n\n")
    file_sizes, bandwidths = tensorstore_zarr.continuous_write(
        result_path = abs_path_to_data + "/tensorstore_data/stressTest.zarr",
        append_dim_size = append_dim_size
        )
    print("--------------------------------------------------------------\n\n")
    plt.plot(file_sizes, bandwidths, label="tensorstore writes")


def tensorstore_continuous_append_test(append_dim_size: int) -> None:
    print("\n\n--------Tensorstore Stress Test--------\n\n")
    file_sizes, bandwidths = tensorstore_zarr.continuous_write_append(
        result_path = abs_path_to_data + "/tensorstore_data/stressTestAppend.zarr",
        append_dim_size = append_dim_size
        )
    print("--------------------------------------------------------------\n\n")
    plt.plot(file_sizes, bandwidths, label="tensorstore append")


def zarr_python_continuous_write_test(append_dim_size: int) -> None:
    print("\n\n--------Zarr-Python Stress Test--------\n\n")
    file_sizes, bandwidths = zarr_python.continuous_write(
        result_path = abs_path_to_data + "/zarr_python_data/stressTest.zarr",
        append_dim_size = append_dim_size
        )
    print("--------------------------------------------------------------\n\n")
    plt.plot(file_sizes, bandwidths, label="zarr-python writes")


def zarr_python_continuous_append_test(append_dim_size: int) -> None:
    print("\n\n--------Zarr-Python Append Stress Test--------\n\n")
    file_sizes, bandwidths = zarr_python.continuous_write_append(
        result_path = abs_path_to_data + "/zarr_python_data/stressTestAppend.zarr",
        append_dim_size = append_dim_size
        )
    print("--------------------------------------------------------------\n\n")
    plt.plot(file_sizes, bandwidths, label="zarr-python append")


def ome_zarr_continuous_write_test(append_dim_size: int) -> None:
    print("\n\n--------OME-Zarr Stress Test--------\n\n")
    file_sizes, bandwidths = ome_zarr.continuous_write(
        result_path = abs_path_to_data + "/ome_zarr_data/stressTest.zarr",
        append_dim_size = append_dim_size
        )
    print("--------------------------------------------------------------\n\n")
    plt.plot(file_sizes, bandwidths, label="ome-zarr writes")
    
    
def ome_zarr_continuous_append_test(append_dim_size: int) -> None:
    print("\n\n--------Ome-Zarr Append Stress Test--------\n\n")
    file_sizes, bandwidths = ome_zarr.continuous_write_append(
        result_path = abs_path_to_data + "/ome_zarr_data/stressTestAppend.zarr",
        append_dim_size = append_dim_size
        )
    print("--------------------------------------------------------------\n\n")
    plt.plot(file_sizes, bandwidths, label="ome-zarr append")


if __name__ == "__main__":
    '''
    Append Tests:
    - These tests benchmark the continuous appending to a single zarr folder 
    - The append dimension size passed in equates to ~26 gigs of data
    '''
    #tensorstore_continuous_append_test(append_dim_size=200)
    #zarr_python_continuous_append_test(append_dim_size=200) 
    ome_zarr_continuous_append_test(append_dim_size=12) # at around 17 gigs of data ome-zarr throws an error, 12 is right before that happens
   
    '''
    Continuous write tests:
    - These tests benchmark the creation of many increasingly large zarr folders
    '''
    #acquire_radialSin_test()
    #tensorstore_radialSin_copy_test()
    #tensorstore_continuous_write_test(append_dim_size=30)
    #zarr_python_continuous_write_test(append_dim_size=30)
    #ome_zarr_continuous_write_test(append_dim_size=30)
   
    plt.legend()
    plt.xlabel("Data Size (GB)")
    plt.ylabel("Bandwidth (GBps)")
    plt.show()
