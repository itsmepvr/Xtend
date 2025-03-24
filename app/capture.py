import subprocess
import threading
import time
import cv2
import numpy as np
from Xlib import display, X
from Xlib.ext import composite
from Xlib.error import XError

class AppCapturer:
    def __init__(self, app_name):
        self.app_name = app_name
        self.running = False
        self.frame = None
        self.capture_thread = None
        self.disp = None
        self.window = None
    
    def _find_window(self):
        """Find window using wmctrl"""
        try:
            output = subprocess.check_output(['wmctrl', '-l']).decode()
            for line in output.split('\n'):
                parts = line.split(None, 3)
                if len(parts) == 4 and self.app_name.lower() in parts[3].lower():
                    return int(parts[0], 16)  # Convert window ID to integer
        except Exception as e:
            print(f"Window finding failed: {e}")
        return None

    def _init_composite(self):
        """Ensure Composite extension is enabled"""
        ext_info = self.disp.query_extension('Composite')
        if not ext_info.present:
            raise RuntimeError("XComposite extension not available")

    def start_capture(self):
        """Start capturing the application's window"""
        window_id = self._find_window()
        if not window_id:
            raise RuntimeError(f"Window for '{self.app_name}' not found")

        self.disp = display.Display()
        self._init_composite()
        self.window = self.disp.create_resource_object('window', window_id)

        # Redirect window to an off-screen pixmap
        composite.redirect_window(self.window, composite.RedirectManual)
        self.disp.sync()  # Ensure X operations are applied

        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()

    def _capture_loop(self):
        """Main capture loop"""
        try:
            while self.running:
                try:
                    geom = self.window.get_geometry()
                    image = self.window.get_image(0, 0, geom.width, geom.height, X.ZPixmap, 0xffffffff)

                    if image:
                        img = np.frombuffer(image.data, dtype=np.uint8)
                        img = img.reshape((geom.height, geom.width, 4))  # RGBA format
                        self.frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                except XError:
                    print("X11 Error: Window may have closed.")
                    break  # Exit the loop if the window is invalid

                time.sleep(0.033)  # Maintain 30 FPS

        except Exception as e:
            print(f"Unexpected error in capture loop: {e}")

    def cleanup(self):
        """Release resources properly without crashing"""
        if self.window:
            try:
                composite.unredirect_window(self.window, composite.RedirectManual)
            except XError:
                pass  # Ignore X errors if the window is already gone

        if self.disp:
            try:
                self.disp.sync()  # Ensure all commands are processed
                self.disp.close()  # Close the display connection properly
            except XError:
                pass  # Ignore errors if display is already invalid
            except Exception as e:
                print(f"Warning: Failed to close X display: {e}")

        self.window = None
        self.disp = None  # Ensure object references are cleared

    def stop_capture(self):
        """Stop capturing without blocking indefinitely"""
        self.running = False  # Signal the thread to stop
        if self.capture_thread:
            self.capture_thread.join(timeout=2)  # Prevent infinite blocking
            if self.capture_thread.is_alive():
                print("Warning: Capture thread did not terminate properly.")

        self.cleanup()

if __name__ == '__main__':
    capturer = AppCapturer("Visual Studio Code")
    capturer.start_capture()
