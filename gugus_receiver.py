from flask import Flask, request, jsonify
import time
import subprocess
import os
import threading
from openai import OpenAI
from gugus_flags import set_state_idle, set_state_listen
from datetime import datetime

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

FIRST_RUN_FILE = "/tmp/gugus_first_run.done"

def first_run_greeting():
    if not os.path.exists(FIRST_RUN_FILE):
        print(">>> FIRST RUN GREETING <<<", flush=True)
        
        text = "Hey!  Coucou Rose ! Je suis Gugusse, oui, je sais... c'est bizarre  un  robot poilu ! Je ne suis pas encore tout à fait au point mais je te promets que je vais faire de mon mieux! En tout cas je suis trop content d'être enfin en vie ! "
        
        try:
            # Génération TTS
            response = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="coral",
                input=text,
                response_format="wav",
            )

            audio_file = "/tmp/gugus_first.wav"
            with open(audio_file, "wb") as f:
                f.write(response.content)

            # Effet robot (même pipeline que d'habitude)
            robot_file = "/tmp/gugus_first_robot.wav"

            subprocess.run(
                ["sox", audio_file, robot_file, "pad", "2", "gain", "-n", "pitch", "180", "treble", "+4", "chorus", "0.5", "0.7", "20", "0.3", "0.2", "2", "-t"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            subprocess.Popen(
                ["paplay", robot_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        except Exception as e:
            print(f"Erreur first run: {e}", flush=True)

        # Marquer comme déjà exécuté
        open(FIRST_RUN_FILE, "w").close()
first_run_greeting()
last_wake = 0.0
COOLDOWN = 60.0
def alexa_reply(text: str, end_session: bool = False):
    response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": text},
            "shouldEndSession": end_session,
        },
    }

    if not end_session:
        response["response"]["reprompt"] = {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Je t'écoute."
            }
        }

    return response

def process_text_and_speak(text: str):
    print("### process_text_and_speak ###", flush=True)
    print(f"Texte reçu: {text}", flush=True)
    today_str = datetime.now().strftime("%d/%m/%Y")
    set_state_listen()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"Tu es Gugus, un petit robot sympathique. Réponds avec des phrases courtes. La date d'aujourd'hui est {today_str}. Si on te demande la date ou le jour, utilise cette information et n'invente pas." 
                },
                {
                    "role": "user",
                    "content": text
                },
            ],
        )

        answer = response.choices[0].message.content.strip()
        print(f"Réponse générée: {answer}", flush=True)
        audio_file = "/tmp/gugus_reply.wav"
        robot_file = "/tmp/gugus_reply_robot.wav"
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="coral",
            input=answer,
            response_format="wav",
        ) as audio_response:
            audio_response.stream_to_file(audio_file)
        subprocess.run(
        ["sox", audio_file, robot_file,"pad", "2", "gain", "-n", "pitch", "220", "treble", "+4", "chorus", "0.5", "0.7", "20", "0.3", "0.2", "2", "-t"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        loud_file = "/tmp/gugus_reply_loud.wav"

        subprocess.run(
            ["sox", audio_file, loud_file, "gain", "-n"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.Popen(
            ["paplay", robot_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    except Exception as e:
        print(f"Erreur dans process_text_and_speak: {e}", flush=True)
    finally:
        print(">>> PASSAGE EN IDLE <<<", flush=True)
        set_state_idle()

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

        subprocess.Popen(
            ["paplay", "/home/rose/gugus/sounds/wake.wav"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

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
    # Génération audio via OpenAI TTS
    audio_file = "/tmp/gugus_reply.wav"

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=answer
    ) as audio_response:
        audio_response.stream_to_file(audio_file)

    # Lecture du fichier audio
    subprocess.Popen(
        ["paplay", audio_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    set_state_idle()

    return jsonify({"ok": True, "answer": answer})

@app.post("/")
def alexa_webhook():
    try:
        data = request.get_json(force=True) or {}
        req = data.get("request") or {}
        req_type = req.get("type")

        print("=== ALEXA WEBHOOK ===", flush=True)
        print(f"req_type = {req_type}", flush=True)

        if req_type == "LaunchRequest":
            reply = alexa_reply("gugusse est prêt.", end_session=False)
            print(f"reply_text = {reply['response']['outputSpeech']['text']}", flush=True)
            return jsonify(reply)

        if req_type == "IntentRequest":
            intent = req.get("intent") or {}
            name = intent.get("name")
            print(f"intent_name = {name}", flush=True)

            if name == "TalkToGugusIntent":
                slots = intent.get("slots") or {}
                text = (((slots.get("text") or {}).get("value")) or "").strip()
                print(f"slot_text = {text}", flush=True)

                if not text:
                    reply = alexa_reply("Je n'ai pas compris. Répète ta phrase.")
                    print(f"reply_text = {reply['response']['outputSpeech']['text']}", flush=True)
                    return jsonify(reply)

                threading.Thread(
                    target=process_text_and_speak,
                    args=(text,),
                    daemon=True
                ).start()

                reply = alexa_reply("Ok.", end_session=True)
                print(f"reply_text = {reply['response']['outputSpeech']['text']}", flush=True)
                return jsonify(reply)

            if name in ("AMAZON.StopIntent", "AMAZON.CancelIntent"):
                reply = alexa_reply("D'accord.", end_session=True)
                print(f"reply_text = {reply['response']['outputSpeech']['text']}", flush=True)
                return jsonify(reply)

            reply = alexa_reply("Je n'ai pas compris.")
            print(f"reply_text = {reply['response']['outputSpeech']['text']}", flush=True)
            return jsonify(reply)

        if req_type == "SessionEndedRequest":
            reply = alexa_reply("À bientôt.", end_session=True)
            print(f"reply_text = {reply['response']['outputSpeech']['text']}", flush=True)
            return jsonify(reply)

        reply = alexa_reply("Requête inconnue.", end_session=True)
        print(f"reply_text = {reply['response']['outputSpeech']['text']}", flush=True)
        return jsonify(reply)

    except Exception as e:
        print(f"ERREUR alexa_webhook: {e}", flush=True)
        return jsonify(alexa_reply("Erreur interne.", end_session=True))
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
