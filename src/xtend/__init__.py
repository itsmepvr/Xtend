"Main file"
import threading
import sys
import uvicorn
from PySide6.QtWidgets import QApplication
from xtend.gui import XtendScreenQt
from xtend.app import app
from xtend.config import settings

__version__ = "0.0.1"

def start_application(mode:str="qt"):
    "Qt application with fastapi server"
    if mode == "web":
        run_fastapi()
    else:
        fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
        fastapi_thread.start()

        qt = QApplication(sys.argv)
        window = XtendScreenQt()
        window.show()
        sys.exit(qt.exec())

def run_fastapi():
    "FastAPI server"
    uvicorn.run(
        "xtend.app:app",
        host=settings.HOST,
        port=settings.PORT
    )
