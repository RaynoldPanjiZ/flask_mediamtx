import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

import threading
import time
import atexit
import signal
import os

from config import STREAM_SOURCES

Gst.init(None)

running = True
pipelines = {}


def build_gst_pipeline(name, source):
    """Membangun pipeline GStreamer sesuai tipe input."""

    if source.startswith("rtsp://"):
        # RTSP input → decode → encode → RTSP
        pipeline_str = f"""
            rtspsrc location={source} latency=0 !
            rtph264depay ! h264parse ! avdec_h264 !
            videoconvert !
            x264enc speed-preset=ultrafast tune=zerolatency !
            rtspclientsink location=rtsp://localhost:8554/{name}
        """

    elif source.endswith(".mp4") or os.path.isfile(source):
        pipeline_str = f"""
            filesrc location={source} !
            qtdemux ! h264parse ! avdec_h264 !
            videoconvert !
            x264enc speed-preset=ultrafast tune=zerolatency !
            rtspclientsink location=rtsp://localhost:8554/{name}
        """

    elif source.startswith("/dev/video"):
        pipeline_str = f"""
            v4l2src device={source} !
            videoconvert !
            x264enc speed-preset=ultrafast tune=zerolatency !
            rtspclientsink location=rtsp://localhost:8554/{name}
        """

    else:
        raise ValueError(f"Sumber tidak dikenal: {source}")

    return pipeline_str


def start_stream(name, source):
    global running

    pipeline_str = build_gst_pipeline(name, source)
    pipeline = Gst.parse_launch(pipeline_str)
    pipelines[name] = pipeline

    pipeline.set_state(Gst.State.PLAYING)
    print(f"[STREAM] Started GStreamer pipeline for: {name}")

    # Loop sampai shutdown
    while running:
        time.sleep(0.3)

    print(f"[STREAM] Stopping pipeline: {name}")
    pipeline.set_state(Gst.State.NULL)


def start_all():
    for name, src in STREAM_SOURCES.items():
        t = threading.Thread(target=start_stream, args=(name, src), daemon=True)
        t.start()


def stop_all():
    global running
    running = False

    print("\n[STOP] Stopping all pipelines...")

    for name, p in pipelines.items():
        try:
            p.set_state(Gst.State.NULL)
        except:
            pass

    print("[STOP] All pipelines stopped.")


# Graceful shutdown
atexit.register(stop_all)
signal.signal(signal.SIGINT, lambda s, f: exit(0))
signal.signal(signal.SIGTERM, lambda s, f: exit(0))
