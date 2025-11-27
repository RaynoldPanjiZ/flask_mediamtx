import subprocess
import datetime
import os
from config import STREAM_SOURCES, MEDIAMTX_HOST

recording_processes = {}

def start_record(channel):
    if channel not in STREAM_SOURCES:
        raise ValueError("Unknown channel")

    start_time = datetime.datetime.now()
    start_str = start_time.strftime("%Y%m%d-%H%M%S")

    filename = f"{channel}-{start_str}-ONGOING.mp4"
    filepath = f"recordings/{filename}"

    if not os.path.exists("recordings"):
        os.makedirs("recordings")

    # record from MediaMTX RTSP proxy
    src = f"rtsp://{MEDIAMTX_HOST}:8554/{channel}"

    cmd = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", src,
        "-c", "copy",
        filepath
    ]

    p = subprocess.Popen(cmd)
    recording_processes[channel] = (p, start_time, filepath)
    return filename


def stop_record(channel):
    if channel not in recording_processes:
        return None

    p, start_time, filepath = recording_processes[channel]

    p.terminate()
    p.wait()

    end_time = datetime.datetime.now()

    start_str = start_time.strftime("%Y%m%d-%H%M%S")
    end_str = end_time.strftime("%Y%m%d-%H%M%S")

    newname = filepath.replace("ONGOING", end_str)
    os.rename(filepath, newname)

    del recording_processes[channel]

    return os.path.basename(newname)


def list_recordings():
    return [f for f in os.listdir("recordings") if f.endswith(".mp4")]
