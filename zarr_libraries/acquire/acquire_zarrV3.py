# bug in the following code
# when ran it produces errors that seem to indicate that the config isn't being set properly
# code was referenced from the unit tests in the acquire-python repo
import acquire 
import napari
import dask.array as da
import os 
import shutil


if __name__ == "__main__":    
    runtime = acquire.Runtime()
    dm = runtime.device_manager()
    config = runtime.get_configuration()

    if config.video[0].storage.settings.filename in os.listdir("."):
        shutil.rmtree(config.video[0].storage.settings.filename)

    # config camera 
    config.video[0].camera.identifier = dm.select(acquire.DeviceKind.Camera, "simulated: radial sin")
    config.video[0].camera.settings.shape = (1920, 1080)
    config.video[0].camera.settings.exposure_time_us = 1e4
    config.video[0].camera.settings.pixel_type = acquire.SampleType.U8
    config.video[0].storage.identifier = dm.select(acquire.DeviceKind.Storage, "ZarrV3")
    config.video[0].storage.settings.filename = f"../example_data/radialSinV3.zarr"
    config.video[0].max_frame_count = 64

    # storage dimensions
    dimension_x = acquire.StorageDimension(
        name="x",
        kind="Space",
        array_size_px=1920,
        chunk_size_px=960,
        shard_size_chunks=2,
    )
    dimension_y = acquire.StorageDimension(
        name="y",
        kind="Space",
        array_size_px=1080,
        chunk_size_px=540,
        shard_size_chunks=2,
    )
    dimension_t = acquire.StorageDimension(
        name="t",
        kind="Time",
        array_size_px=0,
        chunk_size_px=64,
        shard_size_chunks=1,
    )
    config.video[0].storage.settings.acquisition_dimensions = [
        dimension_x,
        dimension_y,
        dimension_t,
    ]

    runtime.set_configuration(config)
    runtime.start()
    runtime.stop()

    data = da.from_zarr(config.video[0].storage.settings.filename, component="0")
    viewer = napari.view_image(data)
    napari.run()

    print("Finished with no issues")