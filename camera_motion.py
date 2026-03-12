import cv2
import numpy as np

prev_gray = None

def camera_moved(frame):

    global prev_gray

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if prev_gray is None:
        prev_gray = gray
        return False

    diff = cv2.absdiff(prev_gray, gray)
    movement = np.mean(diff)

    prev_gray = gray

    if movement > 25:
        return True

    return False