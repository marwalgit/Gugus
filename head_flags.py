import os
import time
import random
from head_controller import HeadController

FLAG_LISTEN = "/tmp/gugus_listen.on"
FLAG_THINK = "/tmp/gugus_thinking.on"
FLAG_SLEEP = "/tmp/gugus_sleep.on"

CENTER = 1500
LISTEN_POS = 1650

# THINK amplitude limites
THINK_MIN = 1400
THINK_MAX = 1600

# IDLE plage complète (pas micro-centre)
IDLE_MIN = 1450
IDLE_MAX = 1550

# Intervalle entre mouvements idle
IDLE_INTERVAL_MIN = 3.0
IDLE_INTERVAL_MAX = 10.0


def flag_exists(path: str) -> bool:
    return os.path.exists(path)


def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


if __name__ == "__main__":
    print("[head] démarrage")

    head = HeadController(gpio_pin=18, start_us=CENTER)

    last_mode = None
    idle_pos = CENTER
    next_idle_move = time.time() + random.uniform(2.0, 4.0)

    try:
        while True:
            now = time.time()

            listen = flag_exists(FLAG_LISTEN)
            think = flag_exists(FLAG_THINK)
            sleep = flag_exists(FLAG_SLEEP)

            # Détermination du mode
            if sleep:
                mode = "sleep"
            elif listen:
                mode = "listen"
            elif think:
                mode = "think"
            else:
                mode = "idle"

            # Si changement de mode
            if mode != last_mode:
                print(f"[head] mode -> {mode}")

                if mode == "sleep":
                    head.move_to(CENTER)

                elif mode == "listen":
                    head.move_to(LISTEN_POS)

                elif mode == "think":
                    amp = random.randint(40, 120)
                    side = random.choice([-1, 1])
                    target = clamp(CENTER + side * amp, THINK_MIN, THINK_MAX)
                    print(f"[head] think target = {target}")
                    head.move_to(target, step_us=4, step_delay=0.04)

                elif mode == "idle":
                    # On ne recentre pas, on garde la position actuelle
                    next_idle_move = now + random.uniform(0.5, 2.0)

                last_mode = mode

            # Animation idle naturelle (positions aléatoires)
            if mode == "idle" and now >= next_idle_move:
                target = random.randint(IDLE_MIN, IDLE_MAX)

                # éviter les mini déplacements insignifiants
                if abs(target - idle_pos) < 8:
                    target = clamp(
                        target + random.choice([-15, 15]),
                        IDLE_MIN,
                        IDLE_MAX,
                    )

                print(f"[head] idle wander -> {idle_pos} -> {target}")
                head.move_to(target, step_us=3, step_delay=0.04)
                idle_pos = target

                next_idle_move = now + random.uniform(
                    IDLE_INTERVAL_MIN,
                    IDLE_INTERVAL_MAX,
                )

            time.sleep(0.05)

    finally:
        head.stop()
        print("[head] stop")
