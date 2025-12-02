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

    # INPUT Source setup (rtsp, mp4, v4l2, etc)
    if source.startswith("rtsp://"):
        # cmd += ["-rtsp_transport", "tcp", "-i", source]
        cmd += [
            "-rtsp_transport", "tcp",
            "-fflags", "+genpts",
            "-use_wallclock_as_timestamps", "1",
            "-i", source
        ]
    elif source.endswith(".mp4") or os.path.isfile(source):
        cmd += ["-re", "-stream_loop", "-1", "-i", source]
    elif source.startswith("/dev/video"):
        cmd += ["-f", "v4l2", "-i", source]
    else:
        raise ValueError(f"Sumber tidak dikenal: {source}")

    # OUTPUT Transcode to MediaMTX RTSP
    cmd += [
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",
        "-crf", "24",           # sedikit lebih ringan
        "-g", "25",
        "-keyint_min", "25",
        "-pix_fmt", "yuv420p",

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
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        text=True,
        bufsize=1
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
        t = threading.Thread(
            target=process_stream,
            args=(name, src),
            daemon=True  # <── Fix: daemon thread
        )
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
