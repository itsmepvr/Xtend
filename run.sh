#!/bin/bash

# Clear the terminal
clear

# Run the Python script with the specified mode (default: qt)
MODE=${1:-qt}

python run.py --mode "$MODE"