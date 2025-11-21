import cv2
import subprocess
import threading
import os

MEDIAMTX_IP = "192.168.45.39"

sources = {
    # "mp41": "static/video/0423.mp4",
    # "cam1": "rtsp://192.168.1.11:8554/test",
    "cam1": "rtsp://admin:aery2021!@192.168.45.167:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif"
}

def build_ffmpeg_command(name, source):
    cmd = ["ffmpeg"]

    # ================================
    # 1. Video source input
    # ================================
    if source.startswith("rtsp://"):
        # RTSP CAMERA
        cmd += [
            "-rtsp_transport", "tcp",    # use TCP for RTSP
            "-i", source
        ]
    elif source.endswith(".mp4") or os.path.isfile(source):
        # MP4 FILE
        cmd += [
            "-re",                      # real-time playback
            "-stream_loop", "-1",              # loop indefinitely
            "-i", source
        ]
    elif source.startswith("/dev/video"):
        # WEBCAM (v4l2)
        cmd += [
            "-f", "v4l2",
            "-i", source
        ]

    else:
        raise ValueError(f"Tipe sumber tidak dikenal: {source}")

    # ================================
    # 2. MediaMTX output
    # ================================
    # MediaMTX will handle:
    #   /{name} (RTSP)
    #   /{name} (WebRTC)
    #   /{name}/index.m3u8 (HLS)
    cmd += [
        "-c:v", "copy",     # copy video codec
        "-c:a", "copy",     # copy audio codec
        "-an",
        "-f", "rtsp",
        f"rtsp://localhost:8554/{name}"
    ]

    return cmd

def process_stream(name, source):
    print(f"[INFO] Starting processor for {name}")

    # FFmpeg menerima RAWVIDEO dari stdin
    # cmd = [
    #     "ffmpeg",
    #     "-rtsp_transport", "tcp",
    #     "-itsoffset", "2",
    #     "-i", source,

    #     "-c:v", "copy",
    #     "-an",
    #     "-f", "rtsp",
    #     f"rtsp://localhost:8554/{name}",
    # ]

    cmd = build_ffmpeg_command(name, source)

    process = subprocess.Popen(cmd)
    process.wait()

def start_all_streams():
    for name, src in sources.items():
        threading.Thread(
            target=process_stream,
            args=(name, src),
            daemon=True
        ).start()

if __name__ == "__main__":
    start_all_streams()
    print("[INFO] streaming..")
    while True:
        pass
