from flask import Flask, request, jsonify
import time
import subprocess
from gugus_flags import set_state_idle, set_state_listen

app = Flask(__name__)
last_wake = 0.0
COOLDOWN = 60.0

@app.post("/event")
def event():
    global last_wake
    data = request.get_json(force=True) or {}
    if data.get("event") == "wake":
        now = time.time()
        if now - last_wake < COOLDOWN:
            return jsonify({"ok": True, "ignored": True})
        last_wake = now
        set_state_listen()
        subprocess.Popen(["paplay", "/home/rose/gugus/sounds/wake.wav"],
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.0)
        set_state_idle()
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 400

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
