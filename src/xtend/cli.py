import argparse
from xtend import start_application

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["qt","web"], default="qt")
    args = parser.parse_args()
    start_application(mode=args.mode)

if __name__ == "__main__":
    main()
