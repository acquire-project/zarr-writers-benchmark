import acquire 
import time
import matplotlib.pyplot as plt
from zarr_libraries import folder_size
import shutil
from pathlib import Path

global runtime 
global dm
global config

runtime = acquire.Runtime()
dm = runtime.device_manager()
config = runtime.get_configuration()


def setup_camera(sim_type: str, folder_path: str, max_frames: int) -> None:    
    config.video[0].camera.identifier = dm.select(acquire.DeviceKind.Camera, sim_type)
    config.video[0].storage.identifier = dm.select(acquire.DeviceKind.Storage, "Zarr")
    config.video[0].storage.settings.filename = folder_path
    config.video[0].camera.settings.shape = (1920, 1080)
    config.video[0].camera.settings.exposure_time_us = 1e4
    config.video[0].camera.settings.pixel_type = acquire.SampleType.U8
    config.video[0].max_frame_count = max_frames  # set to 64 for example


def setup_dimensions(
    x_array_size: int, 
    x_chunk_size: int,
    y_array_size: int,
    y_chunk_size: int,
    t_array_size: int, 
    t_chunk_size: int,
) -> None:
    dimension_x = acquire.StorageDimension(
        name="x",
        kind="Space",
        array_size_px = x_array_size,  #set to 1920 for example
        chunk_size_px = x_chunk_size,  #set to 960 for example
        shard_size_chunks = 2,         #ignored for zarrV2 
    )
    dimension_y = acquire.StorageDimension(
        name="y",
        kind="Space",
        array_size_px = y_array_size,  #set to 1080 for example
        chunk_size_px = y_chunk_size,  #set to 540 for example
        shard_size_chunks = 2,         #ignored for zarrV2 
    )
    dimension_t = acquire.StorageDimension(
        name="t",
        kind="Time",
        array_size_px = t_array_size,  #set to 0
        chunk_size_px = t_chunk_size,  #set to 64 for example
        shard_size_chunks = 1,         #ignored for zarrV2 
    )
    config.video[0].storage.settings.acquisition_dimensions = [
        dimension_x,
        dimension_y,
        dimension_t,
    ]
    runtime.set_configuration(config)


def create_zarr() -> int:
    t = time.perf_counter()
    runtime.start()
    runtime.stop()
    total_time = time.perf_counter() - t
    print(f"Acquire -> creating zarr : {total_time} seconds")
    return total_time


def acquire_radialSin_test() -> None:
    abs_path_to_data = str((Path(__file__).parent / "../example_data/acquire_data").resolve()) 
    frame_multipliers = [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
        12, 13, 14, 15, 16, 17, 18, 19, 20,
        25, 30, 35, 40, 45, 50, 60, 70, 80, 100
    ]
    
    print("\nRadial sin Zarr data\n---------------------\n")
    file_sizes = []
    bandwidths = []
    
    for i, multiplier in enumerate(frame_multipliers):
        if 1 < i < len(frame_multipliers) - 1: continue
        setup_camera(
            sim_type = "simulated: uniform random", 
            folder_path = abs_path_to_data + f"/acquire_data/radialSin{multiplier}.zarr", 
            max_frames = 64 * multiplier
            )
        print(f"Acquire Folder {multiplier}")
        setup_dimensions(
            x_array_size=1920,    # set to 1920      
            x_chunk_size=960,     # set to 960 
            y_array_size=1080,    # set to 1080
            y_chunk_size=540,     # set to 540
            t_array_size=0,       # set to 0
            t_chunk_size=64       # set to 64
            )
        time = create_zarr()
        size = folder_size(folder_path = abs_path_to_data + f"/acquire_data/radialSin{multiplier}.zarr/0")
        shutil.rmtree(abs_path_to_data + f"/acquire_data/radialSin{multiplier}.zarr")
        file_sizes.append(size * 10**-9)
        bandwidths.append(size * 10 **-9 / time)
        
    print("--------------------------------------------------------------\n\n")
    plt.plot(file_sizes, bandwidths, label="Acquire Writes")