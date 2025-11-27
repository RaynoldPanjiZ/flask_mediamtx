# app.py

from flask import Flask, render_template, jsonify
import os
import stream_manager as sm
from record_manager import start_record, stop_record, list_recordings
from config import STREAM_SOURCES, MEDIAMTX_HOST

app = Flask(__name__)


# Jalankan stream hanya di child flask process
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    print("[INFO] Starting all streams...")
    sm.start_all()
else:
    print("[INFO] Flask reloader detected, do NOT start streams.")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/streams")
def streams():
    return render_template("stream.html",
                           streams=STREAM_SOURCES,
                           host=MEDIAMTX_HOST)


@app.route("/page")
def other_page():
    return render_template("page.html")


# ======================
# API ROUTES (RECORDING)
# ======================
@app.route("/api/record/start/<channel>")
def api_start(channel):
    file = start_record(channel)
    return jsonify({"status": "started", "file": file})

@app.route("/api/record/stop/<channel>")
def api_stop(channel):
    file = stop_record(channel)
    return jsonify({"status": "stopped", "file": file})

@app.route("/api/record/list")
def api_list():
    return jsonify(list_recordings())


if __name__ == "__main__":
    # debug=True tetap aman
    app.run(debug=True, threaded=True)
    # app.run(debug=True, threaded=True, use_reloader=False)
