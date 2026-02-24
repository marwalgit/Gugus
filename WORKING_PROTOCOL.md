# GUGUS – WORKING PROTOCOL

------------------------------------------------------------
CORE PHILOSOPHY
------------------------------------------------------------

Gugus is built step by step.
One change at a time.
One validation at a time.

If something becomes unclear → STOP.

------------------------------------------------------------
GENERAL RULES
------------------------------------------------------------

1. Never change multiple subsystems at once.
2. Always validate after each modification.
3. Production stability is priority over new features.
4. Receiver is the central orchestrator.
5. PIR only detects presence — no logic inside.
6. All state flags must remain simple and explicit.

------------------------------------------------------------
DEVELOPMENT CYCLE
------------------------------------------------------------

1. Modify file inside:
   /home/rose/gugus/

2. Restart affected service:
   sudo systemctl restart <service>

3. Validate:
   - systemctl status
   - journalctl logs
   - physical behavior of robot

4. Only when stable:
   git add
   git commit -m "clear description"
   git push

------------------------------------------------------------
DEBUGGING PRINCIPLE
------------------------------------------------------------

If something breaks:

- Check logs first.
- Identify which service is responsible.
- Fix the smallest possible thing.
- Never rewrite blindly.

------------------------------------------------------------
ARCHITECTURE PRINCIPLE
------------------------------------------------------------

Central brain:
gugus_receiver.py

State shared via flags.

Services must remain independent and simple.

------------------------------------------------------------
VOICE DEVELOPMENT RULE
------------------------------------------------------------

Voice must be added progressively:

1. Text endpoint test
2. ChatGPT integration
3. TTS output
4. Alexa webhook
5. Behavioral integration (head + eyes)

No direct complex jump.

------------------------------------------------------------
PROJECT MENTALITY
------------------------------------------------------------

This is a learning project.
Clarity > speed.
Stability > features.
Understanding > copying code.

------------------------------------------------------------
END OF PROTOCOL
------------------------------------------------------------
