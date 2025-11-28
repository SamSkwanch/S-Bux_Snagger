"""
S-Bux Snagger v3.0
A tool to automatically detect and collect S-Bux in Pixel Starships.

Features:
- Simple GUI with start/stop controls
- Real-time detection feedback
- Color-based detection for accurate S-Bux finding
- Works at any zoom level
- Multi-monitor support
"""

import cv2
import numpy as np
import pygetwindow as gw
from PIL import ImageGrab
import threading
import time
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import win32gui
import win32con
import win32api
import win32ui
import win32com.client
from ctypes import windll


# =============================================================================
# CONFIGURATION - Adjust these values to tune detection
# =============================================================================

class Config:
    """Configuration settings for the S-Bux Snagger."""
    
    # Game window title (partial match)
    GAME_WINDOW_TITLE = "Pixel Starships"
    
    # Portion of screen to monitor (from right edge)
    # 0.33 = right 1/3, 0.5 = right half, 1.0 = full screen
    MONITOR_RIGHT_PORTION = 0.75
    
    # Exclude bottom portion of monitored area (for chat/UI)
    # 0.0 = don't exclude, 0.2 = exclude bottom 20%
    EXCLUDE_BOTTOM_PORTION = 0.15
    
    # Exclude left portion of monitored area (optional)
    # 0.0 = don't exclude, 0.3 = exclude left 30% of monitored area
    EXCLUDE_LEFT_PORTION = 0.0  # Disabled since chat bubbles can appear anywhere
    
    # How often to scan for S-Bux (seconds)
    SCAN_INTERVAL = 0.15
    
    # Delay between clicks (seconds)
    CLICK_DELAY = 0.1
    
    # S-Bux specific bright green color in HSV
    # The S-Bux border is HSV (74, 151, 254) - very distinctive
    # Very tight range to avoid chat text false positives
    SBUX_HUE_LOW = 73
    SBUX_HUE_HIGH = 76
    SBUX_SAT_LOW = 145   # Must be highly saturated
    SBUX_VAL_LOW = 245   # Must be very bright (chat may be slightly dimmer)
    
    # Size constraints for S-Bux contours (pixels)
    # S-Bux icon is small and consistent; chat bubbles are larger/variable
    MIN_CONTOUR_AREA = 100    # Minimum area
    MAX_CONTOUR_AREA = 800    # S-Bux shouldn't be huge; chat bubbles often are
    
    # S-Bux dimension constraints (pixels)
    # At various zoom levels, S-Bux is roughly 15-60 pixels wide/tall
    MIN_DIMENSION = 8
    MAX_DIMENSION = 70


# =============================================================================
# DETECTION ENGINE
# =============================================================================

