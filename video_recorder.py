import cv2
import time
from collections import deque

buffer_seconds = 10
fps = 20

frame_buffer = deque(maxlen=buffer_seconds * fps)

recording = False
writer = None
record_start = None
record_duration = 20
filename = None


def buffer_frame(frame):
    frame_buffer.append(frame)


def start_recording(frame):

    global recording, writer, record_start, filename

    if recording:
        return

    h, w, _ = frame.shape

    filename = f"fall_event_{int(time.time())}.avi"

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_file = f"fall_{int(time.time())}.mp4"

    writer = cv2.VideoWriter(filename, fourcc, fps, (w, h))

    for buffered_frame in frame_buffer:
        writer.write(buffered_frame)

    record_start = time.time()

    recording = True


def record_frame(frame):

    global writer

    if writer is not None:
        writer.write(frame)


def recording_finished():

    global record_start, record_duration

    if record_start is None:
        return False

    return (time.time() - record_start) > record_duration


def stop_recording():

    global writer, recording, filename

    if writer:
        writer.release()

    writer = None
    recording = False

    return filename