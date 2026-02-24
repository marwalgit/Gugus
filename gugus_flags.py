from pathlib import Path

TMP = Path("/tmp")

FLAGS = {
    "sleep": TMP / "gugus_sleep.on",
    "think": TMP / "gugus_thinking.on",
    "listen": TMP / "gugus_listen.on",
}

def set_state_idle():
    for p in FLAGS.values():
        try:
            p.unlink()
        except FileNotFoundError:
            pass

def set_state_sleep():
    set_state_idle()
    FLAGS["sleep"].touch()

def set_state_think():
    try:
        FLAGS["sleep"].unlink()
    except FileNotFoundError:
        pass
    FLAGS["think"].touch()

def set_state_listen():
    for k in ("sleep", "think"):
        try:
            FLAGS[k].unlink()
        except FileNotFoundError:
            pass
    FLAGS["listen"].touch()

def get_state():
    if FLAGS["sleep"].exists():
        return "sleep"
    if FLAGS["think"].exists():
        return "think"
    if FLAGS["listen"].exists():
        return "listen"
    return "idle"
