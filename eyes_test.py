import time
import random
import os

from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from luma.core.render import canvas


# =========================
# Flags (états)
# =========================
SLEEP_FLAG = "/tmp/gugus_sleep.on"
LISTEN_FLAG = "/tmp/gugus_listen.on"
THINKING_FLAG = "/tmp/gugus_thinking.on"


# =========================
# Écran
# =========================
serial = i2c(port=1, address=0x3C)
device = sh1106(serial)


# =========================
# Paramètres yeux (formes)
# =========================

# IDLE
IDLE_EYE_W, IDLE_EYE_H = 26, 30
IDLE_RADIUS = 6
IDLE_GAP = 8
IDLE_Y = 12
IDLE_MOVE_SET = [
    (0, 0),
    (5, 0), (-5, 0),
    (0, 8), (0, -8),
]
IDLE_BLINK_CHOICES = [2, 3,5, 5]

# THINK
THINK_EYE_W, THINK_EYE_H = 26, 38
THINK_RADIUS = 6
THINK_GAP_DELTA = -6
THINK_Y_OFFSET = -6
THINK_MOVE_SET = [
    (0, 0),
    (1, 0), (-1, 0),
    (0, 2), (0, -2),
]
THINK_BLINK_RANGE = (7, 12)

# LISTEN
LISTEN_EYE_W, LISTEN_EYE_H = 34, 44
LISTEN_RADIUS = 8
LISTEN_GAP = 6
LISTEN_Y = 6

# SLEEP
SLEEP_ARC_W = 26
SLEEP_ARC_H = 14
SLEEP_GAP = 10
SLEEP_YY = device.height - 18


# =========================
# Animation "..." (think)
# =========================
DOTS_Y = device.height - 8
DOT_SPACING = 6
DOT_SIZE = 4
DOT_PERIOD = 1.6

t0 = time.time()


# =========================
# Fonctions dessin
# =========================

def draw_dots(draw):
    elapsed = time.time() - t0
    phase = int((elapsed / DOT_PERIOD) * 3) % 3
    n = phase + 1

    total_w = (n * DOT_SIZE) + ((n - 1) * DOT_SPACING)
    start_x = (device.width - total_w) // 2

    for i in range(n):
        x = start_x + i * (DOT_SIZE + DOT_SPACING)
        draw.rectangle((x, DOTS_Y, x + DOT_SIZE, DOTS_Y + DOT_SIZE), fill="white")


def draw_sleep(draw):
    draw.rectangle(device.bounding_box, fill="black")

    cx = device.width // 2
    x1 = cx - SLEEP_GAP // 2 - SLEEP_ARC_W
    x2 = cx + SLEEP_GAP // 2

    draw.arc((x1, SLEEP_YY, x1 + SLEEP_ARC_W, SLEEP_YY + SLEEP_ARC_H),
             start=0, end=180, fill="white")
    draw.arc((x2, SLEEP_YY, x2 + SLEEP_ARC_W, SLEEP_YY + SLEEP_ARC_H),
             start=0, end=180, fill="white")


