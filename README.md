# Xtend

Xtend Screen turns any web-enabled device into a secondary screen for your computer by capturing desktop applications and streaming them in real time via a FastAPI-powered backend with Rust-based performance enhancements.

## Features

- **Real-Time Screen Sharing:** Capture and stream any desktop application window.

- **Device Flexibility:** Access shared screens from smartphones, tablets, or any browser-enabled device.

- **Rust-Powered Capture:** High-performance screen capture via Rust FFI using X11 and OpenCV.

- **FastAPI Integration:** Ultra-fast API serving and web interface via FastAPI + Uvicorn.

- **Dynamic URL Sharing:** Unique URLs generated for each shared application.

- **Cross-Platform:** Portable and installable on Linux, macOS, and Windows.

## Requirements

- Python 3.x
- FastAPI
- Uvicorn (ASGI server for FastAPI)
- Rust + Cargo
- Xlib, Composite (Linux)
- `pyobjc` (on macOS) or equivalent packages for other platforms

## Installation

#### Prerequisites (OS‑level)

Before installing Python dependencies, ensure your system has the native X11 Composite libraries and utilities:

- **Linux (X11/Composite):**
  ```
   sudo apt-get update
   sudo apt-get install -y wmctrl x11-utils libxcomposite-dev libxrender-dev
   sudo apt install llvm-dev libclang-dev clang pkg-config libopencv-dev
   sudo apt install libopencv-dev
  ```
- macOS (for screen capture support via PyObjC):
  ```
   brew update
   brew install imagemagick  # install any additional native libs if needed
  ```

You can install and run Xtend Screen via pip + setuptools or Poetry. Choose the workflow that suits you.

#### A. Using Poetry (recommended)

```
git clone https://github.com/itsmepvr/Xtend.git
cd Xtend
pip install poetry
poetry install
poetry shell
xtend  # launches Qt + FastAPI
```

#### B. Using pip + setuptools

```
git clone https://github.com/itsmepvr/Xtend.git
cd Xtend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
xtend
```

To run only the Web API server:

```
xtend --mode web
```

## Configuration

1. Copy the example file and fill in secret values:
   ```
   cp .env.example .env
   ```
2. Edit (project root):
   ```
   DEBUG=True
   HOST=0.0.0.0
   PORT=4563
   SECRET_KEY=your-secret-key
   ```

## Usage

#### Qt GUI Mode (default)

```
xtend           # Launches Qt application + FastAPI server
```

#### Web Mode (API only)

```
xtend --mode web    # Starts FastAPI server without Qt
```

#### Direct Uvicorn (development)

```
uvicorn xtend.server:app --host 0.0.0.0 --port 9999 --reload
```

Open your browser at http://127.0.0.1:9999 to view available applications.

## Building Rust FFI (Required)

```
cd app_capturer
cargo build --release -p app_lib
```

This generates the shared library `(libapp_capturer.so / .dll / .dylib)` used by the Python layer.

## Contributing

We welcome contributions! Please follow the branching convention:

- `feature/your-feature-name`

- `bug-fix/your-bug-description`

- `other/chore-or-doc-task`

## How It Works

- Home page lists open windows.

- App selection generates a unique stream URL.

- Screen is captured via Rust/X11/OpenCV.

- Frames are streamed to the browser in real-time.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the web framework.
- [Uvicorn](https://www.uvicorn.org/) for running the FastAPI app (ASGI server).
- [Xlib](https://pypi.org/project/python-xlib/) for interacting with the X11 display server.
- [Composite Extension](https://www.x.org/wiki/) for capturing the application windows.

## Author

Developed by [Venkata Ramana, P](https://github.com/itsmepvr).
