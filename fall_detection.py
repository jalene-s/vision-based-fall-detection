# fall_detection.py

"""
1. Height Calculation

With this file, the system can estimate body height using the vertical distance between the head and ankles.
"""

"""
2. Body Angle Calculation

Body orientation can be computed using the midpoints of shoulders and hips.
So when a person falls, the body becomes more horizontal, increasing the body angle.
"""

"""
A fall is detected when height drops suddenly, body angle exceeds threshold, or waiting time for standing up prevents repeated alerts
"""

import math
import time

HEIGHT_DROP_THRESHOLD = 0.25     # sudden height decrease
ANGLE_THRESHOLD = 60             # body angle from vertical
FALL_COOLDOWN = 2                # seconds before another detection

previous_height = None
last_fall_time = 0


def calculate_body_height(landmarks):
    """
    Estimate body height using head and ankle landmarks.
    """
    head = landmarks[0]        # nose/head
    left_ankle = landmarks[27]
    right_ankle = landmarks[28]

    ankle_y = (left_ankle.y + right_ankle.y) / 2

    height = abs(head.y - ankle_y)
    return height


def calculate_body_angle(landmarks):
    """
    Compute body orientation angle using shoulders and hips.
    """
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

    angle = abs(math.degrees(math.atan2(dy, dx)))

    return angle


def detect_fall(landmarks):
    """
    Main fall detection logic.
    Returns:
        fall_detected (bool)
        height
        angle
    """
    global previous_height, last_fall_time

    height = calculate_body_height(landmarks)
    angle = calculate_body_angle(landmarks)

    fall_detected = False

    if previous_height is not None:

        height_change = previous_height - height
        current_time = time.time()

        if (
            height_change > HEIGHT_DROP_THRESHOLD and
            angle > ANGLE_THRESHOLD and
            current_time - last_fall_time > FALL_COOLDOWN
        ):
            fall_detected = True
            last_fall_time = current_time

    previous_height = height

    return fall_detected, height, angle