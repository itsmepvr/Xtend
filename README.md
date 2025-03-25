# Xtend Screen

This project enables any device with a web browser to be used as a secondary screen for your computer. It captures the screen of specific applications running on the desktop and streams them to a browser for display. Developed using Python and Flask, it uses Xlib, Composite, and Display to capture the application’s screen in real-time and provide an interactive user experience.

## Features

- **Screen Sharing**: View and interact with any open application on your desktop directly in your browser.
- **Device Flexibility**: Use any device with a web browser as a secondary screen for your computer.
- **Real-Time Streaming**: Stream your selected application’s screen in real-time with minimal delay.
- **Dynamic URL Generation**: Each application is assigned a unique URL for easy access and sharing.

## Requirements

- Python 3.x
- Flask
- Xlib
- Python-Xlib
- Composite extension for X11
- `pyobjc` (on macOS) or equivalent packages for other platforms

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/itsmepvr/Xtend.git
cd Xtend
```

### 2. Install Dependencies

Install the necessary Python packages using `pip`:

```bash
pip install -r requirements.txt
```

### 3. Set Up Xlib and Composite

Ensure that you have the necessary dependencies for screen capturing:

- **For Linux**: Install Xlib and Composite extension packages.

  ```bash
  sudo apt-get install wmctrl x11-utils xrandr libxcomposite-dev libxrender-dev
  ```

- **For macOS**: Ensure that you have the appropriate libraries for screen capturing and display.

### 4. Run the Flask Application

Start the Flask server to begin capturing and streaming the screens.

```bash
python run.py
```

By default, the app will be accessible at `http://127.0.0.1:9999`.

## Test Cases

Test cases are in `tests` folder. Run test cases using below command:

```bash
PYTHONPATH=$(pwd) pytest
```

## How It Works

1. **Home Page**: The home page lists all the open applications on the desktop.
2. **URL Generation**: Upon selecting an application, a unique URL is generated with a query parameter (e.g., `?app_id=12345`).
3. **Screen Capture**: The Flask app uses Xlib, Composite, and Display libraries to capture the screen of the selected application.
4. **Web Streaming**: The captured screen is then streamed to the web browser in real-time.

## Contributing

We welcome contributions to improve the functionality and features of the Secondary Screen project. To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to your forked repository (`git push origin feature-branch`).
6. Create a pull request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [Xlib](https://pypi.org/project/python-xlib/) for interacting with the X11 display server.
- [Composite Extension](https://www.x.org/wiki/) for capturing the application windows.
