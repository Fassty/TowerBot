import logging
import time

import win32api
import win32con
import win32gui

logger = logging.getLogger(__name__)

def focus_window(window_title, retry=2):
    """
    Bring the specified window to the foreground.
    Args:
        window_title (str): Title of the window to focus.
    Returns:
        hwnd (int): Handle to the window or None if not found.
    """
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd == 0:
        logger.error("Window '{}' not found.".format(window_title))
        return None
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Restore the window if minimized
        win32gui.SetForegroundWindow(hwnd)  # Bring the window to the foreground
    except Exception as e:
        if retry > 0:
            logger.info('Failed to focus window. Retrying...')
            time.sleep(2)
            focus_window(window_title, retry=retry - 1)
        else:
            raise e
    return hwnd

def send_click_to_window(hwnd, x, y):
    """
    Send a mouse click to the specified window at given coordinates.
    Args:
        hwnd (int): Handle to the window.
        x (int): X-coordinate relative to the window.
        y (int): Y-coordinate relative to the window.
    """
    # Convert client-area coordinates to screen coordinates
    rect = win32gui.GetWindowRect(hwnd)
    screen_x = rect[0] + x
    screen_y = rect[1] + y

    # Send the mouse events
    win32api.SetCursorPos((screen_x, screen_y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, screen_x, screen_y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, screen_x, screen_y, 0, 0)
    logger.info("Clicked at ({}, {}) in window '{}'.".format(screen_x, screen_y, hwnd))

def send_scroll_to_window(hwnd, x, y, scroll_amount):
    """
    Send a scroll signal to the specified window at given coordinates.
    Args:
        hwnd (int): Handle to the window.
        x (int): X-coordinate relative to the window.
        y (int): Y-coordinate relative to the window.
        scroll_amount (int): Amount to scroll (positive for up, negative for down).
    """
    # Convert client-area coordinates to screen coordinates
    rect = win32gui.GetWindowRect(hwnd)
    if x < 1 and y < 1:
        w, h = rect[2] - rect[0], rect[3] - rect[1]
        x, y = int(w * x), int(h * y)
    screen_x = rect[0] + x
    screen_y = rect[1] + y

    # Move the cursor to the target position
    win32api.SetCursorPos((screen_x, screen_y))

    # Send the scroll signal
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, scroll_amount, 0)
    logger.info("Scrolled at ({}, {}) in window '{}' by {}.".format(screen_x, screen_y, hwnd, scroll_amount))