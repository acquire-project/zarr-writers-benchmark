import acquire 
import time


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
