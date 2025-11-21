from flask import Flask, render_template, redirect, url_for
from config import STREAM_SOURCES, MEDIAMTX_HOST
import stream_manager as sm

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("server.html",
                           streams=STREAM_SOURCES,
                           is_running=sm.is_running)


@app.route("/client/<name>")
def client(name):
    if name not in STREAM_SOURCES:
        return "Stream not found", 404
    return render_template("client.html",
                           name=name,
                           mtx_host=MEDIAMTX_HOST)


@app.route("/server/<name>")
def server(name):
    if name not in STREAM_SOURCES:
        return "Stream not found", 404
    return render_template("server.html",
                           name=name,
                           streams=STREAM_SOURCES,
                           is_running=sm.is_running)


# ==== STREAM CONTROL ==========================

@app.route("/start/<name>")
def start(name):
    sm.start_stream(name)
    return redirect(url_for("home"))


@app.route("/stop/<name>")
def stop(name):
    sm.stop_stream(name)
    return redirect(url_for("home"))


# ==========================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
