import re
import subprocess
import threading
import time
import cv2
import numpy as np
from Xlib import display, X
from Xlib.ext import composite
from Xlib.protocol import request

class AppCapturer:
    def __init__(self, app_name):
        self.app_name = app_name
        print(app_name)
        self.running = False
        self.frame = None
        self.capture_thread = None
        self.disp = None
        self.window = None
        self.composite_opcode = None

    def _find_window(self):
        """Get window ID using wmctrl"""
        try:
            output = subprocess.check_output(['wmctrl', '-l']).decode()
            window_lines = [line for line in output.split('\n') 
                          if self.app_name in line]
            if not window_lines:
                return None
            return int(window_lines[0].split()[0], 16)
        except Exception as e:
            print(f"Window finding failed: {e}")
            return None

    def start_capture(self):
        """Start capturing window using XComposite"""
        window_id = self._find_window()
        if not window_id:
            raise RuntimeError(f"Window for {self.app_name} not found")

        self.disp = display.Display()
        self._init_composite()
        
        self.window = self.disp.create_resource_object('window', window_id)
        
        # Redirect window to off-screen storage
        composite.redirect_window(self.window, composite.RedirectManual)
        self.disp.sync()

        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.start()

    def _init_composite(self):
        """Initialize Composite extension"""
        if not self.disp.has_extension('Composite'):
            raise RuntimeError("XComposite extension not available")
        
        # Get Composite extension details
        self.composite_opcode = self.disp.get_extension('Composite').major_opcode

    def _capture_loop(self):
        """Main capture loop using XComposite"""
        try:
            while self.running:
                try:
                    # Get window geometry
                    geom = self.window.get_geometry()
                    
                    # Create temporary pixmap
                    pixmap = self.disp.screen().root.create_pixmap(
                        geom.width, geom.height, self.disp.screen().root_depth
                    )
                    
                    # Copy window contents to pixmap
                    composite.name_window_pixmap(self.window, pixmap)
                    self.disp.sync()
                    
                    # Get pixmap data
                    image = pixmap.get_image(0, 0, geom.width, geom.height, X.ZPixmap, 0xffffffff)
                    
                    # Convert to numpy array
                    img = np.frombuffer(image.data, dtype=np.uint8)
                    img = img.reshape((geom.height, geom.width, 4))  # BGRA format
                    self.frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    
                    pixmap.free()
                    time.sleep(0.033)
                except X.Error as e:
                    print(f"X11 error: {e}")
                    break
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        if self.window:
            composite.unredirect_window(self.window)
            self.disp.sync()
        if self.disp:
            self.disp.close()

    def stop_capture(self):
        """Stop capturing"""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join()
        self.cleanup()


if __name__ == '__main__':
    capturer = AppCapturer("Visual Studio Code")
    capturer.start_capture()