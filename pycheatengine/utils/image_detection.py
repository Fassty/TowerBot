import numpy as np
import cv2
import PIL.ImageGrab
import pygetwindow as gw

def screenshot_window(window_title: str):
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
    screenshot = PIL.ImageGrab.grab(bbox=(left, top, right, bottom), all_screens=True)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot

def _detect_image(scene_bw, template_path, threshold = 0.8):
    """
    Detect
    :param scene_bw: The scene on which the image is to be detected, black and white image
    :param template_path: The path to the template image
    :param threshold: The threshold to detect the image
    :return: bounding box of the detected image or None if no bounding box is found
    """
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        raise FileNotFoundError(f"Template image not found at {template_path}")

    result = cv2.matchTemplate(scene_bw, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Threshold for detection
    if max_val >= threshold:
        h, w = template.shape
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        bounding_box = (top_left[0], top_left[1], bottom_right[0], bottom_right[1])
        return bounding_box
    return None

def detect_image_in_scene(scene, template_path, threshold = 0.8, draw_bbox = False):
    """
    Detect a small image on the screen using template matching.
    Args:
        scene: The scene on which the image is to be detected (window screenshot)
        template_path: Dictionary of template image names and their paths
        threshold: The threshold to detect the image
        draw_bbox: If True, draw bounding boxes around the detected image
    Returns:
        tuple: Bounding box coordinates (x_min, y_min, x_max, y_max) or None if not found.
    """
    # Convert scene to grayscale
    scene_bw = cv2.cvtColor(scene, cv2.COLOR_BGR2GRAY)

    bbox = _detect_image(scene_bw, template_path, threshold)
    if draw_bbox:
        cv2.rectangle(scene, bbox, (0, 255, 0), 2)

    return scene, bbox

def detect_images_in_scene(scene, templates, threshold = 0.8, draw_bboxes = False):
    """
    Detect a small image on the screen using template matching.
    Args:
        scene: The scene on which the image is to be detected (window screenshot)
        templates: Dictionary of template image names and their paths
        threshold: The threshold to detect the image
        draw_bboxes: If True, draw bounding boxes around the detected image
    Returns:
        tuple: Bounding box coordinates (x_min, y_min, x_max, y_max) or None if not found.
    """
    # Convert scene to grayscale
    scene_bw = cv2.cvtColor(scene, cv2.COLOR_BGR2GRAY)

    bounding_boxes = {}
    for template_name, template_path in templates.items():
        bbox = _detect_image(scene_bw, template_path, threshold)
        if draw_bboxes:
            cv2.rectangle(scene, bbox, (0, 255, 0), 2)
        bounding_boxes[template_name] = bbox

    return scene, bounding_boxes