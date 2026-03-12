import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

pose = mp_pose.Pose()

def get_pose(frame):

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = pose.process(rgb)

    if not results.pose_landmarks:
        return None

    mp_drawing.draw_landmarks(
        frame,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_styles.get_default_pose_landmarks_style()
    )

    landmarks = results.pose_landmarks.landmark

    shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]

    xs = [l.x for l in landmarks]
    ys = [l.y for l in landmarks]

    width = max(xs) - min(xs)
    height = max(ys) - min(ys)

    aspect_ratio = width / height if height != 0 else 0

    shoulder_point = np.array([shoulder.x, shoulder.y])
    hip_point = np.array([hip.x, hip.y])

    body_vector = hip_point - shoulder_point

    angle = abs(np.degrees(np.arctan2(body_vector[1], body_vector[0])))

    hip_height = min(max(hip.y, 0), 1)
    shoulder_height = shoulder.y

    hip_shoulder_ratio = abs(hip_height - shoulder_height)

    floor_distance = 1 - hip.y

    return {
        "angle": angle,
        "hip_height": hip_height,
        "aspect_ratio": aspect_ratio,
        "hip_shoulder_ratio": hip_shoulder_ratio,
        "floor_distance": floor_distance
    }