"""Module to retrieve currently open applications across different OS platforms."""

import base64
import platform
import subprocess
import socket
import random

try:
    import psutil  # Used for Linux process retrieval
except ImportError:
    psutil = None

from xtend.capture import AppCapturer
import cv2
import numpy as np
from Xlib import display, X

def get_open_applications() -> list[str]:
    """Retrieves a list of currently open applications.

    Returns:
        list[str]: A sorted list of open application names.
    """
    system = platform.system()
    apps: set[str] = set()

    if system == 'Windows':
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        enum_windows = user32.EnumWindows  # Changed to snake_case
        enum_windows_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        is_window_visible = user32.IsWindowVisible
        get_window_text_w = user32.GetWindowTextW
        get_window_text_length_w = user32.GetWindowTextLengthW

        def enum_window_callback(hwnd, _):
            """Callback function for EnumWindows to fetch visible window titles."""
            if is_window_visible(hwnd):
                length = get_window_text_length_w(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    get_window_text_w(hwnd, buff, length + 1)
                    title = buff.value.strip()
                    if title:
                        parts = title.split(' - ')
                        apps.add(parts[-1].strip())

            return True

        enum_windows(enum_windows_proc(enum_window_callback), 0)

    elif system == 'Darwin':
        script = 'tell application "System Events" to get the name of every process where ' \
        'background only is false'
        try:
            output = subprocess.check_output(['osascript', '-e', script], text=True).strip()
            if output:
                apps.update(output.split(', '))
        except subprocess.CalledProcessError:
            pass

    elif system == 'Linux':
        try:
            from Xlib import display, X
            from Xlib.Xatom import _NET_CLIENT_LIST, _NET_WM_PID

            if not psutil:
                raise ImportError("psutil module is required for Linux application retrieval.")

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
            try:
                output = subprocess.check_output(['wmctrl', '-l'], text=True)
                for line in output.splitlines():
                    parts = line.split(maxsplit=3)
                    if len(parts) > 3:
                        title = parts[3].strip()
                        clean_parts = title.split(' - ')
                        apps.add(clean_parts[-1].strip())

            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

    # Common mapping for app normalization
    app_mapping = {
        'chrome': 'Google Chrome',
        'chrome.exe': 'Google Chrome',
        'code': 'Visual Studio Code',
        'code.exe': 'Visual Studio Code',
        'Code': 'Visual Studio Code'
    }

    processed_apps = []
    for app in sorted(apps):
        normalized = app_mapping.get(app, app)
        parts = normalized.split(' - ')
        final_name = app_mapping.get(parts[-1].strip(), parts[-1].strip())
        app_data = {"name": final_name}
        try:
            thumbnail = get_application_thumbnail(final_name)
            app_data["thumbnail"] = thumbnail
        except Exception as e:
            app_data["thumbnail"] = None
        
        processed_apps.append(app_data)

    return processed_apps

def get_application_thumbnail(app_name: str) -> str:
    """Get base64 encoded thumbnail for an application window."""
    try:
        capturer = AppCapturer(app_name)
        window_id = capturer._find_window()
        
        if not window_id:
            return None
            
        disp = display.Display()
        window = disp.create_resource_object('window', window_id)
        geom = window.get_geometry()
        
        # Capture original image
        raw = window.get_image(0, 0, geom.width, geom.height, X.ZPixmap, 0xffffffff)
        img = np.frombuffer(raw.data, dtype=np.uint8).reshape((geom.height, geom.width, 4))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # Increase target size and use better interpolation
        target_width = 320
        scale_factor = target_width / geom.width
        target_height = int(geom.height * scale_factor)
        
        frame = cv2.resize(frame, 
                          (target_width, target_height), 
                          interpolation=cv2.INTER_AREA)  # Better for downscaling

        # Encode with higher quality
        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        return base64.b64encode(buffer).decode('utf-8')
    except:
        print("Error")

def get_local_ip():
    """Get the actual local IP address of the machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    return local_ip

def generate_session_id(app_sessions: dict) -> str:
    """
    Generate a unique 4-digit session ID (0000–9999),
    retrying if there’s a collision in app_sessions.
    """
    while True:
        sid = f"{random.randint(0, 9999):04d}"
        if sid not in app_sessions:
            return sid

if __name__ == '__main__':
    print("Open applications:", get_open_applications())
