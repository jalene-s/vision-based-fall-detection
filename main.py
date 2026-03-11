import cv2

from alert_system import AlertSystem
from fall_detection import detect_fall
from monitoring import PostFallMonitor
from pose_detection import close_pose_detector, get_landmarks


def run(video_source=0):

    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        raise RuntimeError("Could not open camera/video source.")

    alert_system = AlertSystem(alert_delay=10, escalation_delay=15)
    monitor = PostFallMonitor(no_movement_time=10)

    try:

        while True:

            ok, frame = cap.read()

            if not ok:
                break

            landmarks, annotated = get_landmarks(frame)

            status_text = "Monitoring..."
            color = (0, 255, 0)

            if landmarks is not None:

                fall_state = detect_fall(landmarks)

                monitor_state = monitor.update(
                    fall_detected=fall_state["fall_detected"],
                    movement=fall_state["movement"],
                    lying=fall_state["lying"],
                    recovered=fall_state["recovered"],
                )

                alert_state = alert_system.process_fall_state(
                    fall_detected=fall_state["fall_detected"],
                    recovered=fall_state["recovered"],
                    movement=fall_state["movement"],
                    frame=frame,
                )

                # -------- STATE DISPLAY --------

                if fall_state["fall_detected"]:
                    status_text = "FALL DETECTED"
                    color = (0, 165, 255)

                elif fall_state["lying"]:
                    status_text = "PERSON LYING"
                    color = (255, 0, 255)

                if monitor_state["no_movement_alert"]:
                    status_text = "NO MOVEMENT ALERT"
                    color = (0, 0, 255)

                if fall_state["recovered"]:
                    status_text = "RECOVERED"
                    color = (255, 255, 0)

                # -------- VISUAL BOX FOR DEMO --------

                if fall_state["fall_detected"] or fall_state["lying"]:
                    h, w, _ = annotated.shape
                    cv2.rectangle(
                        annotated,
                        (0, 0),
                        (w, h),
                        (0, 0, 255),
                        5
                    )

                # -------- MONITOR TEXT --------

                if monitor_state["monitoring"]:

                    cv2.putText(
                        annotated,
                        "Monitoring after fall...",
                        (10, 95),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 0),
                        2,
                    )

                if monitor_state["no_movement_elapsed"] > 0:

                    cv2.putText(
                        annotated,
                        f"No movement: {int(monitor_state['no_movement_elapsed'])}s",
                        (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 0, 255),
                        2,
                    )

                if alert_state["alert_sent_now"]:
                    status_text = "ALERT SENT"
                    color = (0, 0, 255)

                if alert_state["escalation_now"]:
                    status_text = "ESCALATION SENT"
                    color = (0, 0, 255)

                # -------- DEBUG INFO --------

                cv2.putText(
                    annotated,
                    f"height={fall_state['height']:.2f} angle={fall_state['angle']:.1f}",
                    (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

            # -------- MAIN STATUS TEXT --------

            cv2.putText(
                annotated,
                status_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                color,
                2,
            )

            cv2.imshow("Fall Detection Monitoring System", annotated)

            key = cv2.waitKey(1) & 0xFF

            if key in (27, ord("q")):
                break

    finally:

        cap.release()
        close_pose_detector()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run()