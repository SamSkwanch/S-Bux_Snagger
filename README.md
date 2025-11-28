# S-Bux Snagger

A Python automation tool that monitors the Pixel Starships game window, detects floating S-Bux using color-based detection, and automatically clicks them to collect.

## Features
- **Passive Monitoring** - Monitors the game window even when it's behind other windows
- **Color-Based Detection** - Uses precise HSV color matching to find S-Bux (no template matching)
- **Smart Filtering** - Ignores chat bubbles and UI elements through size/shape analysis
- **Auto-Click** - Briefly activates game window, clicks S-Bux, restores your previous window
- **Mouse Position Preserved** - Your cursor returns to where it was after each click
- **Simple GUI** - Start/stop buttons, activity log, and collection counter
- **Multi-Monitor Support** - Works with game on any monitor

## Requirements
- Windows 10/11
- Python 3.8+
- Pixel Starships running in a window

## Setup
1. Install Python 3.8+
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
```bash
python sbux_snagger.py
```

1. Open Pixel Starships and have your ship visible
2. Run the snagger
3. Click **Start** to begin monitoring
4. Work on other things - the snagger will collect S-Bux automatically
5. Click **Stop** when done

### How It Works
- Captures the game window content (even when behind other windows)
- Scans for the distinctive bright green S-Bux color (HSV 73-76)
- Filters out chat bubbles using size, shape, and fill ratio checks
- When S-Bux detected: briefly activates game → clicks → restores your window

### Configuration
Edit the `Config` class in `sbux_snagger.py` to adjust:
- `MONITOR_RIGHT_PORTION` - How much of screen to monitor (default: 0.75 = right 75%)
- `SBUX_HUE_LOW/HIGH` - Color range for detection
- `MIN/MAX_CONTOUR_AREA` - Size limits for detections
- `MIN/MAX_DIMENSION` - Pixel dimension limits

## Debug Tool
Run `debug_detection.py` to visualize detection in real-time:
```bash
python debug_detection.py
```
- Shows live view with detection boxes
- Press 'm' to toggle color mask view
- Press 's' to save screenshots
- Press 'q' to quit

## Building Executable
```bash
build.bat
```
Creates `dist/S-Bux Snagger.exe` (requires PyInstaller)

## Troubleshooting
- **Not detecting S-Bux**: Run `debug_detection.py` to see what's being detected
- **Clicking wrong things**: Tighten color range or size limits in Config
- **Click not registering**: Game may need to be visible briefly for click to work
- This bot is for educational purposes. Use responsibly.
- Run as Administrator if clicks aren't registering.
- The script monitors only the right half of the game window where S-Bux typically appear.
