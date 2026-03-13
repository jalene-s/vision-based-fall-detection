import time
from collections import deque

# store recent posture (~0.5 sec history)
posture_history = deque(maxlen=15)

fall_start_time = None
descent_start = None
state = "UPRIGHT"

FALL_CONFIRM_TIME = 1
ALERT_CONFIRM_TIME = 10


def detect_fall(data):

    global fall_start_time
    global descent_start
    global state

    if data is None:
        fall_start_time = None
        descent_start = None
        posture_history.clear()
        state = "UPRIGHT"
        return False

    angle = abs(data["angle"])
    height = data["hip_height"]
    aspect = data["aspect_ratio"]

    # store posture history
    posture_history.append((angle, height))

    if len(posture_history) < 10:
        return False

    old_angle, old_height = posture_history[0]

    # compute posture changes
    angle_change = abs(old_angle - angle)
    height_change = max(0, old_height - height)

    # estimate time (~30 FPS camera)
    change_time = len(posture_history) / 30

    # fall speed (important indicator)
    fall_speed = height_change / change_time if change_time > 0 else 0

    # posture definitions
    lying_posture = (
        height > 0.65 and
        aspect > 1.2 and
        (angle < 45 or angle > 135)
    )

    upright_posture = (
        aspect < 1.0 and
        60 <= angle <= 120
    )

    # ---------- STAGE 1: UPRIGHT ----------
    if upright_posture:
        state = "UPRIGHT"
        fall_start_time = None
        return False

    # ---------- STAGE 2: RAPID DESCENT ----------
    if state == "UPRIGHT" and fall_speed > 0.08 and angle_change > 10:
        state = "DESCENDING"
        descent_start = time.time()

    # cancel if descent is too slow
    if state == "DESCENDING" and descent_start:
        if time.time() - descent_start > 2:
            state = "UPRIGHT"

    # ---------- STAGE 3: LYING AFTER DESCENT ----------
    if state == "DESCENDING" and lying_posture:

        if fall_start_time is None:
            fall_start_time = time.time()

        elapsed = time.time() - fall_start_time

        if elapsed >= FALL_CONFIRM_TIME:
            state = "FALL_CONFIRMED"
            return True

    return False


def check_unrecovered():

    global fall_start_time

    if fall_start_time is None:
        return False

    elapsed = time.time() - fall_start_time

    if elapsed >= ALERT_CONFIRM_TIME:
        return True

    return False