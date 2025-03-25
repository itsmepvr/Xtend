import platform
import subprocess

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
        try:
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

if __name__ == '__main__':
    print("Open applications:", get_open_applications())

    ap = AppCapturer('Google Chrome')
    ap.start_capture()
    print(ap.frame)