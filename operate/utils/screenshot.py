import os
import platform
import subprocess
import pyautogui
from PIL import Image, ImageDraw, ImageGrab
import Xlib.display
import Xlib.X
import Xlib.Xutil  # not sure if Xutil is necessary


def capture_screen_with_cursor(file_path):
    user_platform = platform.system()

    if user_platform == "Windows":
        screenshot = pyautogui.screenshot()
        screenshot.save(file_path)
    elif user_platform == "Linux":
        # Try flameshot first (works on both X11 and Wayland)
        try:
            result = subprocess.run(
                ["flameshot", "full", "-p", file_path],
                capture_output=True,
                timeout=10,
            )
            if result.returncode == 0 and os.path.exists(file_path):
                return
        except Exception:
            pass

        # Fallback: try gnome-screenshot
        try:
            result = subprocess.run(
                ["gnome-screenshot", "-f", file_path],
                capture_output=True,
                timeout=10,
            )
            if result.returncode == 0 and os.path.exists(file_path):
                return
        except Exception:
            pass

        # Fallback: try mss
        try:
            import mss
            with mss.MSS() as sct:
                sct.shot(output=file_path)
            return
        except Exception:
            pass

        # Fallback: original X11 method
        screen = Xlib.display.Display().screen()
        size = screen.width_in_pixels, screen.height_in_pixels
        screenshot = ImageGrab.grab(bbox=(0, 0, size[0], size[1]))
        screenshot.save(file_path)
    elif user_platform == "Darwin":  # (Mac OS)
        # Use the screencapture utility to capture the screen with the cursor
        subprocess.run(["screencapture", "-C", file_path])
    else:
        print(f"The platform you're using ({user_platform}) is not currently supported")


def compress_screenshot(raw_screenshot_filename, screenshot_filename):
    with Image.open(raw_screenshot_filename) as img:
        # Check if the image has an alpha channel (transparency)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            # Create a white background image
            background = Image.new('RGB', img.size, (255, 255, 255))
            # Paste the image onto the background, using the alpha channel as mask
            background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
            # Save the result as JPEG
            background.save(screenshot_filename, 'JPEG', quality=85)  # Adjust quality as needed
        else:
            # If no alpha channel, simply convert and save
            img.convert('RGB').save(screenshot_filename, 'JPEG', quality=85)
