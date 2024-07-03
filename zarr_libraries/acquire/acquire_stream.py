## currently not working: unknown error ###
from pathlib import Path
import acquire
runtime = acquire.Runtime()

if __name__ == '__main__':
    # Initialize the device manager
    dm = runtime.device_manager()

    # Grab the current configuration
    config = runtime.get_configuration()

    # Select the uniform random camera as the video source
    config.video[0].camera.identifier = dm.select(acquire.DeviceKind.Camera, "simulated: radial sin")

    # Set the storage to trash to avoid saving the data
    config.video[0].storage.identifier = dm.select(acquire.DeviceKind.Storage, "Zarr")
    config.video[0].storage.settings.filename = str(Path(__file__).parent / "../example_data/stream.zarr")

    # Set the time for collecting data for a each frame
    config.video[0].camera.settings.exposure_time_us = 5e4  # 500 ms

    config.video[0].camera.settings.shape = (1920, 1080)

    # Set the max frame count to 100 frames
    config.video[0].max_frame_count = 100

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

    # Update the configuration with the chosen parameters
    config = runtime.set_configuration(config)

    # import napari and open a viewer to stream the data
    import napari
    viewer = napari.Viewer()

    import time
    from napari.qt.threading import thread_worker

    def update_layer(args) -> None:
        (new_image, stream_id) = args
        print(f"update layer: {new_image.shape=}, {stream_id=}")
        layer_key = f"Video {stream_id}"
        try:
            layer = viewer.layers[layer_key]
            layer._slice.image._view = new_image
            layer.data = new_image
            # you can use the private api with layer.events.set_data() to speed up by 1-2 ms/frame

        except KeyError:
            viewer.add_image(new_image, name=layer_key)

    @thread_worker(connect={"yielded": update_layer})
    def do_acquisition():
        time.sleep(5)
        runtime.start()

        nframes = [0, 0]
        stream_id = 0

        def is_not_done() -> bool:
            return (nframes[0] < config.video[0].max_frame_count) or (
                    nframes[1] < config.video[1].max_frame_count
                    )

        def next_frame(): #-> Optional[npt.NDArray[Any]]:
            """Get the next frame from the current stream."""
            if nframes[stream_id] < config.video[stream_id].max_frame_count:
                with runtime.get_available_data(stream_id) as packet:           ### important !!!! see test_zarr.py in acquire-python repo and search for "get_available_data" for proper implementation
                    n = packet.get_frame_count()
                    nframes[stream_id] += n
                    f = next(packet.frames())
                    return f.data().squeeze().copy()
            return None

        stream = 1
        # loop to continue to update the data in napari while acquisition is running
        while is_not_done():
            if (frame := next_frame()) is not None:
                yield frame, stream_id
            time.sleep(0.1)

    do_acquisition()

    napari.run()
