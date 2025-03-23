import platform
import subprocess
import threading
import re
import time
import cv2
import mss
import numpy as np

def get_open_applications():
    system = platform.system()
    apps = set()

    if system == 'Windows':
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        EnumWindows = user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        GetWindowThreadProcessId = user32.GetWindowThreadProcessId
        IsWindowVisible = user32.IsWindowVisible
        GetWindowTextW = user32.GetWindowTextW
        GetWindowTextLengthW = user32.GetWindowTextLengthW

        def enum_window_callback(hwnd, lParam):
            if IsWindowVisible(hwnd):
                # Get window title
                length = GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value
                    if title:
                        # Extract potential app name from title
                        parts = [p.strip() for p in title.split(' - ')]
                        apps.add(parts[-1])
            return True

        EnumWindows(EnumWindowsProc(enum_window_callback), 0)

    elif system == 'Darwin':
        script = 'tell application "System Events" to get the name of every process where background only is false'
        try:
            output = subprocess.check_output(['osascript', '-e', script]).decode('utf-8').strip()
            apps = set(output.split(', '))
        except subprocess.CalledProcessError:
            pass

    elif system == 'Linux':
        try:  # Try Xlib method first
            from Xlib import display, X
            from Xlib.Xatom import _NET_CLIENT_LIST, _NET_WM_PID
            
            d = display.Display()
            root = d.screen().root
            client_list = root.get_full_property(_NET_CLIENT_LIST, X.AnyPropertyType)
            
            if client_list:
                for win_id in client_list.value:
                    window = d.create_resource_object('window', win_id)
                    pid_prop = window.get_full_property(_NET_WM_PID, X.AnyPropertyType)
                    if pid_prop:
                        pid = pid_prop.value[0]
                        try:
                            process = psutil.Process(pid)
                            apps.add(process.name())
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
        except ImportError:
            try:  # Fallback to wmctrl
                output = subprocess.check_output(['wmctrl', '-l']).decode('utf-8')
                for line in output.splitlines():
                    parts = line.split(maxsplit=3)
                    if len(parts) > 3:
                        title = parts[3]
                        # Extract potential app name from title
                        clean_parts = [p.strip() for p in title.split(' - ')]
                        apps.add(clean_parts[-1])
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

    # Common processing and mapping
    app_mapping = {
        'chrome': 'Google Chrome',
        'chrome.exe': 'Google Chrome',
        'code': 'Visual Studio Code',
        'code.exe': 'Visual Studio Code',
        'Code': 'Visual Studio Code'
    }
    
    processed_apps = set()
    for app in apps:
        # Try to find in mapping first
        normalized = app_mapping.get(app, app)
        # Additional check for split results
        parts = [p.strip() for p in normalized.split(' - ')]
        final_name = app_mapping.get(parts[-1], parts[-1])
        processed_apps.add(final_name)

    return sorted(processed_apps)


class AppCapturer:
    def __init__(self, app_name):
        self.app_name = app_name
        self.running = False
        self.frame = None
        self.capture_thread = None
        self.system = platform.system()
        self.geometry = None

    def find_window_geometry(self):
        """Find application window geometry for current platform"""
        if self.system == 'Windows':
            return self._find_window_windows()
        elif self.system == 'Darwin':
            return self._find_window_mac()
        elif self.system == 'Linux':
            return self._find_window_linux()
        return None

    def start_capture(self):
        """Start capturing frames in background thread"""
        self.geometry = self.find_window_geometry()
        print(self.geometry)
        if not self.geometry:
            raise RuntimeError("Could not find application window")
        
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.start()

    def stop_capture(self):
        """Stop capturing frames"""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join()

    def _capture_loop(self):
        """Main capture loop using MSS"""
        with mss.mss() as sct:
            monitor = {
                "top": self.geometry['top'],
                "left": self.geometry['left'],
                "width": self.geometry['width'],
                "height": self.geometry['height']
            }
            sct.shot(output="test.png")

            while self.running:
                try:
                    img = sct.grab(monitor)
                    self.frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGRA2BGR)
                except Exception as e:
                    print(f"Capture error: {e}")
                time.sleep(0.033)  # ~30 FPS

    # Windows implementation
    def _find_window_windows(self):
        import win32gui
        import win32con
        import win32api

        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if self.app_name.lower() in title.lower():
                    rect = win32gui.GetWindowRect(hwnd)
                    extra.append({
                        'left': rect[0],
                        'top': rect[1],
                        'width': rect[2] - rect[0],
                        'height': rect[3] - rect[1],
                        'hwnd': hwnd
                    })
            return True

        windows = []
        win32gui.EnumWindows(callback, windows)
        
        if not windows:
            return None

        # Bring window to front
        hwnd = windows[0]['hwnd']
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)

        return windows[0]

    # macOS implementation
    def _find_window_mac(self):
        script = f'''
        tell application "System Events"
            set appProcess to first process whose name is "{self.app_name}"
            set windowPos to position of first window of appProcess
            set windowSize to size of first window of appProcess
            return {{windowPos, windowSize}}
        end tell
        '''
        
        try:
            result = subprocess.check_output(['osascript', '-e', script]).decode()
            numbers = list(map(int, re.findall(r'\d+', result)))
            
            if len(numbers) >= 4:
                # Adjust for retina displays
                scale_factor = subprocess.check_output([
                    'system_profiler', 'SPDisplaysDataType'
                ]).decode()
                scale = 2 if 'Retina' in scale_factor else 1
                
                return {
                    'left': numbers[0] // scale,
                    'top': numbers[1] // scale,
                    'width': numbers[2] // scale,
                    'height': numbers[3] // scale
                }
        except Exception as e:
            print(f"macOS window detection failed: {e}")
        return None

    # Linux implementation
    def _find_window_linux(self):
        try:
            # Get window ID using wmctrl (more reliable)
            output = subprocess.check_output(
                ['wmctrl', '-l'], timeout=5).decode()
            window_lines = [line for line in output.split('\n') 
                        if self.app_name in line]
            if not window_lines:
                return None

            # Get the first matching window ID
            window_id = window_lines[0].split()[0]

            # Get geometry using xwininfo
            xwininfo = subprocess.check_output(
                ['xwininfo', '-id', window_id], timeout=5).decode()

            # Extract absolute coordinates
            abs_x = int(re.search(r'Absolute upper-left X:\s+(\d+)', xwininfo).group(1))
            abs_y = int(re.search(r'Absolute upper-left Y:\s+(\d+)', xwininfo).group(1))
            
            # Extract window dimensions
            width = int(re.search(r'Width:\s+(\d+)', xwininfo).group(1))
            height = int(re.search(r'Height:\s+(\d+)', xwininfo).group(1))

            # Adjust for multi-monitor setups
            screen_info = subprocess.check_output(['xrandr']).decode()
            primary_screen = [line for line in screen_info.split('\n') 
                            if ' connected primary' in line][0]
            screen_x = int(re.search(r'primary (\d+)x(\d+)\+(\d+)\+(\d+)', 
                                primary_screen).group(3))

            return {
                'left': abs_x - screen_x,  # Adjust for primary monitor offset
                'top': abs_y,
                'width': width,
                'height': height
            }
        except Exception as e:
            print(f"Linux window detection failed: {e}")
            return None

if __name__ == '__main__':
    print("Open applications:", get_open_applications())

    ap = AppCapturer('Google Chrome')
    ap.start_capture()
    print(ap.frame)