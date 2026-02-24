# GUGUS – PROJECT STATE
Last update: 2026-02-24
Version: V1 Stable – Repo Migrated

------------------------------------------------------------
HARDWARE
------------------------------------------------------------

- Raspberry Pi Zero 2 W
- Servo head controlled via pigpio
- PIR motion sensor
- OLED display (eyes)
- Audio output: Echo Pop (Bluetooth A2DP sink)
- OS audio system: PipeWire
- No local microphone connected to Pi

------------------------------------------------------------
SOFTWARE ARCHITECTURE
------------------------------------------------------------

Official source directory:
/home/rose/gugus/

All systemd services now execute code from this directory.

Services:

- gugus-receiver.service
  → /home/rose/gugus/gugus_receiver.py
  → Flask server (localhost:8080)
  → Central orchestration

- gugus-head.service
  → /home/rose/gugus/head_flags.py
  → Uses head_controller.py

- gugus-pir.service
  → /home/rose/gugus/gugus_pir.py
  → Triggers wake/sleep states

- gugus-eyes.service
  → /home/rose/gugus/eyes_test.py
  → OLED control

Sound assets:
- /home/rose/gugus/sounds/wake.wav

------------------------------------------------------------
BOOT BEHAVIOR
------------------------------------------------------------

At boot:
- sleep mode ON
- listen/thinking OFF
- All services start automatically via systemd
- Idle head wander active (3–10s, 1450–1550µs validated)

------------------------------------------------------------
AUDIO STATUS
------------------------------------------------------------

Output:
- bluez_output (Echo Pop Bluetooth) → OK

Input:
- No usable microphone detected via pactl
- Voice input planned via Alexa Skill → webhook → receiver

------------------------------------------------------------
GIT WORKFLOW
------------------------------------------------------------

Local working directory:
- /home/rose/gugus

Workflow:
1. Modify file
2. Test via systemctl restart <service>
3. Validate stability
4. git add
5. git commit
6. git push

GitHub is:
- Backup
- History
- Remote mirror

Robot does NOT execute code from Internet.

------------------------------------------------------------
CURRENT OBJECTIVE
------------------------------------------------------------

Migration completed.
Next phase:
Voice interface:
Alexa → Receiver → ChatGPT → TTS → Echo Pop

------------------------------------------------------------
END OF STATE
------------------------------------------------------------