class DetectionEngine:
    """Handles S-Bux detection using color-based approach."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def is_ready(self) -> bool:
        """Check if the engine is ready to detect."""
        return True  # Color detection doesn't need a template
    
    def get_info(self) -> str:
        """Get detection info string."""
        return f"Color detection: HSV ({self.config.SBUX_HUE_LOW}-{self.config.SBUX_HUE_HIGH})"
    
    def detect(self, screenshot: np.ndarray) -> list:
        """
        Detect S-Bux in the screenshot using color-based detection.
        Finds the distinctive bright green color of the S-Bux.
        Returns list of (x, y, width, height) tuples for each detection.
        """
        if screenshot is None:
            return []
        
        height, width = screenshot.shape[:2]
        
        # Calculate exclusion zones
        exclude_left = int(width * self.config.EXCLUDE_LEFT_PORTION)
        exclude_bottom = int(height * self.config.EXCLUDE_BOTTOM_PORTION)
        
        # Convert to HSV
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        # Create mask for S-Bux specific bright green
        lower = np.array([self.config.SBUX_HUE_LOW, self.config.SBUX_SAT_LOW, self.config.SBUX_VAL_LOW])
        upper = np.array([self.config.SBUX_HUE_HIGH, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        
        # Black out exclusion zones (left side for chat, bottom for UI)
        if exclude_left > 0:
            mask[:, :exclude_left] = 0
        if exclude_bottom > 0:
            mask[height - exclude_bottom:, :] = 0
        
        # Find contours of green regions
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by contour area
            if area < self.config.MIN_CONTOUR_AREA or area > self.config.MAX_CONTOUR_AREA:
                continue
            
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by dimensions (S-Bux has consistent size range)
            if w < self.config.MIN_DIMENSION or w > self.config.MAX_DIMENSION:
                continue
            if h < self.config.MIN_DIMENSION or h > self.config.MAX_DIMENSION:
                continue
            
            # S-Bux should be roughly square-ish (aspect ratio check)
            # Text tends to be wide rectangles, S-Bux is more square
            aspect = w / h if h > 0 else 0
            if aspect < 0.6 or aspect > 1.7:  # Very tight aspect ratio
                continue
            
            # Compactness check: S-Bux fills its bounding box well
            # Text characters are sparse, S-Bux icon is dense
            bounding_area = w * h
            fill_ratio = area / bounding_area if bounding_area > 0 else 0
            if fill_ratio < 0.3:  # S-Bux should fill at least 30% of its bounding box
                continue
            
            detections.append((x, y, w, h))
        
        return detections


# =============================================================================
# GAME INTEGRATION
# =============================================================================

class GameInterface:
    """Handles interaction with the Pixel Starships game window."""
    
    def __init__(self, config: Config):
        self.config = config
        self.window = None
        self.hwnd = None  # Windows handle for background clicking
        self.last_window_info = None
    
    def find_window(self) -> bool:
        """Find the game window."""
        try:
            all_windows = gw.getAllWindows()
            for window in all_windows:
                if self.config.GAME_WINDOW_TITLE.lower() in window.title.lower():
                    self.window = window
                    self.last_window_info = f'"{window.title}" ({window.width}x{window.height})'
                    # Get the Windows handle for background clicking
                    self.hwnd = win32gui.FindWindow(None, window.title)
                    return True
        except Exception:
            pass
        
        self.window = None
        self.hwnd = None
        return False
    
    def get_window_info(self) -> str:
        """Get window information string."""
        return self.last_window_info or "Not found"
    
    def capture_window(self) -> tuple:
        """
        Capture the game window content even when it's behind other windows.
        Uses Windows API to capture the actual window, not just screen pixels.
        Returns (screenshot, offset_x, offset_y) or (None, 0, 0) on failure.
        """
        if self.hwnd is None or self.window is None:
            return None, 0, 0
        
        try:
            # Get window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
            width = right - left
            height = bottom - top
            
            if width <= 0 or height <= 0:
                return None, 0, 0
            
            # Get the window's device context
            hwndDC = win32gui.GetWindowDC(self.hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # Create a bitmap to store the capture
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # Use PrintWindow to capture even when window is behind others
            # Flag 2 = PW_RENDERFULLCONTENT (captures even for layered windows)
            result = windll.user32.PrintWindow(self.hwnd, saveDC.GetSafeHdc(), 2)
            
            if result == 0:
                # Fallback: try without the flag
                result = windll.user32.PrintWindow(self.hwnd, saveDC.GetSafeHdc(), 0)
            
            # Convert to numpy array
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype='uint8')
            img.shape = (height, width, 4)  # BGRA format
            
            # Clean up Windows resources
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, hwndDC)
            
            # Convert BGRA to BGR
            screenshot = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # Calculate monitored portion (right side)
            portion_width = int(width * self.config.MONITOR_RIGHT_PORTION)
            portion_start = width - portion_width
            
            # Crop to right portion
            cropped = screenshot[:, portion_start:, :]
            
            # Return with offsets for click positioning
            return cropped, left + portion_start, top
            
        except Exception as e:
            return None, 0, 0
    
    def click_at(self, screen_x: int, screen_y: int):
        """
        Click at the specified screen coordinates.
        Quickly switches to game, clicks, and switches back.
        Total interruption is ~100ms, mouse position is preserved.
        """
        if self.hwnd is None or self.window is None:
            return
        
        try:
            # Save current mouse position
            original_pos = win32api.GetCursorPos()
            
            # Get the currently active window to restore later
            foreground_hwnd = win32gui.GetForegroundWindow()
            
            # Use multiple methods to ensure window activation
            # First, show/restore the window if minimized
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            
            # Try SetForegroundWindow with the Alt key workaround
            try:
                # Send Alt key to allow focus change (Windows security workaround)
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys('%')
                time.sleep(0.02)
            except:
                pass
            
            # Bring window to top
            win32gui.BringWindowToTop(self.hwnd)
            win32gui.SetForegroundWindow(self.hwnd)
            
            # Wait for window to be active
            time.sleep(0.05)
            
            # Move mouse to target position
            win32api.SetCursorPos((screen_x, screen_y))
            time.sleep(0.03)
            
            # Perform click
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.03)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(0.03)
            
            # Restore mouse position
            win32api.SetCursorPos(original_pos)
            
            # Restore previous window
            if foreground_hwnd and foreground_hwnd != self.hwnd:
                time.sleep(0.02)
                try:
                    win32gui.SetForegroundWindow(foreground_hwnd)
                except:
                    pass
            
        except Exception as e:
            # Restore mouse position even on error
            try:
                win32api.SetCursorPos(original_pos)
            except:
                pass


# =============================================================================
# MAIN APPLICATION GUI
# =============================================================================

class SBuxSnaggerApp:
    """Main application with GUI."""
    
    def __init__(self):
        self.config = Config()
        self.detection_engine = DetectionEngine(self.config)
        self.game_interface = GameInterface(self.config)
        
        self.running = False
        self.scan_thread = None
        self.total_collected = 0
        self.session_collected = 0
        self.scan_count = 0
        
        self._setup_gui()
    
    def _setup_gui(self):
        """Set up the main GUI window."""
        self.root = tk.Tk()
        self.root.title("S-Bux Snagger v3.0")
        self.root.geometry("420x650")
        self.root.minsize(420, 650)
        self.root.resizable(True, True)
        
        # Style
        style = ttk.Style()
        style.configure("Start.TButton", font=("Segoe UI", 12, "bold"), padding=8, foreground="green")
        style.configure("Stop.TButton", font=("Segoe UI", 12, "bold"), padding=8, foreground="red")
        style.configure("Status.TLabel", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Count.TLabel", font=("Segoe UI", 24, "bold"))
        
        # Main container
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="💰 S-Bux Snagger", font=("Segoe UI", 18, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Control buttons - PUT AT TOP so they're always visible
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.start_button = tk.Button(button_frame, text="▶ START", font=("Segoe UI", 14, "bold"), 
                                       bg="#4CAF50", fg="white", height=2, command=self.start)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        self.stop_button = tk.Button(button_frame, text="⏹ STOP", font=("Segoe UI", 14, "bold"),
                                      bg="#f44336", fg="white", height=2, command=self.stop, state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))
        
        # Stats frame
        stats_frame = ttk.LabelFrame(main_frame, text="Session Stats", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.collected_label = ttk.Label(stats_frame, text="0", style="Count.TLabel")
        self.collected_label.pack()
        ttk.Label(stats_frame, text="S-Bux Collected", style="Status.TLabel").pack()
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Status indicator
        self.status_var = tk.StringVar(value="⏹ Stopped")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, style="Header.TLabel")
        self.status_label.pack(pady=(0, 5))
        
        # Info labels
        info_frame = ttk.Frame(status_frame)
        info_frame.pack(fill=tk.X)
        
        ttk.Label(info_frame, text="Game Window:", style="Status.TLabel").grid(row=0, column=0, sticky="w")
        self.window_var = tk.StringVar(value="Not found")
        ttk.Label(info_frame, textvariable=self.window_var, style="Status.TLabel").grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(info_frame, text="Detection:", style="Status.TLabel").grid(row=1, column=0, sticky="w")
        self.detection_mode_var = tk.StringVar(value=self.detection_engine.get_info())
        ttk.Label(info_frame, textvariable=self.detection_mode_var, style="Status.TLabel").grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(info_frame, text="Last Detection:", style="Status.TLabel").grid(row=2, column=0, sticky="w")
        self.detection_var = tk.StringVar(value="None")
        ttk.Label(info_frame, textvariable=self.detection_var, style="Status.TLabel").grid(row=2, column=1, sticky="w", padx=(10, 0))
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, height=10, width=40, font=("Consolas", 9), state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Initial log
        self._log("S-Bux Snagger v3.0 ready")
        self._log(f"Detection: {self.detection_engine.get_info()}")
    
    def _log(self, message: str):
        """Add a message to the activity log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
    
    def start(self):
        """Start the S-Bux detection."""
        self.running = True
        self.session_collected = 0
        self.scan_count = 0
        self.collected_label.configure(text="0")
        
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.status_var.set("🔍 Scanning...")
        
        self._log("Started scanning for S-Bux...")
        self._log(f"Monitoring right {int(self.config.MONITOR_RIGHT_PORTION * 100)}% of screen")
        
        self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
        self.scan_thread.start()
    
    def stop(self):
        """Stop the S-Bux detection."""
        self.running = False
        
        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.status_var.set("⏹ Stopped")
        
        self._log(f"Stopped. Collected {self.session_collected} S-Bux this session")
    
    def _scan_loop(self):
        """Main scanning loop (runs in separate thread)."""
        window_found = False
        
        while self.running:
            # Find game window
            if not self.game_interface.find_window():
                if window_found:
                    self.root.after(0, lambda: self._log("Lost game window"))
                    self.root.after(0, lambda: self.window_var.set("Not found"))
                    self.root.after(0, lambda: self.status_var.set("⚠ Window not found"))
                    window_found = False
                time.sleep(1)
                continue
            
            if not window_found:
                info = self.game_interface.get_window_info()
                self.root.after(0, lambda i=info: self._log(f"Found: {i}"))
                self.root.after(0, lambda i=info: self.window_var.set(i))
                window_found = True
            
            # Capture window content (works even when window is behind others)
            screenshot, offset_x, offset_y = self.game_interface.capture_window()
            if screenshot is None:
                self.root.after(0, lambda: self._log("⚠ Screenshot failed"))
                time.sleep(self.config.SCAN_INTERVAL)
                continue
            
            # Update scan counter
            self.scan_count += 1
            if self.scan_count % 10 == 0:  # Update status every 10 scans
                self.root.after(0, lambda c=self.scan_count: self.status_var.set(f"🔍 Scanning... ({c} scans)"))
            
            detections = self.detection_engine.detect(screenshot)
            
            if detections:
                count = len(detections)
                self.root.after(0, lambda c=count: self._on_detection(c))
                self.root.after(0, lambda: self._log(f"🎯 Detected! Clicking..."))
                
                # Click on each detection
                for x, y, w, h in detections:
                    if not self.running:
                        break
                    
                    # Calculate screen coordinates (center of detection)
                    screen_x = offset_x + x + w // 2
                    screen_y = offset_y + y + h // 2
                    
                    self.root.after(0, lambda sx=screen_x, sy=screen_y: self._log(f"   Click @ ({sx}, {sy})"))
                    self.game_interface.click_at(screen_x, screen_y)
                    time.sleep(self.config.CLICK_DELAY)
            
            time.sleep(self.config.SCAN_INTERVAL)
    
    def _on_detection(self, count: int):
        """Called when S-Bux are detected (runs on main thread)."""
        self.session_collected += count
        self.total_collected += count
        
        self.collected_label.configure(text=str(self.session_collected))
        self.detection_var.set(f"{count} found @ {datetime.now().strftime('%H:%M:%S')}")
        self._log(f"💰 Collected {count} S-Bux!")
    
    def _on_close(self):
        """Handle window close."""
        self.running = False
        time.sleep(0.3)  # Let thread finish
        self.root.destroy()
    
    def run(self):
        """Start the application."""
        self.root.mainloop()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app = SBuxSnaggerApp()
    app.run()
