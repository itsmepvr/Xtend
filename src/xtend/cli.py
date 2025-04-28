import argparse
from xtend import start_application

# import os
# os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"
# from PyQt5.QtCore import Qt, QCoreApplication
# QCoreApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["qt","web"], default="qt")
    args = parser.parse_args()
    start_application(mode=args.mode)

if __name__ == "__main__":
    main()
