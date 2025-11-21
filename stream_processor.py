import cv2
import subprocess
import threading

MEDIAMTX_IP = "192.168.45.39"

sources = {
    # "mp41": "static/video/0423.mp4",
    # "cam1": "rtsp://192.168.1.11:8554/test",
    "cam1": "rtsp://admin:aery2021!@192.168.45.167:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif"
}

# def process_stream(name, source):
#     print(f"[INFO] Starting processor for {name}")

#     cap = cv2.VideoCapture(source)
#     if not cap.isOpened():
#         print(f"[ERROR] Cannot open {source}")
#         return

#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     if fps <= 0: fps = 25

#     # FFmpeg menerima RAWVIDEO dari stdin
#     ffmpeg = subprocess.Popen([
#         "ffmpeg",
#         "-re",
#         "-f", "rawvideo",
#         "-pix_fmt", "bgr24",
#         "-s", f"{width}x{height}",
#         "-r", str(fps),
#         "-i", "-",

#         "-c:v", "libx264",
#         "-pix_fmt", "yuv420p",
#         "-preset", "veryfast",
#         "-tune", "zerolatency",
#         "-f", "rtsp",
#         f"rtsp://localhost:8554/{name}",
#     ], stdin=subprocess.PIPE)

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print(f"[INFO] End of source: {source}")
#             break

#         # =======================
#         #    FRAME PROCESSING
#         # =======================
#         cv2.rectangle(frame, (50,50), (250,200), (0,255,0), 3)
#         cv2.putText(frame, f"STREAM: {name}", (50,40),
#             cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

#         ffmpeg.stdin.write(frame.tobytes())

def process_stream(name, source):
    print(f"[INFO] Starting processor for {name}")

    # FFmpeg menerima RAWVIDEO dari stdin
    cmd = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-itsoffset", "2",
        "-i", source,

        "-c:v", "copy",
        "-an",
        "-f", "rtsp",
        f"rtsp://localhost:8554/{name}",
    ]

    # cmd = [
    #     "ffmpeg",
    #     "-rtsp_transport", "tcp",
    #     "-i", source,

    #     "-c:v", "libx264",
    #     "-preset", "veryfast",
    #     "-tune", "zerolatency",
    #     "-pix_fmt", "yuv420p",

    #     "-f", "rtsp",
    #     f"rtsp://localhost:8554/{name}",
    # ]

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
