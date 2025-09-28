import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
from PIL import ImageGrab
import time
import os

# Path to S-Bux template image
TEMPLATE_PATH = os.path.join('assets', 'sbux.png')

# Game window title (may need adjustment)
GAME_WINDOW_TITLE = 'Pixel Starships'

# Template matching threshold
MATCH_THRESHOLD = 0.8


def find_game_window():
    windows = gw.getWindowsWithTitle(GAME_WINDOW_TITLE)
    if windows:
        return windows[0]
    return None


def screenshot_window(window):
    left, top, width, height = window.left, window.top, window.width, window.height
    img = ImageGrab.grab(bbox=(left, top, left + width, top + height))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def find_sbux_locations(screenshot, template_path):
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= MATCH_THRESHOLD)
    w, h = template.shape[1], template.shape[0]
    points = list(zip(*loc[::-1]))
    return [(x + w//2, y + h//2) for x, y in points]


def click_locations(window, locations):
    for x, y in locations:
        abs_x = window.left + x
        abs_y = window.top + y
        pyautogui.click(abs_x, abs_y)
        time.sleep(0.1)


def main():
    print('S-Bux Snagger started. Looking for game window...')
    while True:
        window = find_game_window()
        if not window:
            print('Game window not found. Retrying...')
            time.sleep(2)
            continue
        screenshot = screenshot_window(window)
        locations = find_sbux_locations(screenshot, TEMPLATE_PATH)
        if locations:
            print(f'Found {len(locations)} S-Bux! Clicking...')
            click_locations(window, locations)
        time.sleep(1)

if __name__ == '__main__':
    main()
