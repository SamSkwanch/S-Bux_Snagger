# S-Bux Snagger - Copilot Instructions

## Project Overview
S-Bux Snagger is a Python automation tool for the game Pixel Starships that:
- Monitors the game window in the background (works while behind other windows)
- Uses color-based HSV detection to find floating S-Bux icons
- Filters out chat bubbles using size/shape analysis
- Briefly activates game window to click, then restores focus

## Tech Stack
- Python 3.8+
- OpenCV (cv2) for color-based image processing
- pywin32 for background window capture (PrintWindow API) and mouse automation
- pygetwindow for window detection
- Pillow (PIL) for image handling
- tkinter for GUI

## Key Files
- `sbux_snagger.py` - Main GUI application with color detection
- `debug_detection.py` - Real-time detection visualization tool
- `build.bat` - PyInstaller build script
- `requirements.txt` - Python dependencies

## Development Notes
- Uses HSV color matching (hue 73-76) instead of template matching
- Filters: contour area (100-800), dimensions (8-70px), aspect ratio (0.6-1.7), fill ratio (30%+)
- Background window capture via Win32 PrintWindow API
- Clicks require brief window activation (game ignores simulated input)
- Mouse position preserved during click operations

## Running the Project
```bash
# Install dependencies
pip install -r requirements.txt

# Run the GUI app
python sbux_snagger.py

# Run debug visualization
python debug_detection.py
```

## Building Executable
```bash
# Run the build script
build.bat
# Output: dist/S-Bux Snagger.exe
```

