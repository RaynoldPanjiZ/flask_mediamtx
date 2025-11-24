import subprocess
import threading
import atexit
import signal
import time
import os

from config import STREAM_SOURCES

processes = []   # simpan semua proses ffmpeg
threads = []
running = True   # flag global


def build_ffmpeg_command(name, source):
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


def process_stream(name, source):
    global running
    cmd = build_ffmpeg_command(name, source)

    print(f"[STREAM] Starting FFmpeg for {name}")

    p = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT
    )
    processes.append(p)

    # tunggu sampai stop sinyal
    while running and p.poll() is None:
        time.sleep(0.5)

    # stop FFmpeg
    if p.poll() is None:
        print(f"[STREAM] Terminating FFmpeg: {name}")
        p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print(f"[STREAM] Killing FFmpeg: {name}")
            p.kill()


def start_all():
    for name, src in STREAM_SOURCES.items():
        t = threading.Thread(target=process_stream, args=(name, src))
        t.start()
        threads.append(t)


# ===========================================================
# CLEAN SHUTDOWN HANDLER
# ===========================================================

def stop_all():
    global running
    running = False

    print("\n[STOP] Stopping all FFmpeg processes...")

    # terminate all processes
    for p in processes:
        if p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                p.kill()

    print("[STOP] All FFmpeg processes stopped.")


# Register shutdown cleanup
atexit.register(stop_all)
signal.signal(signal.SIGINT, lambda s, f: exit(0))
signal.signal(signal.SIGTERM, lambda s, f: exit(0))
