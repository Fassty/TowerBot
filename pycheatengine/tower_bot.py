from pycheatengine.utils.logging_config import setup_logging

setup_logging()

import random
import sys
import time

import cv2
import numpy as np
import pyautogui
import win32api
import win32con
import win32gui
from PIL import ImageGrab
import pygetwindow as gw
import pytesseract
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract\tesseract.exe'

def screenshot_window(window_title):
    """
    Takes a screenshot of the specified window on Windows.
    Args:
        window_title (str): Title of the window to capture.
    Returns:
        PIL.Image.Image: Screenshot of the specified window, or None if not found.
    """
    # Find the window by title
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
    except IndexError:
        print(f"Window with title '{window_title}' not found.")
        return None

    # Get window bounds
    left, top, right, bottom = window.left, window.top, window.right, window.bottom

    # Take a screenshot of the window region
    screenshot = ImageGrab.grab(bbox=(left, top, right, bottom), all_screens=True)
    return screenshot

def detect_image_on_screen(template_path, window_title):
    """
    Detect an image on the screen and return its bounding box coordinates.
    Args:
        template_path (str): Path to the image to detect.
    Returns:
        tuple: Bounding box coordinates (x_min, y_min, x_max, y_max) or None if not found.
    """
    # Step 1: Take a screenshot of the current screen
    screenshot = screenshot_window(window_title)
    screenshot.save('screenshot.png')
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Step 2: Load the template image
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        raise FileNotFoundError(f"Template image not found at {template_path}")

    # Convert screenshot to grayscale for feature matching
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    # Step 3: Detect keypoints and descriptors using ORB
    orb = cv2.ORB_create(5000)
    keypoints1, descriptors1 = orb.detectAndCompute(template, None)
    keypoints2, descriptors2 = orb.detectAndCompute(gray_screenshot, None)

    # Step 4: Match features using BFMatcher
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    matches = sorted(matches, key=lambda x: x.distance)

    # Step 5: Find homography if sufficient matches are found
    if len(matches) > 10:  # You can adjust the threshold
        src_pts = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

        matrix, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if matrix is not None:
            # Step 6: Get the bounding box of the template
            h, w = template.shape
            points = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
            transformed_points = cv2.perspectiveTransform(points, matrix)

            # Convert to integer points for OpenCV drawing
            transformed_points = np.int32(transformed_points)

            # Draw bounding box as a closed polygon
            cv2.polylines(screenshot, [transformed_points], isClosed=True, color=(0, 255, 0), thickness=3)

            # Get bounding box coordinates
            x_min = int(min(transformed_points[:, 0, 0]))
            y_min = int(min(transformed_points[:, 0, 1]))
            x_max = int(max(transformed_points[:, 0, 0]))
            y_max = int(max(transformed_points[:, 0, 1]))

            # Draw bounding box on the screenshot
            #cv2.polylines(screenshot, [np.int32(transformed_points)], True, (0, 255, 0), 3)
            return screenshot, (x_min, y_min, x_max, y_max)

    return None, None

def detect_text_on_screen(window_title):
    """
    Detects all text on the screen and retrieves their coordinates.
    Returns:
        list of dict: A list of dictionaries containing text and bounding box coordinates.
    """
    # Take a screenshot of the entire screen
    screenshot = screenshot_window(window_title)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

    # Perform OCR on the screenshot
    ocr_data = pytesseract.image_to_data(screenshot, output_type=Output.DICT, config='--oem 1 --psm 1')

    detected_text = []
    for i in range(len(ocr_data['text'])):
        text = ocr_data['text'][i].strip()
        if text:  # Ignore empty strings
            x, y, w, h = (ocr_data['left'][i], ocr_data['top'][i],
                          ocr_data['width'][i], ocr_data['height'][i])
            detected_text.append({
                'text': text,
                'x_min': x,
                'y_min': y,
                'x_max': x + w,
                'y_max': y + h
            })

    return detected_text, screenshot

