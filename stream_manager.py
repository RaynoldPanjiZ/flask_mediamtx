import subprocess
import threading
import os
from config import STREAM_SOURCES

stream_processes = {}      # name → subprocess.Popen
stream_threads = {}        # name → thread obj


def build_ffmpeg_cmd(name, source):
    cmd = ["ffmpeg"]

    # INPUT SOURCES
    if source.startswith("rtsp://"):
        cmd += ["-rtsp_transport", "tcp", "-i", source]

    elif source.endswith(".mp4") or os.path.isfile(source):
        cmd += ["-re", "-stream_loop", "-1", "-i", source]

    elif source.startswith("/dev/video"):
        cmd += ["-f", "v4l2", "-i", source]

    else:
        raise ValueError(f"Sumber tidak dikenal: {source}")

    # OUTPUT KE MEDIAMTX (RTSP → WebRTC/HLS otomatis)
    cmd += [
        "-c:v", "copy",
        "-an",
        "-f", "rtsp",
        f"rtsp://localhost:8554/{name}"
    ]

    return cmd


def stream_worker(name, source):
    cmd = build_ffmpeg_cmd(name, source)
    proc = subprocess.Popen(cmd)
    stream_processes[name] = proc
    proc.wait()
    stream_processes.pop(name, None)


# === PUBLIC FUNCTIONS =====================================

def start_stream(name):
    """Start stream jika belum berjalan."""
    if name in stream_processes:
        return False  # sudah berjalan

    if name not in STREAM_SOURCES:
        return False

    thread = threading.Thread(
        target=stream_worker,
        args=(name, STREAM_SOURCES[name]),
        daemon=True
    )
    thread.start()
    stream_threads[name] = thread
    return True


def stop_stream(name):
    """Stop FFmpeg process."""
    if name not in stream_processes:
        return False

    proc = stream_processes[name]
    proc.terminate()
    proc.kill()
    return True


def is_running(name):
    return name in stream_processes
