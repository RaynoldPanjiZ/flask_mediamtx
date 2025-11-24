# app.py

from flask import Flask, render_template
import os
import stream_manager as sm
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


if __name__ == "__main__":
    # debug=True tetap aman
    app.run(debug=True, threaded=True)
    # app.run(debug=True, threaded=True, use_reloader=False)
