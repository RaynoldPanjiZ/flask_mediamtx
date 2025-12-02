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
        cmd += ["-rtsp_transport", "tcp", "-i", source]
    elif source.endswith(".mp4") or os.path.isfile(source):
        cmd += ["-re", "-stream_loop", "-1", "-i", source]
    elif source.startswith("/dev/video"):
        cmd += ["-f", "v4l2", "-i", source]
    else:
        raise ValueError(f"Sumber tidak dikenal: {source}")

    # OUTPUT Transcode to MediaMTX RTSP
    cmd += [
        "-fflags", "+genpts",            # perbaiki PTS terus menerus
        "-use_wallclock_as_timestamps", "1",
        "-pkt_size", "1300",
        "-flush_packets", "1",

        "-bsf:v", "h264_metadata=video_full_range_flag=1",
        "-maxrate", "5M",
        "-bufsize", "5M",

        "-max_interleave_delta", "0",   # cegah ffmpeg 'menumpuk' packet
        "-muxdelay", "0",               # paksa RTP realtime
        "-muxpreload", "0",             # no buffering

        "-vsync", "1",                  # stabilisasi frame pacing
        "-copyts",                      # tetap copy timestamps
        "-start_at_zero",               # mulai dari 0

        "-c:v", "copy",                 # tetap tanpa re-encode
        # "-c:v", "libx264", 
        # "-preset", "ultrafast", 
        # "-tune", "zerolatency",
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
