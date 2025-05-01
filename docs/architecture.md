# Xtend Screen - Architecture Overview

Xtend is a cross-platform screen sharing tool that turns any browser-enabled device into a real-time secondary screen for your desktop. It combines a Rust-powered screen capture engine with a FastAPI backend and a Qt GUI frontend.

## System Components

### 1. **Rust Capture Engine**

- Built with X11, OpenCV, and FFI (cdylib)
- Provides real-time image capture from root or window-specific surfaces
- Exposes C-compatible interface to Python
- Resize and encode frames using OpenCV for consistent resolution (e.g., 1920x1080)

### 2. **Python Backend (FastAPI)**

- API endpoints for UI, app list, and stream control
- Serves HTML templates, JS, and WebSockets
- Dynamically generates and manages app URLs for sharing
- Loads .env via Pydantic configuration

### 3. **Qt GUI (Frontend Wrapper)**

- Embedded QWebEngineView loading FastAPI UI
- Provides a native app feel with browser functionality inside a Qt window
- Used as the default UX for xtend

### 4. **Static Web Interface**

- Bootstrap-based responsive layout
- Device-agnostic access
- Indexed app windows and live MJPEG stream rendering

## 🖥️ System Design Diagram

```
  +-----------------+       +----------------------+      +-----------------+
  |                 | FFI   |                      | API  |                 |
  | Rust Capture    | <----> Python FastAPI Server | <--> | HTML / JS Front |
  | (X11 / OpenCV)  |       |  (App list, stream)  |      |   Browser or Qt |
  |                 |       |                      |      |                 |
  +-----------------+       +----------------------+      +-----------------+
                                  |          ^
                                  |          |
                             +--------+  +----------+
                             |  Qt UI |  | Web UI   |
                             +--------+  +----------+
```

## ⚙️ Technology Stack

LayerTechCapture CoreRust + X11 + OpenCVWeb BackendPython 3.11 + FastAPIWeb ServerUvicorn (ASGI)Frontend UIBootstrap + JSDesktop UIPyQt5 + QWebEngineViewPackagingPyInstaller, NSIS, AppImageConfigPydantic + .env

## 📊 Screen Capture Comparison

| Capture Method | Language | Latency | CPU Usage | Resolution Support | Notes |
| Python + Xlib + X11 | Python | High | High | Limited by PIL | Easy, but slow for real-time |
| Python + Composite | Python | Medium | Medium | Acceptable | More flexible but still limited |
| Rust + X11 + OpenCV | Rust | Low | Low | Full HD / 4K | Best perf for X11-based systems |
| Rust + Pipewire (todo) | Rust | Lowest | Lowest | 4K+ | Best modern option (Wayland) |

> Xtend uses Rust + X11/OpenCV as it's the most stable and performant on X11 systems. Future support will include PipeWire for Wayland and macOS/Windows native APIs.

## 🔍 Extensibility

- **Multi-client Streaming**: WebSocket broadcast planned
- **Wayland/PipeWire Support**: Under exploration for modern Linux distros
- **Recording**: Optional future module for local recording
- **Compression Optimization**: WebP or H.264 encoding for better perf

## 🔐 Security Considerations

- Randomized app share URLs (UUID-based)
- No access to window content unless selected
- Secrets managed via .env (SECRET_KEY, etc.)
- HTTPS deployment required for production use

## 🛠️ Build Pipeline Highlights

- GitHub Actions (ci-cd-pipeline.yml, release.yml)
- Linux: AppImage, .deb builds
- Windows: NSIS installer
- macOS: .dmg support
- Multi-platform PyInstaller
- Rust shared library built and used via FFI

## 📁 Directory Summary

```
Xtend/
├── app_capturer/     # Rust workspace (lib + test binary)
├── src/xtend/        # Python FastAPI + GUI entrypoint
├── packaging/        # .desktop, Windows installer scripts
├── scripts/          # Build automation
├── windows/          # Platform-specific configs
├── docs              # Architecture docs
```

## Roadmap

- ✅ Rust FFI + OpenCV live streaming
- 🔜 PipeWire capture for Wayland
- 🔜 Auth-protected session sharing
- 🔜 Extend Qt frontend with tray menu / controls
- 🔜 Browser-based control panel for session hosts
