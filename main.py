import cv2
import time
import threading

from pose_detection import get_pose
from fall_detection import detect_fall
from camera_motion import camera_moved

from video_recorder import (
    buffer_frame,
    start_recording,
    record_frame,
    recording_finished,
    stop_recording
)

from alert_system import (
    send_alert_message,
    send_alert_image,
    send_alert_video
)

cap = cv2.VideoCapture(0)

recording_active = False
fall_start_time = None
alert_cooldown = False
cooldown_start = None
COOLDOWN_TIME = 8


def send_alerts(video_file):
    send_alert_message()
    send_alert_image("fall_snapshot.jpg")
    send_alert_video(video_file)


while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    status = "Monitoring"
    color = (0,255,0)

    buffer_frame(frame)

    if alert_cooldown:
        if time.time() - cooldown_start > COOLDOWN_TIME:
            alert_cooldown = False
        else:
            status = "Cooldown"
            color = (255,255,0)

    if camera_moved(frame):

        status = "Movement Detected"
        color = (0,255,255)

        cv2.putText(frame,status,(20,40),
                    cv2.FONT_HERSHEY_SIMPLEX,1,color,2)

        cv2.imshow("Fall Detection System",frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == 27:
            break

        if cv2.getWindowProperty("Fall Detection System", cv2.WND_PROP_VISIBLE) < 1:
            break

        continue

    data = get_pose(frame)

    if data is not None:

        angle = round(data["angle"],1)
        height = round(data["hip_height"],2)
        aspect = round(data["aspect_ratio"],2)

        debug_text = f"Angle:{angle}  Height:{height}  Aspect:{aspect}"

        cv2.putText(frame,debug_text,(20,80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255,255,0),
                    2)

    fall = detect_fall(data)

    if fall and not recording_active and not alert_cooldown:

        print("Possible fall detected")

        cv2.imwrite("fall_snapshot.jpg",frame)

        start_recording(frame)

        recording_active = True
        fall_start_time = time.time()

    if recording_active:

        record_frame(frame)

        recovered = False

        if data is not None:
            angle = abs(data["angle"])
            aspect = data["aspect_ratio"]

            if aspect < 1.2 and 45 <= angle <= 135:
                recovered = True

        if recovered:

            print("Recovery posture detected")

            recording_active = False
            fall_start_time = None

            status = "Recovery Detected"
            color = (0,255,0)

        else:

            elapsed = int(time.time() - fall_start_time)

            status = f"Fall Detected | No Movement: {elapsed}s"
            color = (0,0,255)

            if recording_finished():

                video_file = stop_recording()

                threading.Thread(
                    target=send_alerts,
                    args=(video_file,),
                    daemon=True
                ).start()

                recording_active = False
                fall_start_time = None

                alert_cooldown = True
                cooldown_start = time.time()

    cv2.putText(frame,status,(20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color,
                2)

    cv2.imshow("Fall Detection System",frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q') or key == 27:
        break

    if cv2.getWindowProperty("Fall Detection System", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()