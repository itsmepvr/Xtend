"Run file --args"
import argparse
from app import start_application

def main():
    parser = argparse.ArgumentParser(description="Choose application mode: Qt or Web")
    parser.add_argument("--mode", choices=["qt", "web"],
                        default="qt", help="Run in Qt mode or Web mode (default: qt)")

    args = parser.parse_args()

    if args.mode == "web":
        start_application(mode='web')
    else:
        start_application(mode='qt')

if __name__ == "__main__":
    main()
