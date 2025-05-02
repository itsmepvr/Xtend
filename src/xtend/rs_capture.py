import ctypes
import numpy as np
import threading
import queue
import time
import os
import sys

if getattr(sys, 'frozen', False):
    # Running from PyInstaller
    base_path = sys._MEIPASS
else:
    # Running from source
    base_path = os.path.dirname(__file__)

lib_path = os.path.join(base_path, "libapp_lib.so")
lib = ctypes.CDLL(lib_path)

# FFI setup
lib.start_capture.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
lib.start_capture.restype = ctypes.c_bool

lib.get_frame.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
lib.get_frame.restype = ctypes.c_int

lib.stop_capture.restype = None


class RustCapturer:
    def __init__(self, app_name: str = "", capture_mode: str = "full_screen"):
        self.app_name = app_name.encode()
        self.capture_mode = capture_mode.encode()
        self.running = False
        self.frame_queue = queue.Queue(maxsize=2)
        self.thread = None
        self.frame_shape = (1080, 1920, 3) 
        self.buffer = np.empty(np.prod(self.frame_shape), dtype=np.uint8)

    def start_capture(self):
        success = lib.start_capture(self.app_name, self.capture_mode)
        if not success:
            raise RuntimeError("Rust capturer failed to start")

        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def _read_loop(self):
        while self.running:
            size = lib.get_frame(self.buffer.ctypes.data, self.buffer.nbytes)
            if size > 0:
                try:
                    frame = self.buffer[:size].reshape(self.frame_shape)
                    if not self.frame_queue.full():
                        self.frame_queue.put_nowait(frame.copy())
                except Exception as e:
                    print("Failed to reshape or push frame:", e)
            time.sleep(1 / 30)

    def stop_capture(self):
        self.running = False
        lib.stop_capture()
