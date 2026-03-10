# fall_detection.py

"""
Fall and recovery decision helpers.
"""

import math
import time

HEIGHT_DROP_THRESHOLD = 0.25     # sudden height decrease
ANGLE_THRESHOLD = 60             # body angle threshold for likely fall
FALL_COOLDOWN = 2                # seconds before another fall trigger

RECOVERY_HEIGHT_THRESHOLD = 0.35  # higher body height suggests standing/recovered
RECOVERY_ANGLE_THRESHOLD = 50     # lower body angle suggests vertical posture
MOVEMENT_THRESHOLD = 0.03         # landmark movement threshold

previous_height = None
last_fall_time = 0
previous_landmarks = None


def calculate_body_height(landmarks):
    """Estimate body height using head and ankle landmarks."""
    head = landmarks[0]
    left_ankle = landmarks[27]
    right_ankle = landmarks[28]
    ankle_y = (left_ankle.y + right_ankle.y) / 2
    return abs(head.y - ankle_y)


def calculate_body_angle(landmarks):
    """Compute body orientation angle using shoulder and hip midpoints."""
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
    """Detect simple body movement by tracking average landmark displacement."""
    global previous_landmarks

    if previous_landmarks is None:
        previous_landmarks = landmarks
        return False

    total = 0.0
    for current, previous in zip(landmarks, previous_landmarks):
        total += math.sqrt((current.x - previous.x) ** 2 + (current.y - previous.y) ** 2)

    avg_displacement = total / len(landmarks)
    previous_landmarks = landmarks
    return avg_displacement > MOVEMENT_THRESHOLD


def detect_recovery(height, angle):
    """Person is considered recovered when posture returns to standing-like shape."""
    return height >= RECOVERY_HEIGHT_THRESHOLD and angle <= RECOVERY_ANGLE_THRESHOLD


def detect_fall(landmarks):
    """Main fall detection logic."""
    global previous_height, last_fall_time

    height = calculate_body_height(landmarks)
    angle = calculate_body_angle(landmarks)
    movement = detect_movement(landmarks)
    recovered = detect_recovery(height, angle)

    fall_detected = False

    if previous_height is not None:
        height_change = previous_height - height
        current_time = time.time()

        if (
            height_change > HEIGHT_DROP_THRESHOLD
            and angle > ANGLE_THRESHOLD
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
    }