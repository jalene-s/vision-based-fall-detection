import time

fall_start_time = None

FALL_CONFIRM_TIME = 1
ALERT_CONFIRM_TIME = 10


def detect_fall(data):

    global fall_start_time

    if data is None:
        fall_start_time = None
        return False

    angle = abs(data["angle"])
    height = data["hip_height"]
    aspect = data["aspect_ratio"]

    # lying posture (fall)
    lying_posture = (
        height > 0.65 and
        aspect > 1.2 and
        (angle < 45 or angle > 135)
    )

    # upright posture (standing or sitting)
    upright_posture = (
        aspect < 0.6 and
        60 <= angle <= 120
    )

    # RECOVERY: reset fall if upright again
    if upright_posture:
        fall_start_time = None
        return False

    if lying_posture:

        if fall_start_time is None:
            fall_start_time = time.time()

        elapsed = time.time() - fall_start_time

        if elapsed >= FALL_CONFIRM_TIME:
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