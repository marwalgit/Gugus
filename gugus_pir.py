import time
import os
import json
import urllib.request
import RPi.GPIO as GPIO
from gugus_flags import set_state_sleep

PIR_PIN = 17
SLEEP_FLAG = "/tmp/gugus_sleep.on"


def send_wake():
    url = "http://127.0.0.1:8080/event"
    payload = json.dumps({"event": "wake"}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=2):
            pass
    except Exception as e:
        print("⚠️ Wake non envoyé:", e)


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIR_PIN, GPIO.IN)

    print("🕵️ PIR Gugus actif — Gugus dort")
    open(SLEEP_FLAG, "w").close()

    presence_start = None
    DETECTION_TIME = 1.0  # secondes de mouvement continu avant de valider une présence

    COOLDOWN = 15         # sécurité anti-spam (même si awake gère déjà)
    last_trigger = 0.0

    awake = False         # True après un wake : on n'en renvoie plus tant qu'on est "présent"
    last_motion = 0.0     # dernière fois où le PIR a vu du mouvement
    ABSENCE_TIME = 60.0   # secondes sans mouvement pour considérer "parti" (à ajuster)

    try:
        while True:
            now = time.time()
            motion = GPIO.input(PIR_PIN)

            if motion:
                last_motion = now

            if motion:
                if presence_start is None:
                    presence_start = now
                elif now - presence_start >= DETECTION_TIME:
                    if (now - last_trigger > COOLDOWN) and (not awake):
                        print("✨ Présence détectée → Réveil de Gugus")
                        send_wake()
                        last_trigger = now
                        awake = True
            else:
                presence_start = None

            # Si plus de mouvement depuis longtemps, on autorise un nouveau wake plus tard
            if awake and (now - last_motion > ABSENCE_TIME):
                print("💤 Absence détectée → Gugus s'endort (mode sleep)")
                set_state_sleep()
                awake = False
            time.sleep(0.1)

    except KeyboardInterrupt:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
