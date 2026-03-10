# pose_detection.py

import cv2
import sys

_pose = None
_mp_pose = None
_mp_drawing = None
_pose_import_error = None


def _load_mediapipe_pose_modules():
    """Load MediaPipe pose modules with compatibility fallbacks."""
    global _mp_pose, _mp_drawing, _pose_import_error

    if _mp_pose is not None and _mp_drawing is not None:
        return

    try:
        import mediapipe as mp

        # Standard API path for most mediapipe releases.
        if hasattr(mp, "solutions"):
            _mp_pose = mp.solutions.pose
            _mp_drawing = mp.solutions.drawing_utils
            return

        # Fallback for environments where `solutions` isn't exposed at top-level.
        from mediapipe.python.solutions import drawing_utils, pose

        _mp_pose = pose
        _mp_drawing = drawing_utils
        return
    except Exception as exc:
        _pose_import_error = exc
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        hint = (
            "MediaPipe does not consistently ship wheels for Python 3.13+ yet. "
            "If you are using Python 3.13/3.14, install Python 3.10-3.12 and recreate your venv. "
        )
        raise RuntimeError(
            "MediaPipe Pose could not be initialized. "
            "Install/repair mediapipe in the same interpreter (`python -m pip install --upgrade mediapipe`) "
            "and ensure no local file/folder is named 'mediapipe'. "
            f"Detected Python {py_version}. "
            + hint
        ) from exc


def _ensure_pose_initialized():
    """Lazy-init pose detector so import-time failures are avoided."""
    global _pose

    if _pose is not None:
        return

    _load_mediapipe_pose_modules()
    _pose = _mp_pose.Pose(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )


def get_landmarks(frame):
    """
    Process frame and return pose landmarks + annotated frame.
    """
    _ensure_pose_initialized()

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = _pose.process(rgb_frame)

    if results.pose_landmarks:
        _mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            _mp_pose.POSE_CONNECTIONS,
        )
        return results.pose_landmarks.landmark, frame

    return None, frame


def close_pose_detector():
    """Release MediaPipe pose resources."""
    global _pose

    if _pose is not None:
        _pose.close()
        _pose = None