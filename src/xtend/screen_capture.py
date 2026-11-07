"""Cross-platform desktop capture used where the Linux Rust/X11 backend is unavailable."""

import queue
import threading
import time

import cv2
import mss
import numpy as np


class ScreenCapturer:
    """Capture the primary display at a stable 1080p-or-smaller resolution.

    macOS requires the user to grant the app Screen Recording permission in
    System Settings.  Apple does not expose arbitrary application-window
    capture through this backend, so an app selection captures its display.
    """

    def __init__(self, app_name: str = "", capture_mode: str = "full_screen"):
        self.app_name = app_name
        self.capture_mode = capture_mode
        self.running = False
        self.frame_queue = queue.Queue(maxsize=2)
        self.thread: threading.Thread | None = None

    def start_capture(self) -> None:
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self) -> None:
        try:
            with mss.mss() as capture:
                monitor = capture.monitors[1]
                while self.running:
                    start = time.monotonic()
                    frame = np.asarray(capture.grab(monitor))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                    height, width = frame.shape[:2]
                    scale = min(1.0, 1920 / width, 1080 / height)
                    if scale < 1.0:
                        frame = cv2.resize(
                            frame,
                            (round(width * scale), round(height * scale)),
                            interpolation=cv2.INTER_AREA,
                        )

                    if not self.frame_queue.full():
                        self.frame_queue.put_nowait(frame)
                    time.sleep(max(0, (1 / 30) - (time.monotonic() - start)))
        except Exception as error:  # Permission errors are surfaced to the UI via its empty stream.
            self.running = False
            print(f"Screen capture failed: {error}")

    def stop_capture(self) -> None:
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
