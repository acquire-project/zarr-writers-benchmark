# Code below is work in progress which is why it is commented off for now 
# there are 2 approaches and both give me errors
# 1) 1st approach comes from the livestream_napari.py file in acquire-docs repo
# 2) 2nd approach comes from the __init__.py file in acquire-python repo


# 1st approach 
'''
import acquire
runtime = acquire.Runtime()

# Initialize the device manager
dm = runtime.device_manager()

# Grab the current configuration
config = runtime.get_configuration()

# Select the uniform random camera as the video source
config.video[0].camera.identifier = dm.select(acquire.DeviceKind.Camera, "simulated: radial sin")

# Set the storage to trash to avoid saving the data
config.video[0].storage.identifier = dm.select(acquire.DeviceKind.Storage, "Zarr")
config.video[0].storage.settings.filename = f"../example_data/stream.zarr"

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
            if packet := runtime.get_available_data(stream_id):
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
'''


# 2nd approach 
'''
from acquire import *
import logging
from napari import Viewer
import time
from typing import (
    TYPE_CHECKING,
    Any,
    Generator,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)
import numpy.typing as npt
import os
import shutil

runtime = Runtime()
config = runtime.get_configuration()

if config.video[0].storage.settings.filename in os.listdir("."):
    shutil.rmtree(config.video[0].storage.settings.filename)

viewer = Viewer()
stream_count = 1
frame_count = 100

def setup_stream(runtime: Runtime, frame_count: int) -> Properties:
    dm = runtime.device_manager()
    p = runtime.get_configuration()

    cameras = [
        d.name
        for d in dm.devices()
        if (d.kind == DeviceKind.Camera) and ("C15440" in d.name)
    ]
    logging.warning(f"Cameras {cameras}")

    if len(cameras) == 0:
        cameras = ["simulated: radial sin"]

    p.video[0].camera.identifier = dm.select(DeviceKind.Camera, cameras[0])

    p.video[0].camera.identifier = dm.select(DeviceKind.Camera, "simulated: radial sin")
    p.video[0].storage.identifier = dm.select(DeviceKind.Storage, "Zarr")
    p.video[0].storage.settings.filename = f"../example_data/stream.zarr"
    p.video[0].camera.settings.binning = 1
    p.video[0].camera.settings.shape = (64, 64)
    p.video[0].camera.settings.pixel_type = SampleType.U16
    p.video[0].max_frame_count = frame_count
    p.video[0].frame_average_count = 0  # disables
    
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
    p.video[0].storage.settings.acquisition_dimensions = [
        dimension_x,
        dimension_y,
        dimension_t,
    ]

    return p

def start_stream() -> None:
    """Napari dock-widget plugin entry-point

    This instances a magicgui dock widget that streams video to a layer.
    """
    from napari.qt.threading import thread_worker  # type: ignore
    from numpy import cumsum, histogram, where

    update_times: List[float] = []

    def update_layer(args: Tuple[npt.NDArray[Any], int]) -> None:
        (new_image, stream_id) = args
        layer_key = f"Video {stream_id}"
        try:
            clock = time.time()

            layer = viewer.layers[layer_key]
            layer._slice.image._view = new_image
            layer.events.set_data()
            # layer.data=new_image # public api adds another 1-2 ms/frame

            elapsed = time.time() - clock
            update_times.append(elapsed)
            logging.info(f"UPDATED LAYER {layer_key} in {elapsed} s")
        except KeyError:
            # (nclack) This takes ~ 60ms for 630x480 the one time I measured it
            viewer.add_image(new_image, name=layer_key)

    @thread_worker(connect={"yielded": update_layer})
    def do_acquisition() -> (
        Generator[Tuple[npt.NDArray[Any], int], None, None]
    ):
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)

        runtime = acquire.Runtime()

        p = setup_stream(runtime, frame_count)

        p = runtime.set_configuration(p)

        runtime.start()

        nframes = [0, 0]
        stream_id = 0

        def is_not_done() -> bool:
            return (nframes[0] < p.video[0].max_frame_count) or (
                nframes[1] < p.video[1].max_frame_count
            )

        def next_frame() -> Optional[npt.NDArray[Any]]:
            """Get the next frame from the current stream."""
            if nframes[stream_id] < p.video[stream_id].max_frame_count:
                with runtime.get_available_data(stream_id) as packet:
                    n = packet.get_frame_count()
                    nframes[stream_id] += n
                    logging.info(
                        f"[stream {stream_id}] frame count: {nframes}"
                    )
                    f = next(packet.frames())
                    logging.debug(
                        f"stream {stream_id} frame {f.metadata().frame_id}"
                    )
                    return f.data().squeeze().copy()
            return None

        while is_not_done():  # runtime.get_state()==DeviceState.Running:
            clock = time.time()
            if (frame := next_frame()) is not None:
                yield frame, stream_id
            stream_id = (stream_id + 1) % stream_count
            elapsed = time.time() - clock
            time.sleep(max(0, 0.03 - elapsed))
        logging.info("stopping")

        counts, bins = histogram(update_times)
        p50 = bins[where(cumsum(counts) >= 0.5 * len(update_times))[0][0]]
        p90 = bins[where(cumsum(counts) >= 0.9 * len(update_times))[0][0]]
        logging.info(f"Update times - median: {p50*1e3} ms  90%<{p90*1e3} ms")

        runtime.stop()
        logging.info("STOPPED")

    viewer.layers.clear()
    do_acquisition()
    
start_stream()
'''