# vision-based-fall-detection
-This repository contains a vision-based fall detection and post-fall monitoring system that uses camera input and pose detection to identify possible fall incidents and monitor recovery.

+## Modules
+- `pose_detection.py`: gets and draws MediaPipe pose landmarks.
+- `fall_detection.py`: computes body height/angle and infers `fall_detected`, `movement`, and `recovered`.
+- `monitoring.py`: tracks inactivity after a fall and measures no-movement duration.
+- `alert_system.py`: handles delayed Telegram alerting, escalation, and optional snapshot sending.
+- `main.py`: connects all modules in a live camera loop.
+
+## Run
+1. Install dependencies (example):
+   - `pip install opencv-python mediapipe`
+2. Set Telegram details in `alert_system.py`:
+   - `TELEGRAM_BOT_TOKEN`
+   - `TELEGRAM_CHAT_ID`
+3. Start the app:
+   - `python main.py`
+
+Press `q` or `Esc` to quit.
