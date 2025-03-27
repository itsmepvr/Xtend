"Main file"
import threading
import sys
import uvicorn
from PySide6.QtWidgets import QApplication
from app.qt_xtend import XtendScreenQt
from app.server import app
from config import Config

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
    uvicorn.run(app, host=Config.HOST, port=Config.PORT, log_level="info")
