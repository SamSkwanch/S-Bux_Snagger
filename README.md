# S-Bux Snagger

A tool that monitors the Pixel Starships game window and detects floating S-Bux using color-based detection. Available in two versions to suit different playstyles.

## Versions

### 🤖 S-Bux Snagger (Full Automation)
Automatically detects **and collects** S-Bux for you. Runs in the background and briefly switches to the game to click, then restores your previous window.

**Download:** `S-Bux Snagger.exe`

### 🔔 S-Bux Snagger Alert (Alert Mode)
Detects S-Bux and **plays a sound alert** instead of auto-clicking. Perfect for players who prefer to collect manually but don't want to constantly watch their screen.

**Download:** `S-Bux Snagger Alert.exe`

---

## Features (Both Versions)
- **Background Monitoring** - Works even when the game is behind other windows
- **Color-Based Detection** - Precise HSV color matching to find S-Bux
- **Smart Filtering** - Ignores chat bubbles and UI elements
- **Simple GUI** - Start/stop buttons, activity log, and counter
- **Multi-Monitor Support** - Works with game on any monitor

### Full Automation Only
- **Auto-Click** - Briefly activates game window, clicks S-Bux, restores your window
- **Mouse Position Preserved** - Cursor returns to where it was after each click

### Alert Mode Only
- **Sound Alerts** - Plays custom sound when S-Bux detected
- **No Auto-Clicking** - Your mouse and windows are never touched
- **Alert Cooldown** - 3-second cooldown prevents alert spam

---

## Quick Start (Executable)
1. Download the `.exe` for your preferred version
2. Open Pixel Starships and have your ship visible
3. Run the executable
4. Click **Start** to begin monitoring
5. Click **Stop** when done

## Requirements
- Windows 10/11
- Pixel Starships running in a window

---

## Development Setup
For running from source or contributing:

1. Install Python 3.8+
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python sbux_snagger.py
   ```

### Configuration
Edit the `Config` class in `sbux_snagger.py` to adjust:
- `MONITOR_RIGHT_PORTION` - How much of screen to monitor (default: 0.75 = right 75%)
- `SBUX_HUE_LOW/HIGH` - Color range for detection
- `MIN/MAX_CONTOUR_AREA` - Size limits for detections
- `ALERT_COOLDOWN` - Seconds between alerts (Alert Mode only)

### Debug Tool
Run `debug_detection.py` to visualize detection in real-time:
```bash
python debug_detection.py
```
- Shows live view with detection boxes
- Press 'm' to toggle color mask view
- Press 's' to save screenshots
- Press 'q' to quit

### Building Executables
```bash
# Full automation version
pyinstaller --onefile --windowed --name "S-Bux Snagger" sbux_snagger.py

# Alert mode version (on alert-mode branch)
pyinstaller --onefile --windowed --name "S-Bux Snagger Alert" --add-data "assets/alert.wav;assets" sbux_snagger.py
```

---

## Branches
- `main` - Full automation version (auto-clicks S-Bux)
- `alert-mode` - Alert-only version (plays sound, no clicking)

## Troubleshooting
- **Not detecting S-Bux**: Run `debug_detection.py` to see what's being detected
- **Clicking wrong things**: Tighten color range or size limits in Config
- **Click not registering**: Game may need to be visible briefly for click to work
- **No sound playing**: Make sure `assets/alert.wav` exists (Alert Mode)
