# Xtend

Extend any device with a web browser into a secondary screen for your computer. Xtend Screen captures the display of selected desktop applications in real time and streams them via a FastAPI server.

## Features

- **Screen Sharing:** Capture and stream any open application window on your desktop.

- **Device Flexibility:** Use smartphones, tablets, or any web‑enabled device as a secondary display.

- **Real-Time Performance:** Low‑latency streaming powered by FastAPI and Uvicorn.

- **Dynamic URL Generation:** Each shared application receives a unique URL for easy access.

- **Cross‑Platform Ready:** Works on Linux (X11/Composite), macOS (via pyobjc), and Windows (future support).

## Requirements

- Python 3.x
- FastAPI
- Uvicorn (ASGI server for FastAPI)
- Xlib
- Python-Xlib
- Composite extension for X11
- `pyobjc` (on macOS) or equivalent packages for other platforms

## Installation

#### Prerequisites (OS‑level)

Before installing Python dependencies, ensure your system has the native X11 Composite libraries and utilities:

- **Linux (X11/Composite):**
  ```
  sudo apt-get update
  sudo apt-get install -y wmctrl x11-utils libxcomposite-dev libxrender-dev
  ```
- macOS (for screen capture support via PyObjC):
  ```
  brew update
  brew install imagemagick  # install any additional native libs if needed
  ```

You can install and run Xtend Screen via pip + setuptools or Poetry. Choose the workflow that suits you.

#### A. Using Poetry (recommended)

1. Clone the repository:

   ```
   git clone https://github.com/itsmepvr/Xtend.git
   cd Xtend
   ```

2. Install Poetry (if not already):
   ```
   pip install poetry
   ```
3. Install dependencies & create venv:
   ```
   poetry install
   ```
4. Activate the Poetry shell:
   ```
   poetry shell
   ```
5. Run the application (Qt GUI + FastAPI server):
   ```
   xtend
   ```

#### B. Using pip + setuptools

1. Clone the repository:
   ```
   git clone https://github.com/itsmepvr/Xtend.git
   cd Xtend
   ```
2. Create and activate a virtual environment:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Install the package:
   ```
   pip install -e .
   ```
5. Run the application (Qt GUI + FastAPI server):
   ```
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
3. Add .env to .gitignore:
   `   .env`
   Xtend loads settings via Pydantic’s BaseSettings, reading `.env` automatically.

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

## Packaging Executables

#### Build scripts

A sample build script is available at `scripts/build_exe.sh`:

```
#!/usr/bin/env bash
pyinstaller --onefile --name xtend-qt src/xtend/cli.py --windowed
pyinstaller --onefile --name xtend-web src/xtend/cli.py --add-data "src/xtend/static:static" --add-data "src/xtend/templates:templates"
```

Run:

```
bash scripts/build_exe.sh
```

Binaries will be in `dist/` for distribution.

## Test Cases

Test cases are in the `tests` folder. Run test cases using the following command:

```bash
PYTHONPATH=$(pwd) pytest
```

## How It Works

1. **Home Page**: The home page lists all the open applications on the desktop.
2. **URL Generation**: Upon selecting an application, a unique URL is generated with a query parameter (e.g., `?app_id=12345`).
3. **Screen Capture**: The FastAPI app uses Xlib, Composite, and Display libraries to capture the screen of the selected application.
4. **Web Streaming**: The captured screen is then streamed to the web browser in real-time.

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.

2. Create a new branch: git checkout -b feature/my-new-feature.

3. Install dependencies and run tests.

4. Make your changes and commit: git commit -m "Add awesome feature".

5. Push to your fork: git push origin feature/my-new-feature.

6. Open a Pull Request and describe your changes.

7. Please adhere to the existing code style and keep feature branches focused.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the web framework.
- [Uvicorn](https://www.uvicorn.org/) for running the FastAPI app (ASGI server).
- [Xlib](https://pypi.org/project/python-xlib/) for interacting with the X11 display server.
- [Composite Extension](https://www.x.org/wiki/) for capturing the application windows.

## Author

Developed by [Venkata Ramana, P](https://github.com/itsmepvr).
