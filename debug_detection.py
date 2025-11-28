"""
Debug tool to test S-Bux detection using color-based detection.
The S-Bux has a very distinctive bright green color (HSV ~74, 151, 254).
"""

import cv2
import numpy as np
import pygetwindow as gw
from PIL import ImageGrab
import os

# Configuration
GAME_WINDOW_TITLE = "Pixel Starships"
MONITOR_RIGHT_PORTION = 0.75

# Exclusion zones (to avoid chat/UI false positives)
EXCLUDE_LEFT_PORTION = 0.25   # Exclude left 25% (chat area)
EXCLUDE_BOTTOM_PORTION = 0.15  # Exclude bottom 15% (UI)

# S-Bux specific bright green color (tightened to avoid chat text)
SBUX_HUE_LOW = 72
SBUX_HUE_HIGH = 78
SBUX_SAT_LOW = 140   # Must be highly saturated
SBUX_VAL_LOW = 220   # Must be very bright

# Size constraints for S-Bux at various zoom levels
MIN_CONTOUR_AREA = 80     # Minimum pixels for a valid detection
MAX_CONTOUR_AREA = 3000   # Maximum to avoid large text blocks


def find_game_window():
    all_windows = gw.getAllWindows()
    for window in all_windows:
        if GAME_WINDOW_TITLE.lower() in window.title.lower():
            return window
    return None


def capture_screen(window):
    left = window.left
    top = window.top
    width = window.width
    height = window.height
    
    portion_width = int(width * MONITOR_RIGHT_PORTION)
    portion_left = left + width - portion_width
    
    img = ImageGrab.grab(bbox=(portion_left, top, portion_left + portion_width, top + height), all_screens=True)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def detect_sbux_by_color(screenshot):
    """
    Detect S-Bux by finding the distinctive bright green color.
    Returns list of (x, y, w, h, pixel_count) for each detection.
    """
    height, width = screenshot.shape[:2]
    
    # Calculate exclusion zones
    exclude_left = int(width * EXCLUDE_LEFT_PORTION)
    exclude_bottom = int(height * EXCLUDE_BOTTOM_PORTION)
    
    hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
    
    # Create mask for S-Bux specific bright green
    lower = np.array([SBUX_HUE_LOW, SBUX_SAT_LOW, SBUX_VAL_LOW])
    upper = np.array([SBUX_HUE_HIGH, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    
    # Black out exclusion zones (left for chat, bottom for UI)
    if exclude_left > 0:
        mask[:, :exclude_left] = 0
    if exclude_bottom > 0:
        mask[height - exclude_bottom:, :] = 0
    
    # Find contours of green regions
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detections = []
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Filter by size
        if area < MIN_CONTOUR_AREA or area > MAX_CONTOUR_AREA:
            continue
        
        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        # S-Bux should be roughly square-ish (aspect ratio check)
        aspect = w / h if h > 0 else 0
        if aspect < 0.5 or aspect > 2.0:  # Tighter aspect for S-Bux vs text
            continue
        
        detections.append((x, y, w, h, area))
    
    return detections, mask


def main():
    print("=" * 50)
    print("S-Bux Detection Debug Tool (COLOR-BASED)")
    print("=" * 50)
    
    print(f"Looking for bright green: HSV ({SBUX_HUE_LOW}-{SBUX_HUE_HIGH}, {SBUX_SAT_LOW}+, {SBUX_VAL_LOW}+)")
    print(f"Contour area range: {MIN_CONTOUR_AREA} - {MAX_CONTOUR_AREA} pixels")
    
    # Find game window
    window = find_game_window()
    if not window:
        print(f"ERROR: Could not find '{GAME_WINDOW_TITLE}' window")
        return
    
    print(f"Found game window: {window.title}")
    print(f"Monitoring right {int(MONITOR_RIGHT_PORTION*100)}% of screen")
    
    print("\n" + "=" * 50)
    print("Controls:")
    print("  s   : Save screenshot")
    print("  m   : Show/hide color mask")
    print("  q   : Quit")
    print("=" * 50 + "\n")
    
    save_counter = 0
    show_mask = False
    
    while True:
        screenshot = capture_screen(window)
        if screenshot is None:
            continue
        
        # Detect S-Bux by color
        detections, mask = detect_sbux_by_color(screenshot)
        
        # Draw detections
        display = screenshot.copy()
        for det in detections:
            x, y, w, h, area = det
            cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(display, f"area:{area}", 
                       (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw info
        cv2.putText(display, f"Detections: {len(detections)} | Press 'm' to toggle mask view",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Resize for display
        scale_factor = min(1.0, 900 / display.shape[1])
        display_resized = cv2.resize(display, None, fx=scale_factor, fy=scale_factor)
        
        cv2.imshow("S-Bux Debug (Color Detection)", display_resized)
        
        if show_mask:
            mask_resized = cv2.resize(mask, None, fx=scale_factor, fy=scale_factor)
            cv2.imshow("Color Mask (white = detected green)", mask_resized)
        
        key = cv2.waitKey(100) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f"debug_capture_{save_counter}.png"
            cv2.imwrite(filename, screenshot)
            cv2.imwrite(f"debug_mask_{save_counter}.png", mask)
            print(f"Saved: {filename} and debug_mask_{save_counter}.png")
            save_counter += 1
        elif key == ord('m'):
            show_mask = not show_mask
            if not show_mask:
                cv2.destroyWindow("Color Mask (white = detected green)")
    
    cv2.destroyAllWindows()
    print("\nDone!")


if __name__ == "__main__":
    main()
