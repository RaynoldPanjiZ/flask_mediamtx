from flask import Flask, render_template

app = Flask(__name__)

# MEDIAMTX_HOST = "192.168.45.39"  # <-- IP server MediaMTX
MEDIAMTX_HOST = "192.168.1.12"

@app.route("/")
def index():
    return render_template("index.html", host=MEDIAMTX_HOST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
