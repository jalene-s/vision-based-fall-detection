import cv2
import mediapipe as mp
import numpy as np
import time

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

fall_detected = False
monitoring = False
no_movement_start = None

previous_landmarks = None
MOVEMENT_THRESHOLD = 0.02
NO_MOVEMENT_TIME = 10  # seconds before alert

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = pose.process(rgb)

    movement = 0

    if results.pose_landmarks:
        mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        landmarks = results.pose_landmarks.landmark

        shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

        h, w, _ = frame.shape
        shoulder_y = int(shoulder.y * h)
        ankle_y = int(ankle.y * h)

        body_height = abs(ankle_y - shoulder_y)

        # --- FALL DETECTION ---
        if body_height < 120 and not fall_detected:
            fall_detected = True
            monitoring = True
            print("Fall detected. Monitoring movement...")

        # --- MOVEMENT DETECTION ---
        if previous_landmarks is not None:
            for i in range(len(landmarks)):
                movement += abs(landmarks[i].x - previous_landmarks[i][0])
                movement += abs(landmarks[i].y - previous_landmarks[i][1])

        previous_landmarks = [(lm.x, lm.y) for lm in landmarks]

        # --- POST FALL MONITORING ---
        if monitoring:

            cv2.putText(frame, "Monitoring after fall...", (20,40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

            if movement < MOVEMENT_THRESHOLD:

                if no_movement_start is None:
                    no_movement_start = time.time()

                elapsed = time.time() - no_movement_start

                cv2.putText(frame, f"No movement: {int(elapsed)}s", (20,70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

                if elapsed > NO_MOVEMENT_TIME:
                    cv2.putText(frame, "ALERT: Person Unconscious!", (120,120),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

            else:
                no_movement_start = None

    if fall_detected:
        cv2.putText(frame, "FALL DETECTED", (200,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

    cv2.imshow("Fall Detection Monitoring System", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()