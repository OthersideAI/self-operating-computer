import math
import os
import platform
import pyautogui
import subprocess
import time
import Xlib
from PIL import Image, ImageGrab
from app.lib import checks
from app.lib.constants import monitor_size, ACCURATE_PIXEL_COUNT
from app.lib.util import ImageUtil


class ScreenshotAction:
    """Defines actions related to taking screenshots"""

    @staticmethod
    def capture_mini_screenshot_with_cursor(file_path=os.path.join("screenshots", "screenshot_mini.png"), x=0, y=0):
        if checks.PLATFORM_LINUX:
            x = float(x[:-1])  # convert x from "50%" to 50.
            y = float(y[:-1])

            x = (x / 100) * monitor_size["width"]  # convert x from 50 to 0.5 * monitor_width
            y = (y / 100) * monitor_size["height"]

            # Define the coordinates for the rectangle
            x1, y1 = int(x - ACCURATE_PIXEL_COUNT / 2), int(y - ACCURATE_PIXEL_COUNT / 2)
            x2, y2 = int(x + ACCURATE_PIXEL_COUNT / 2), int(y + ACCURATE_PIXEL_COUNT / 2)

            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            screenshot = screenshot.resize(
                (screenshot.width * 2, screenshot.height * 2), Image.LANCZOS
            )  # upscale the image so it's easier to see and percentage marks more visible
            screenshot.save(file_path)

            screenshots_dir = "screenshots"
            grid_screenshot_filename = os.path.join(screenshots_dir, "screenshot_mini_with_grid.png")

            ImageUtil.add_grid_to_image(
                file_path, grid_screenshot_filename, int(ACCURATE_PIXEL_COUNT / 2)
            )
        elif checks.PLATFORM_MACOS:
            x = float(x[:-1])  # convert x from "50%" to 50.
            y = float(y[:-1])

            x = (x / 100) * monitor_size["width"]  # convert x from 50 to 0.5 * monitor_width
            y = (y / 100) * monitor_size["height"]

            x1, y1 = int(x - ACCURATE_PIXEL_COUNT / 2), int(y - ACCURATE_PIXEL_COUNT / 2)

            width = ACCURATE_PIXEL_COUNT
            height = ACCURATE_PIXEL_COUNT
            # Use the screencapture utility to capture the screen with the cursor
            rect = f"-R{x1},{y1},{width},{height}"
            subprocess.run(["screencapture", "-C", rect, file_path])

            screenshots_dir = "screenshots"
            grid_screenshot_filename = os.path.join(screenshots_dir, "screenshot_mini_with_grid.png")

            ImageUtil.add_grid_to_image(file_path, grid_screenshot_filename, int(ACCURATE_PIXEL_COUNT / 2))

    @staticmethod
    def capture_screen_with_cursor(file_path):
        if checks.PLATFORM_WINDOWS:
            screenshot = pyautogui.screenshot()
            screenshot.save(file_path)
        elif checks.PLATFORM_LINUX:
            # Use xlib to prevent scrot dependency for Linux
            screen = Xlib.display.Display().screen()
            size = screen.width_in_pixels, screen.height_in_pixels
            monitor_size["width"] = size[0]
            monitor_size["height"] = size[1]
            screenshot = ImageGrab.grab(bbox=(0, 0, size[0], size[1]))
            screenshot.save(file_path)
        elif checks.PLATFORM_MACOS:
            # Use the screencapture utility to capture the screen with the cursor
            subprocess.run(["screencapture", "-C", file_path])
        else:
            print(f"The platform you're using ({platform.system()}) is not currently supported")


class KeyboardAction:
    """Defines actions related to keyboard input"""

    @staticmethod
    def type(text):
        text = text.replace("\\n", "\n")
        for char in text:
            pyautogui.write(char)
        pyautogui.press("enter")
        return "Type: " + text


class MouseAction:
    """Defines actions related to mouse input"""

    @staticmethod
    def click(click_detail):
        try:
            x = MouseAction._convert_percent_to_decimal(click_detail["x"])
            y = MouseAction._convert_percent_to_decimal(click_detail["y"])

            if click_detail and isinstance(x, float) and isinstance(y, float):
                MouseAction._click_at_percentage(x, y)
                return click_detail["description"]
            else:
                return "We failed to click"

        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return "We failed to click"

    @staticmethod
    def _click_at_percentage(
            x_percentage, y_percentage, duration=0.2, circle_radius=50, circle_duration=0.5
    ):
        # Get the size of the primary monitor
        screen_width, screen_height = pyautogui.size()

        # Calculate the x and y coordinates in pixels
        x_pixel = int(screen_width * float(x_percentage))
        y_pixel = int(screen_height * float(y_percentage))

        # Move to the position smoothly
        pyautogui.moveTo(x_pixel, y_pixel, duration=duration)

        # Circular movement
        start_time = time.time()
        while time.time() - start_time < circle_duration:
            angle = ((time.time() - start_time) / circle_duration) * 2 * math.pi
            x = x_pixel + math.cos(angle) * circle_radius
            y = y_pixel + math.sin(angle) * circle_radius
            pyautogui.moveTo(x, y, duration=0.1)

        # Finally, click
        pyautogui.click(x_pixel, y_pixel)
        return "Successfully clicked"

    @staticmethod
    def _convert_percent_to_decimal(percent_str):
        try:
            # Remove the '%' sign and convert to float
            decimal_value = float(percent_str.strip("%"))

            # Convert to decimal (e.g., 20% -> 0.20)
            return decimal_value / 100
        except ValueError as e:
            print(f"Error converting percent to decimal: {e}")
            return None


class SearchAction:
    """Defines actions related to searching for programs"""

    @staticmethod
    def search(text):
        if checks.PLATFORM_WINDOWS or checks.PLATFORM_LINUX:
            pyautogui.press("win")
        else:
            # Press and release Command and Space separately
            pyautogui.keyDown("command")
            pyautogui.press("space")
            pyautogui.keyUp("command")

        # Now type the text
        for char in text:
            pyautogui.write(char)

        pyautogui.press("enter")
        return "Open program: " + text
