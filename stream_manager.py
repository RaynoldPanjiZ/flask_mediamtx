import subprocess
import threading
import atexit
import signal
import time
import os

from config import STREAM_SOURCES, FFMPEG_MODE

processes = []   # simpan semua proses ffmpeg
threads = []
running = True   # flag global


def build_ffmpeg_command(name, source):
    cmd = ["ffmpeg"]

    # ==================================================
    # INPUT SOURCES
    # ==================================================
    if source.startswith("rtsp://"):
        cmd += ["-rtsp_transport", "tcp", "-i", source]

    elif source.endswith(".mp4") or os.path.isfile(source):
        cmd += ["-re", "-stream_loop", "-1", "-i", source]

    elif source.startswith("/dev/video"):
        cmd += ["-f", "v4l2", "-input_format", "mjpeg", "-i", source]

    else:
        raise ValueError(f"Sumber tidak dikenal: {source}")

    # ==================================================
    # OUTPUT PRESET VARIATIONS
    # ==================================================

    # ───────────────────────────────────────────────
    # 1) MODE: COPY (PALING ringan)
    # ───────────────────────────────────────────────
    if FFMPEG_MODE == "copy":
        cmd += [
            "-c:v", "copy",
            "-an",
            "-f", "rtsp",
            "-rtsp_transport", "tcp",
            f"rtsp://localhost:8554/live/stream{name}"
        ]
        return cmd

    # ───────────────────────────────────────────────
    # 2) MODE: REENCODE Standar (kompatibel WebRTC)
    # ───────────────────────────────────────────────
    if FFMPEG_MODE == "reencode":
        cmd += [
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-tune", "zerolatency",
            "-profile:v", "baseline",
            "-level", "3.1",
            "-pix_fmt", "yuv420p",
            "-x264-params", "keyint=30:scenecut=0",

            "-c:a", "aac",
            "-b:a", "96k",
            "-ar", "44100",

            "-f", "rtsp",
            "-muxdelay", "0.1",
            f"rtsp://localhost:8554/live/stream{name}"
        ]
        return cmd

    # ───────────────────────────────────────────────
    # 3) MODE: ULTRA LOW LATENCY (paling smooth)
    # ───────────────────────────────────────────────
    if FFMPEG_MODE == "ultra":
        cmd += [
            "-fflags", "nobuffer",
            "-flags", "low_delay",
            "-strict", "experimental",
            "-analyzeduration", "0",
            "-probesize", "32",

            "-c:v", "libx264",
            "-tune", "zerolatency",
            "-preset", "ultrafast",
            "-profile:v", "baseline",
            "-level", "3.0",

            "-x264-params", "keyint=15:min-keyint=15:no-scenecut",

            "-pix_fmt", "yuv420p",

            "-an",

            "-f", "rtsp",
            "-muxdelay", "0.01",
            "-rtsp_transport", "tcp",
            f"rtsp://localhost:8554/live/stream{name}"
        ]
        return cmd

    # ───────────────────────────────────────────────
    # 4) MODE: ADAPTIVE (bitrate + fps otomatis)
    # ───────────────────────────────────────────────
    if FFMPEG_MODE == "adaptive":
        cmd += [
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-tune", "zerolatency",
            "-crf", "23",                 # kualitas adaptif
            "-maxrate", "3M",             # batasi bitrate
            "-bufsize", "6M",
            "-profile:v", "baseline",
            "-pix_fmt", "yuv420p",
            "-x264-params", "keyint=30",

            "-an",

            "-f", "rtsp",
            "-rtsp_transport", "tcp",
            f"rtsp://localhost:8554/live/stream{name}"
        ]
        return cmd

    # ───────────────────────────────────────────────
    # 5) MODE: FORCE ENCODE (hard reencode untuk source buruk)
    # ───────────────────────────────────────────────
    if FFMPEG_MODE == "force":
        cmd += [
            "-vf", "fps=25",
            "-c:v", "libx264",
            "-preset", "faster",
            "-tune", "zerolatency",
            "-profile:v", "baseline",

            "-pix_fmt", "yuv420p",

            "-c:a", "aac",
            "-ar", "44100",
            "-b:a", "96k",

            "-f", "rtsp",
            "-rtsp_transport", "tcp",
            f"rtsp://localhost:8554/live/stream{name}"
        ]
        return cmd

    # Default fallback
    raise ValueError(f"Mode FFMPEG tidak valid: {FFMPEG_MODE}")


def process_stream(name, source):
    global running
    cmd = build_ffmpeg_command(name, source)
    print(f"[STREAM] Starting FFmpeg for {name}")

    p = subprocess.Popen(
        cmd,
        # stdout=subprocess.PIPE,
        # stderr=subprocess.PIPE,
        # stdin=subprocess.DEVNULL,
        # text=True,
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
