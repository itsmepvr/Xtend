"Qt Application Module"
import sys
import time
import requests
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
from xtend.config import settings

FASTAPI_URL = f"http://{settings.HOST}:{settings.PORT}"

class XtendScreenQt(QWidget): # pylint: disable=too-few-public-methods
    """Qt Application with embedded FastAPI UI"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xtend - Screen Share")
        self.setGeometry(100, 100, 1024, 768)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # WebEngineView to display FastAPI Web UI
        self.web_view = QWebEngineView()
        self.wait_for_fastapi()
        self.web_view.setUrl(QUrl(FASTAPI_URL))
        self.web_view.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(self.web_view)
        self.setLayout(self.layout)

    def wait_for_fastapi(self, timeout=5):
        """Wait until FastAPI server is ready."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://{settings.HOST}:{settings.PORT}", timeout=5)
                if response.status_code == 200:
                    return  # Server is ready
            except requests.exceptions.ConnectionError:
                time.sleep(0.5)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = XtendScreenQt()
    window.show()
    sys.exit(app.exec())
