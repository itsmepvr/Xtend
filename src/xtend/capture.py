"App screen capture module"
import subprocess
import threading
import time
import queue
import cv2
import numpy as np
from Xlib import display, X
from Xlib.ext import composite
from Xlib.error import XError

class AppCapturer:
    """Captures the screen of a specific application window using X11 and Composite extension."""

    def __init__(self, app_name: str = None, capture_mode: str = 'app'):
        """Initialize the AppCapturer with the application name or capture mode."""
        if capture_mode not in ['app', 'full_screen']:
            raise ValueError("Invalid capture mode. Use 'app' or 'full_screen'.")
        self.capture_mode = capture_mode
        if self.capture_mode == 'app' and not app_name:
            raise ValueError("app_name is required for 'app' capture mode.")
        
        self.app_name = app_name
        self.running = False
        self.frame_queue = queue.Queue(maxsize=2)
        self.capture_thread = None
        self.disp = None
        self.window = None
        self.redirected = False

    def _find_window(self) -> int | None:
        """Find the application window ID using wmctrl."""
        try:
            output = subprocess.check_output(['wmctrl', '-l'], text=True)
            for line in output.splitlines():
                parts = line.split(None, 3)
                if len(parts) == 4 and self.app_name.lower() in parts[3].lower():
                    return int(parts[0], 16)  # Convert hex window ID to integer
        except subprocess.CalledProcessError as e:
            print(f"Error finding window: {e}")
        except ValueError:
            print("Failed to parse window ID.")
        return None

    def _init_composite(self) -> None:
        """Ensure XComposite extension is enabled."""
        ext_info = self.disp.query_extension('Composite')
        if not ext_info.present:
            raise RuntimeError("XComposite extension is not available on this system.")

    def start_capture(self) -> None:
        """Start capturing the application's window or full screen."""
        if self.capture_mode == 'app':
            window_id = self._find_window()
            if not window_id:
                raise RuntimeError(f"Window for '{self.app_name}' not found")

            self.disp = display.Display()
            self._init_composite()
            self.window = self.disp.create_resource_object('window', window_id)
            composite.redirect_window(self.window, composite.RedirectManual)
            self.redirected = True
            self.disp.sync()
        else:
            # Full screen mode
            self.disp = display.Display()
            self.window = self.disp.screen().root  # Root window
            self.disp.sync()

        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()

    def _capture_loop(self) -> None:
        """Captures frames and adds them to the queue."""
        try:
            geom = self.window.get_geometry()  # Fetch geometry once
            while self.running:
                start_time = time.time()
                try:
                    image = self.window.get_image(0, 0, geom.width,
                                                  geom.height, X.ZPixmap, 0xffffffff)
                    if image:
                        img = np.frombuffer(image.data, dtype=np.uint8) \
                        .reshape((geom.height, geom.width, 4))
                        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                        if not self.frame_queue.full():
                            self.frame_queue.put_nowait(frame)

                except XError:
                    print("X11 Error: Window may have closed or is inaccessible.")
                    break

                elapsed = time.time() - start_time
                time.sleep(max(0, (1 / 30) - elapsed))  # Adaptive frame rate control

        except Exception as e:
            print(f"Unexpected error in capture loop: {e}")

    def cleanup(self) -> None:
        """Release resources properly."""
        if self.redirected and self.window:
            try:
                composite.unredirect_window(self.window, composite.RedirectManual)
            except XError:
                pass

        if self.disp:
            try:
                self.disp.sync()
                self.disp.close()
            except XError:
                pass
            except Exception as e:
                print(f"Warning: Failed to close X display: {e}")

        self.window = None
        self.disp = None

    def stop_capture(self) -> None:
        """Stop capturing without blocking indefinitely."""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        if self.process_thread:
            self.process_thread.join(timeout=2)

        self.cleanup()

if __name__ == '__main__':
    capturer = AppCapturer("Google Chrome")
    capturer.start_capture()
