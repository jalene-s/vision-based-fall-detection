# alert_system.py

"""
Alert and post-fall monitoring utilities.

Behavior:
1. When a fall is first detected, start fall tracking.
2. Wait ALERT_DELAY seconds before sending the initial alert.
3. Send a camera snapshot to Telegram together with the alert (if a frame is provided).
4. If there is still no movement/recovery by ESCALATION_DELAY, trigger escalation.
5. If recovery happens at any time, clear fall state.
"""

import json
import time
import uuid
import urllib.parse
import urllib.request


ALERT_DELAY = 10           # seconds after fall detection before sending alert
ESCALATION_DELAY = 15      # seconds after fall detection before escalation

# Telegram bot placeholders.
TELEGRAM_BOT_TOKEN = "8513395582:AAEL4mmRoxcHW274a7JCDsoM3lvLw1ZLmhw"
TELEGRAM_CHAT_ID = "8208889681"


class AlertSystem:
    """
    Stateful alert manager for delayed alerting and escalation.
    """

    def __init__(self, alert_delay=ALERT_DELAY, escalation_delay=ESCALATION_DELAY):
        self.alert_delay = alert_delay
        self.escalation_delay = escalation_delay

        self.fall_active = False
        self.fall_start_time = None

        self.alert_sent = False
        self.escalation_sent = False

    def start_fall(self, current_time=None):
        """
        Start tracking a fall event if not already active.
        """
        if current_time is None:
            current_time = time.time()

        if not self.fall_active:
            self.fall_active = True
            self.fall_start_time = current_time
            self.alert_sent = False
            self.escalation_sent = False

    def clear_fall_state(self):
        """
        Clear active fall state on recovery.
        """
        self.fall_active = False
        self.fall_start_time = None
        self.alert_sent = False
        self.escalation_sent = False

    def _send_telegram_message(self, text):
        """
        Send Telegram text message.

        If token/chat id are empty, skip sending and return False.
        """
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            return False

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = urllib.parse.urlencode({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                body = response.read().decode("utf-8")
                parsed = json.loads(body)
                return bool(parsed.get("ok"))
        except Exception:
            return False

    def _send_telegram_photo(self, frame, caption=""):
        """
        Send Telegram photo from an OpenCV frame.

        If token/chat id are empty or frame encoding fails, return False.
        """
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            return False

        try:
            import cv2
        except Exception:
            return False

        ok, encoded = cv2.imencode(".jpg", frame)
        if not ok:
            return False

        photo_bytes = encoded.tobytes()
        boundary = f"----FallBoundary{uuid.uuid4().hex}"

        body = []
        body.append(f"--{boundary}\r\n".encode("utf-8"))
        body.append(b'Content-Disposition: form-data; name="chat_id"\r\n\r\n')
        body.append(f"{TELEGRAM_CHAT_ID}\r\n".encode("utf-8"))

        body.append(f"--{boundary}\r\n".encode("utf-8"))
        body.append(b'Content-Disposition: form-data; name="caption"\r\n\r\n')
        body.append(f"{caption}\r\n".encode("utf-8"))

        body.append(f"--{boundary}\r\n".encode("utf-8"))
        body.append(b'Content-Disposition: form-data; name="photo"; filename="fall.jpg"\r\n')
        body.append(b"Content-Type: image/jpeg\r\n\r\n")
        body.append(photo_bytes)
        body.append(b"\r\n")

        body.append(f"--{boundary}--\r\n".encode("utf-8"))
        payload = b"".join(body)

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                resp_body = response.read().decode("utf-8")
                parsed = json.loads(resp_body)
                return bool(parsed.get("ok"))
        except Exception:
            return False

    def process_fall_state(self, fall_detected, recovered=False, movement=False, frame=None, current_time=None):
        """
        Main alert workflow.

        Args:
            fall_detected (bool): True when fall detector flags a fall.
            recovered (bool): True when person has recovered/stood up.
            movement (bool): True when movement is observed after fall.
            frame (numpy.ndarray | None): current camera frame for Telegram snapshot.
            current_time (float | None): optional timestamp override.

        Returns:
            dict:
                alert_sent_now (bool): True only when alert is sent this call.
                escalation_now (bool): True only when escalation is sent this call.
                fall_active (bool): whether fall tracking is active.
        """
        if current_time is None:
            current_time = time.time()

        alert_sent_now = False
        escalation_now = False

        if fall_detected:
            self.start_fall(current_time=current_time)

        if recovered:
            self.clear_fall_state()

        if self.fall_active and self.fall_start_time is not None:
            elapsed = current_time - self.fall_start_time

            if elapsed >= self.alert_delay and not self.alert_sent:
                self._send_telegram_message("⚠️ Fall detected. Please check immediately.")
                if frame is not None:
                    self._send_telegram_photo(frame, caption="Fall snapshot")
                self.alert_sent = True
                alert_sent_now = True

            if elapsed >= self.escalation_delay and not self.escalation_sent and not movement and not recovered:
                self._send_telegram_message("🚨 Escalation: No movement/recovery detected after fall.")
                self.escalation_sent = True
                escalation_now = True

        return {
            "alert_sent_now": alert_sent_now,
            "escalation_now": escalation_now,
            "fall_active": self.fall_active,
        }
