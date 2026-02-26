from flask import Flask, request, jsonify
import time
import subprocess
import os
from openai import OpenAI
from gugus_flags import set_state_idle, set_state_listen

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
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
@app.post("/say")
def say():
    data = request.get_json(force=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"ok": False, "error": "missing text"}), 400

    set_state_listen()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Tu es Gugus, un petit robot sympathique."},
            {"role": "user", "content": text}
        ]
    )

    answer = response.choices[0].message.content.strip()

    set_state_idle()

    return jsonify({"ok": True, "answer": answer})
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