def wake_animation():
    cx = device.width // 2
    x1 = cx - SLEEP_GAP // 2 - SLEEP_ARC_W
    x2 = cx + SLEEP_GAP // 2

    frames = [
        ("arcs", 0.10),
        ("slit", 0.10),
        ("half", 0.12),
        ("open", 0.15),
    ]

    for kind, delay in frames:
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, fill="black")

            if kind == "arcs":
                draw_sleep(draw)

            elif kind == "slit":
                yline = SLEEP_YY + SLEEP_ARC_H // 2
                draw.rectangle((x1, yline, x1 + SLEEP_ARC_W, yline + 2), fill="white")
                draw.rectangle((x2, yline, x2 + SLEEP_ARC_W, yline + 2), fill="white")

            elif kind == "half":
                h = 12
                ytop = SLEEP_YY - 2
                draw.rounded_rectangle((x1, ytop, x1 + SLEEP_ARC_W, ytop + h),
                                       radius=5, fill="white")
                draw.rounded_rectangle((x2, ytop, x2 + SLEEP_ARC_W, ytop + h),
                                       radius=5, fill="white")

            elif kind == "open":
                eye_w, eye_h = IDLE_EYE_W, IDLE_EYE_H
                gap = IDLE_GAP
                y = IDLE_Y
                xx1 = (device.width // 2) - eye_w - gap // 2
                xx2 = (device.width // 2) + gap // 2

                draw.rounded_rectangle((xx1, y, xx1 + eye_w, y + eye_h),
                                       radius=IDLE_RADIUS, fill="white")
                draw.rounded_rectangle((xx2, y, xx2 + eye_w, y + eye_h),
                                       radius=IDLE_RADIUS, fill="white")

        time.sleep(delay)

    # Petit enchaînement de blinks après ouverture
    for _ in range(3):
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, fill="black")

            eye_w, eye_h = IDLE_EYE_W, IDLE_EYE_H
            gap = IDLE_GAP
            y = IDLE_Y

            x1 = (device.width // 2) - eye_w - gap // 2
            x2 = (device.width // 2) + gap // 2

            yy = y + eye_h // 2
            draw.rectangle((x1, yy, x1 + eye_w, yy + 3), fill="white")
            draw.rectangle((x2, yy, x2 + eye_w, yy + 3), fill="white")

        time.sleep(0.08)

        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, fill="black")
            draw.rounded_rectangle((x1, y, x1 + eye_w, y + eye_h),
                                   radius=IDLE_RADIUS, fill="white")
            draw.rounded_rectangle((x2, y, x2 + eye_w, y + eye_h),
                                   radius=IDLE_RADIUS, fill="white")

        time.sleep(0.08)

# =========================
# Boucle principale
# =========================

dx, dy = 0, 0
next_move = time.time() + random.uniform(0.8, 2.2)
next_blink = time.time() + random.choice(IDLE_BLINK_CHOICES)
was_sleeping = False

print("👀 Gugus eyes started")

while True:
    now = time.time()

    sleeping = os.path.exists(SLEEP_FLAG)
    listening = (not sleeping) and os.path.exists(LISTEN_FLAG)
    thinking = (not sleeping) and (not listening) and os.path.exists(THINKING_FLAG)

    woke_up = (was_sleeping and not sleeping)
    if woke_up:
        wake_animation()

    if sleeping:
        with canvas(device) as draw:
            draw_sleep(draw)
        was_sleeping = True
        time.sleep(0.2)
        continue

    was_sleeping = False

    if listening:
        eye_w, eye_h = LISTEN_EYE_W, LISTEN_EYE_H
        gap = LISTEN_GAP
        y = LISTEN_Y
        radius = LISTEN_RADIUS

        x1 = (device.width // 2) - eye_w - gap // 2
        x2 = (device.width // 2) + gap // 2

        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, fill="black")
            draw.rounded_rectangle((x1, y, x1 + eye_w, y + eye_h),
                                   radius=radius, fill="white")
            draw.rounded_rectangle((x2, y, x2 + eye_w, y + eye_h),
                                   radius=radius, fill="white")

        time.sleep(0.05)
        continue

    if thinking:
        eye_w, eye_h = THINK_EYE_W, THINK_EYE_H
        gap = IDLE_GAP + THINK_GAP_DELTA
        y = IDLE_Y + THINK_Y_OFFSET
        radius = THINK_RADIUS
        move_set = THINK_MOVE_SET
        blink_delay = random.uniform(*THINK_BLINK_RANGE)
    else:
        eye_w, eye_h = IDLE_EYE_W, IDLE_EYE_H
        gap = IDLE_GAP
        y = IDLE_Y
        radius = IDLE_RADIUS
        move_set = IDLE_MOVE_SET
        blink_delay = random.choice(IDLE_BLINK_CHOICES)

    x1 = (device.width // 2) - eye_w - gap // 2
    x2 = (device.width // 2) + gap // 2

    if now >= next_move:
        dx, dy = random.choice(move_set)
        next_move = now + random.uniform(1.5, 4.0)

    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, fill="black")
        draw.rounded_rectangle((x1 + dx, y + dy, x1 + dx + eye_w, y + dy + eye_h),
                               radius=radius, fill="white")
        draw.rounded_rectangle((x2 + dx, y + dy, x2 + dx + eye_w, y + dy + eye_h),
                               radius=radius, fill="white")
        if thinking:
            draw_dots(draw)

    if now >= next_blink:
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, fill="black")
            yy = y + dy + eye_h // 2
            draw.rectangle((x1 + dx, yy, x1 + dx + eye_w, yy + 3), fill="white")
            draw.rectangle((x2 + dx, yy, x2 + dx + eye_w, yy + 3), fill="white")
            if thinking:
                draw_dots(draw)

        time.sleep(0.01)
        next_blink = now + blink_delay

    time.sleep(0.01)
