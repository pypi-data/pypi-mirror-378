"""
Timer implementation for the Python ROS engine.
"""

import threading
import time
from typing import Callable


class Timer:
    """
    Timer for executing callbacks at regular intervals.
    """

    def __init__(self, period: float, callback: Callable):
        """
        Initialize a timer.

        Args:
            period: Timer period in seconds
            callback: Callback function to execute when timer expires
        """
        self.period = period
        self._callback = callback
        self._is_canceled = False
        self._thread = None

        # Start the timer in a separate thread
        self._start_timer()

    def _start_timer(self):
        """
        Start the timer thread.
        """
        self._thread = threading.Thread(target=self._timer_loop, daemon=True)
        self._thread.start()

    def _timer_loop(self):
        """
        Timer loop that executes the callback at regular intervals.
        """
        while not self._is_canceled:
            time.sleep(self.period)
            if not self._is_canceled:
                self._callback()

    def cancel(self):
        """
        Cancel the timer.
        """
        self._is_canceled = True

    def is_canceled(self) -> bool:
        """
        Check if the timer is canceled.

        Returns:
            bool: True if timer is canceled
        """
        return self._is_canceled

    def reset(self):
        """
        Reset the timer.
        """
        self.cancel()
        self._is_canceled = False
        self._start_timer()