def draw_text_boxes(screenshot, detected_text):
    """
    Draws bounding boxes around detected text on the screenshot.
    Args:
        screenshot (np.array): The screenshot image.
        detected_text (list of dict): Detected text with bounding boxes.
    """
    for text_info in detected_text:
        x_min, y_min, x_max, y_max = (text_info['x_min'], text_info['y_min'],
                                      text_info['x_max'], text_info['y_max'])
        cv2.rectangle(screenshot, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        cv2.putText(screenshot, text_info['text'], (x_min, y_min - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

def detect_small_image(template_paths, window_title):
    """
    Detect a small image on the screen using template matching.
    Args:
        template_path (str): Path to the small image template.
    Returns:
        tuple: Bounding box coordinates (x_min, y_min, x_max, y_max) or None if not found.
    """
    # Step 1: Take a screenshot of the current screen
    screenshot = screenshot_window(window_title)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Convert screenshot to grayscale
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    bounding_boxes = {}
    for template_path in template_paths:
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            raise FileNotFoundError(f"Template image not found at {template_path}")

        result = cv2.matchTemplate(gray_screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # Threshold for detection
        threshold = 0.8  # Adjust based on requirements
        if max_val >= threshold:
            h, w = template.shape
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            bounding_boxes[template_path] = (top_left[0], top_left[1], bottom_right[0], bottom_right[1])

    return screenshot, bounding_boxes

def focus_window(window_title):
    """
    Bring the specified window to the foreground.
    Args:
        window_title (str): Title of the window to focus.
    Returns:
        hwnd (int): Handle to the window or None if not found.
    """
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd == 0:
        print(f"Window '{window_title}' not found.")
        return None
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Restore the window if minimized
    win32gui.SetForegroundWindow(hwnd)  # Bring the window to the foreground
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
    print(f"Clicked at ({screen_x}, {screen_y}) in window '{hwnd}'.")

def click_inside_circle(center_x, center_y, radius, window_title):
    """
    Clicks a random point inside the specified circle.
    Args:
        center_x (int): X-coordinate of the circle center.
        center_y (int): Y-coordinate of the circle center.
        radius (int): Radius of the circle.
        window_title (str): Title of the window for coordinate alignment.
    """
    # Generate a random point inside the circle
    while True:
        rand_x = random.randint(-radius, radius)
        rand_y = random.randint(-radius, radius)
        if rand_x**2 + rand_y**2 <= radius**2:  # Check if point is inside the circle
            break

    # Convert to absolute screen coordinates
    absolute_x = center_x + rand_x
    absolute_y = center_y + rand_y

    # Adjust for window position
    window = gw.getWindowsWithTitle(window_title)[0]
    absolute_x += window.left
    absolute_y += window.top


    try:
        hwnd = focus_window(window_title)
    except:
        time.sleep(2)
        hwnd = focus_window(window_title)
    if hwnd is None:
        print("Unable to focus the window. Click not performed.")
        return
    # Simulate a mouse click at the calculated position
    send_click_to_window(hwnd, center_x + rand_x, center_y + rand_y)

if __name__ == "__main__":
    detected_text, screenshot = detect_text_on_screen('MSI App Player')

    if detected_text:
        print(f"Detected {len(detected_text)} text blocks:")
        for text_info in detected_text:
            print(f"Text: '{text_info['text']}', Coordinates: ({text_info['x_min']}, {text_info['y_min']}, {text_info['x_max']}, {text_info['y_max']})")

        # Draw text boxes on the screenshot
        draw_text_boxes(screenshot, detected_text)

        # Display the annotated screenshot
        cv2.imshow("Detected Text", screenshot)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No text detected on the screen.")

if __name__ == "__main__":
    # Example usage
    template_paths = [
        #r"C:\Users\mikul\Pictures\Screenshots\demon_mode.png",
        r"C:\Users\mikul\Pictures\Screenshots\floating_gem.png",
        r"C:\Users\mikul\Pictures\Screenshots\ad_gems.png",
        #r"C:\Users\mikul\Pictures\Screenshots\def_active.png"
        ]

    while True:
        screenshot, bounding_boxes = detect_small_image(template_paths, 'MSI App Player')

        if bounding_boxes:
            print(f"Found {len(bounding_boxes)} matches:")
            for template, bounding_box in bounding_boxes.items():
                print(f"Template '{template}' found at: {bounding_box}")
                x1, y1, x2, y2 = bounding_box
                # cv2.rectangle(screenshot, (x1, y1),
                #               (x2, y2), (0, 255, 0), 2)
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                dist_x = x2 - x1
                dist_y = y2 - y1
                radius = int(min(dist_x, dist_y) * 0.6 / 2)
                if template == r"C:\Users\mikul\Pictures\Screenshots\floating_gem.png":
                    try:
                        click_inside_circle(center_x, center_y, radius, 'MSI App Player')
                    except:
                        time.sleep(10)
                else:
                    time.sleep(5 + random.randint(0, 20))
                    try:
                        click_inside_circle(center_x, center_y, radius, 'MSI App Player')
                    except:
                        pass
                #cv2.circle(screenshot, (center_x, center_y), radius, (0, 0, 255), 2)
            # Display the screenshot
            # cv2.imshow("Detected Images", screenshot)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
        else:
            print("Small image not found on the screen.")

        time.sleep(1)

# if __name__ == "__main__":
#     # Example usage
#     template_path = r"C:\Users\mikul\Pictures\Screenshots\ad_gems.png"
#     screenshot, bounding_box = detect_image_on_screen(template_path, 'MSI App Player')
#     if bounding_box:
#         print(f"Image found at: {bounding_box}")
#         # Display the screenshot with bounding box
#         cv2.imshow("Detected Image", screenshot)
#         cv2.waitKey(0)
#         cv2.destroyAllWindows()
#     else:
#         print("Image not found on the screen.")
