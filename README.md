# S-Bux Snagger

S-Bux Snagger is a Python automation tool that monitors the Pixel Starships game window, detects floating S-Bux using image recognition, and automatically clicks them to collect. It uses OpenCV for image processing and pyautogui for automation.

## Features
- Detects the Pixel Starships game window
- Captures screenshots for analysis
- Uses template matching to find S-Bux (see `assets/sbux.png`)
- Simulates mouse clicks to collect S-Bux

## Setup
1. Install Python 3.8+
2. Install dependencies:
   - opencv-python
   - pyautogui
   - pillow
   - pygetwindow
3. Place a screenshot of the S-Bux in `assets/sbux.png` (already provided)

## Usage
Run `python main.py` while Pixel Starships is open and visible on your desktop.

## Notes
- This bot is for educational purposes. Use responsibly.
- You may need to adjust template matching thresholds for best results.
