import csv
from typing import Dict, Any, Optional
import logging
import random
import time

import numpy as np
import pyautogui

from pycheatengine.utils.image_detection import screenshot_window, detect_image_in_scene
from pycheatengine.bots.utils import random_point_inside_circle, bbox_get_inscribed_circle
from pycheatengine.utils.text_recognition import detect_text_in_scene
from pycheatengine.utils.window_controls import focus_window, send_click_to_window

logger = logging.getLogger(__name__)

class FarmingBot:
    def __init__(self, window_title: str, template_images: Dict[str, str], options: Optional[Dict[str, Any]] = None):
        self.window_title = window_title
        self.template_images = template_images
        self.options = options

        self.ad_gem_timer = None
        self.floating_gem_timer = None

        self.output_file = r'C:\Users\mikul\PycharmProjects\PythonProject\logs\gem_log.csv'
        with open(self.output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["timestamp", "gem_type", "delay"])

    def check_ad_gems(self, scene):
        _, bbox = detect_image_in_scene(scene, self.template_images['ad_gems'])
        if bbox:
            logger.info('Detected an ad gem: {}'.format(bbox))

            if self.ad_gem_timer:
                time_now = time.time()
                took = int(time_now - self.ad_gem_timer)
                with open(self.output_file, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([int(time_now), 'ad_gems', took])

            center_x, center_y, radius = bbox_get_inscribed_circle(*bbox)
            x, y = random_point_inside_circle(center_x, center_y, radius)

            time.sleep(5 + random.randint(0, 10))

            handle = focus_window(self.window_title)
            send_click_to_window(handle, x, y)

            self.ad_gem_timer = time.time()

    def check_floating_gem(self, scene):
        _, bbox = detect_image_in_scene(scene, self.template_images['floating_gem'])
        if bbox:
            logger.info('Detected a floating gem: {}'.format(bbox))

            if self.floating_gem_timer:
                time_now = time.time()
                took = int(time_now - self.floating_gem_timer)
                with open(self.output_file, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([int(time_now), 'floating_gem', took])

            center_x, center_y, radius = bbox_get_inscribed_circle(*bbox)
            x, y = random_point_inside_circle(center_x, center_y, radius)
            handle = focus_window(self.window_title)
            send_click_to_window(handle, x, y)

            self.floating_gem_timer = time.time()

    def get_cash(self, scene):
        x_min, y_min, x_max, y_max = 0, 0, scene.shape[1], scene.shape[0]
        cash_location = (int(0.01 * x_max), int(0.04 * y_max), int(0.24 * x_max), int(0.08 * y_max))
        cash_text = scene[cash_location[1]:cash_location[3], cash_location[0]:cash_location[2]]
        detected_text = detect_text_in_scene(cash_text)
        cash = -1
        for text_info in detected_text:
            text = text_info['text'].strip()
            if text.startswith('$') and len(text) > 1:
                cash_text = text[1:]
                if cash_text.endswith('K'):
                    try:
                        cash = float(cash_text[:-1]) * 1_000
                    except ValueError:
                        logger.info('Could not convert cash to float: {}'.format(text))
                elif cash_text.endswith('M'):
                    try:
                        cash = float(cash_text[:-1]) * 1_000_000
                    except ValueError:
                        logger.info('Could not convert cash to float: {}'.format(text))
                elif cash_text.endswith('B'):
                    try:
                        cash = float(cash_text[:-1]) * 1_000_000_000
                    except ValueError:
                        logger.info('Could not convert cash to float: {}'.format(text))
                else:
                    try:
                        cash = float(cash_text)
                    except ValueError:
                        logger.info('Could not convert cash to float: {}'.format(text))

        return cash

    def get_upgrade_cost(self, scene, stat):
        x_min, y_min, x_max, y_max = 0, 0, scene.shape[1], scene.shape[0]
        health_location = (int(0.26 * x_max), int(0.68 * y_max), int(0.45 * x_max), int(0.75 * y_max))
        health_button = scene[health_location[1]:health_location[3], health_location[0]:health_location[2]]
        detected_text = detect_text_in_scene(health_button)
        upgrade_cost = np.inf
        for text_info in detected_text:
            text = text_info['text'].strip()
            if text.startswith('$') and len(text) > 1:
                upgrade_cost_text = text[1:]
                if upgrade_cost_text.endswith('K'):
                    try:
                        upgrade_cost = float(upgrade_cost_text[:-1]) * 1_000
                    except ValueError:
                        logger.info('Could not convert cash to float: {}'.format(text))
                elif upgrade_cost_text.endswith('M'):
                    try:
                        upgrade_cost = float(upgrade_cost_text[:-1]) * 1_000_000
                    except ValueError:
                        logger.info('Could not convert cash to float: {}'.format(text))
                elif upgrade_cost_text.endswith('B'):
                    try:
                        upgrade_cost = float(upgrade_cost_text[:-1]) * 1_000_000_000
                    except ValueError:
                        logger.info('Could not convert cash to float: {}'.format(text))
                else:
                    try:
                        upgrade_cost = float(upgrade_cost_text)
                    except ValueError:
                        logger.info('Could not convert cash to float: {}'.format(text_info['text']))

        return upgrade_cost

    def upgrade_stat(self, scene, slot: int):
        x_min, y_min, x_max, y_max = 0, 0, scene.shape[1], scene.shape[0]
        health_location = (int(0.26 * x_max), int(0.68 * y_max), int(0.45 * x_max), int(0.75 * y_max))
        center_x, center_y, radius = bbox_get_inscribed_circle(*health_location)
        x, y = random_point_inside_circle(center_x, center_y, radius)
        handle = focus_window(self.window_title)
        send_click_to_window(handle, x, y)

    def switch_card(self, card):
        pass

    def scroll_menu(self, direction: str = 'up'):
        if direction == 'up':
            ...
        elif direction == 'down':
            ...
        else:
            raise ValueError('Invalid direction {}'.format(direction))

    def start(self):
        while True:
            scene = screenshot_window(self.window_title)

            self.check_floating_gem(scene)

            try:
                cash = self.get_cash(scene)
            except Exception:
                cash = -1.0

            self.switch_card('defense')
            try:
                health_upgrade_cost = self.get_upgrade_cost(scene, 'health')
            except Exception:
                health_upgrade_cost = np.inf

            if cash > health_upgrade_cost:
                self.upgrade_stat(scene, 0)

            self.check_ad_gems(scene)

            time.sleep(1)

            # Move the mouse to keep the system awake
            pyautogui.moveRel(1, 0)  # Move mouse 1 pixel to the right
            pyautogui.moveRel(-1, 0)  # Move mouse 1 pixel to the left
