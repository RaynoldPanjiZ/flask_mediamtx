MEDIAMTX_HOST = "192.168.45.39"
# MEDIAMTX_HOST = "192.168.1.12"

STREAM_SOURCES = {
    # "mp41": "static/video/0423.mp4",
    # # "mp42": "static/video/video1a.mp4",
    # "mp43": "static/video/0423.mp4",
    # # "cam1": "rtsp://192.168.1.11:8554/test",
    "cam1": "rtsp://admin:aery2021!@192.168.45.167:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif",
    "cam2": "rtsp://admin:aery2021!@192.168.45.167:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif",
    "cam3": "rtsp://admin:aery2021!@192.168.45.167:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif",
    "cam4": "rtsp://admin:aery2021!@192.168.45.167:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif"
}

FFMPEG_MODE = "copy"          # without re-encode
# FFMPEG_MODE = "reencode"    # reencode standar
# FFMPEG_MODE = "ultra"       # ultrafast + zerolatency
# FFMPEG_MODE = "adaptive"    # hlr + dynamic gop
# FFMPEG_MODE = "force"       # force keyframe every 2 seconds, always reencode