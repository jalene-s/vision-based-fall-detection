# monitoring.py

"""
Post-fall monitoring state manager.
Tracks no-movement duration after a fall and raises an alert.
"""

import time

NO_MOVEMENT_TIME = 10


class PostFallMonitor:

    def __init__(self, no_movement_time=NO_MOVEMENT_TIME):
        self.no_movement_time = no_movement_time
        self.monitoring = False
        self.no_movement_start = None

    def reset(self):
        self.monitoring = False
        self.no_movement_start = None

    def update(self, fall_detected, movement, lying=False, recovered=False, current_time=None):

        if current_time is None:
            current_time = time.time()

        if recovered:
            self.reset()

        if fall_detected or lying:
            self.monitoring = True

        no_movement_elapsed = 0.0
        no_movement_alert = False

        if self.monitoring:

            if movement:
                self.no_movement_start = None

            else:

                if self.no_movement_start is None:
                    self.no_movement_start = current_time

                no_movement_elapsed = current_time - self.no_movement_start

                if no_movement_elapsed >= self.no_movement_time:
                    no_movement_alert = True

        return {
            "monitoring": self.monitoring,
            "no_movement_elapsed": no_movement_elapsed,
            "no_movement_alert": no_movement_alert,
        }