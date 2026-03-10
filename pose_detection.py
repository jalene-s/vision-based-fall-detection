# pose_detection.py

import mediapipe as mp
import cv2

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    static_image_mode=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


def get_landmarks(frame):
    """
    Process a video frame and return pose landmarks.
    Returns landmarks (33 points) and the annotated frame.
    Returns None for landmarks if no pose is detected.
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        return results.pose_landmarks.landmark, frame

    return None, frame