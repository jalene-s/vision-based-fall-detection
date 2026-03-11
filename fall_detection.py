# fall_detection.py

import math
import time


HEIGHT_DROP_THRESHOLD = 0.25
ANGLE_THRESHOLD = 100
LOW_HEIGHT_THRESHOLD = 0.32

FALL_COOLDOWN = 2

RECOVERY_HEIGHT_THRESHOLD = 0.40
RECOVERY_ANGLE_THRESHOLD = 70

MOVEMENT_THRESHOLD = 0.03

HEIGHT_SMOOTHING = 0.7


previous_height = None
previous_landmarks = None
last_fall_time = 0


def calculate_body_height(landmarks):

    head = landmarks[0]
    left_ankle = landmarks[27]
    right_ankle = landmarks[28]

    ankle_y = (left_ankle.y + right_ankle.y) / 2

    return abs(head.y - ankle_y)


def calculate_body_angle(landmarks):

    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]

    left_hip = landmarks[23]
    right_hip = landmarks[24]

    shoulder_mid_x = (left_shoulder.x + right_shoulder.x) / 2
    shoulder_mid_y = (left_shoulder.y + right_shoulder.y) / 2

    hip_mid_x = (left_hip.x + right_hip.x) / 2
    hip_mid_y = (left_hip.y + right_hip.y) / 2

    dx = shoulder_mid_x - hip_mid_x
    dy = shoulder_mid_y - hip_mid_y

    return abs(math.degrees(math.atan2(dy, dx)))


def detect_movement(landmarks):

    global previous_landmarks

    if previous_landmarks is None:
        previous_landmarks = landmarks
        return False

    total = 0

    for current, previous in zip(landmarks, previous_landmarks):

        total += math.sqrt(
            (current.x - previous.x) ** 2 +
            (current.y - previous.y) ** 2
        )

    avg = total / len(landmarks)

    previous_landmarks = landmarks

    return avg > MOVEMENT_THRESHOLD


def detect_fall(landmarks):

    global previous_height
    global last_fall_time

    raw_height = calculate_body_height(landmarks)

    if previous_height is None:
        height = raw_height
    else:
        height = HEIGHT_SMOOTHING * previous_height + (1 - HEIGHT_SMOOTHING) * raw_height

    angle = calculate_body_angle(landmarks)

    movement = detect_movement(landmarks)

    recovered = height >= RECOVERY_HEIGHT_THRESHOLD and angle < RECOVERY_ANGLE_THRESHOLD

    lying = height < LOW_HEIGHT_THRESHOLD and angle > ANGLE_THRESHOLD

    fall_detected = False

    if previous_height is not None:

        height_change = previous_height - height
        current_time = time.time()

        if (
            height_change > HEIGHT_DROP_THRESHOLD
            and lying
            and current_time - last_fall_time > FALL_COOLDOWN
        ):
            fall_detected = True
            last_fall_time = current_time

    previous_height = height

    return {
        "fall_detected": fall_detected,
        "height": height,
        "angle": angle,
        "movement": movement,
        "recovered": recovered,
        "lying": lying,
    }