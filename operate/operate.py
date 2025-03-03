import sys
import os
import time
import asyncio
import pyautogui
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit import prompt
import platform

# from operate.models.prompts import USER_QUESTION, get_system_prompt

def main(model, terminal_prompt, voice_mode=False, verbose_mode=False):
    """
    Main function for the Self-Operating Computer.

    Parameters:
    - model: The model used for generating responses.
    - terminal_prompt: A string representing the prompt provided in the terminal.
    - voice_mode: A boolean indicating whether to enable voice mode.

    Returns:
    None
    """
    from operate.config import Config
    from operate.exceptions import ModelNotRecognizedException
    
    from operate.utils.style import (
        ANSI_GREEN,
        ANSI_RESET,
        ANSI_YELLOW,
        ANSI_RED,
        ANSI_BRIGHT_MAGENTA,
        ANSI_BLUE,
        style,
    )

    from operate.utils.operating_system import OperatingSystem
    from operate.models.prompts import (
        USER_QUESTION,
        get_system_prompt,
    )

    # Load configuration
    config = Config()
    operating_system = OperatingSystem()
    
    from operate.models.apis import get_next_action

    while True:  # Add outer loop to enable restarting after completion
        mic = None
        # Initialize `WhisperMic`, if `voice_mode` is True

        config.verbose = verbose_mode
        config.validation(model, voice_mode)

        if voice_mode:
            try:
                from whisper_mic import WhisperMic

                # Initialize WhisperMic if import is successful
                mic = WhisperMic()
            except ImportError:
                print(
                    "Voice mode requires the 'whisper_mic' module. Please install it using 'pip install -r requirements-audio.txt'"
                )
                sys.exit(1)

        # Skip message dialog if prompt was given directly
        if not terminal_prompt:
            message_dialog(
                title="Self-Operating Computer",
                text="An experimental framework to enable multimodal models to operate computers",
                style=style,
            ).run()

        else:
            print("Running direct prompt...")

        # # Clear the console
        if platform.system() == "Windows":
            os.system("cls")
        else:
            print("\033c", end="")

        if terminal_prompt and not hasattr(main, 'first_run_complete'):
            # Only use the terminal prompt on the first iteration
            objective = terminal_prompt
            main.first_run_complete = True
        elif voice_mode:
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RESET} Listening for your command... (speak now)"
            )
            try:
                objective = mic.listen()
            except Exception as e:
                print(f"{ANSI_RED}Error in capturing voice input: {e}{ANSI_RESET}")
                return  # Exit if voice input fails
        else:
            print(
                f"[{ANSI_GREEN}Self-Operating Computer {ANSI_RESET}|{ANSI_BRIGHT_MAGENTA} {model}{ANSI_RESET}]\n{USER_QUESTION}"
            )
            print(f"{ANSI_YELLOW}[User]{ANSI_RESET}")
            objective = prompt(style=style)

        system_prompt = get_system_prompt(model, objective)
        system_message = {"role": "system", "content": system_prompt}
        messages = [system_message]

        loop_count = 0

        session_id = None

        task_completed = False  # Flag to indicate if the task was completed
        while not task_completed:
            if config.verbose:
                print("[Self Operating Computer] loop_count", loop_count)
            try:
                operations, session_id = asyncio.run(
                    get_next_action(model, messages, objective, session_id)
                )

                # Instead of breaking out of the whole program, we set a flag if "done" is reached
                task_completed = operate(operations, session_id, model)

                loop_count += 1
                if loop_count > 10:
                    task_completed = True  # Force completion if loop count exceeds 10
                    print(
                        f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_YELLOW} Max loop count reached. Moving to next task.{ANSI_RESET}")
            except ModelNotRecognizedException as e:
                print(
                    f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] -> {e} {ANSI_RESET}"
                )
                task_completed = True  # Exit inner loop and start over
            except Exception as e:
                print(
                    f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] -> {e} {ANSI_RESET}"
                )
                task_completed = True  # Exit inner loop and start over

        print(f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RESET} Task completed. Ready for a new task.")
        if terminal_prompt:
            # If the session was started with a terminal prompt, we need to clear it after the first use
            terminal_prompt = None


# def verify_click_target(x_percent, y_percent, target_description, client):
#     import pyautogui
#     import base64
#     import io
#     from PIL import Image, ImageDraw
#
#     screen_width, screen_height = pyautogui.size()
#     x = int(float(x_percent) * screen_width)
#     y = int(float(y_percent) * screen_height)
#
#     region_size = 100
#     region_left = max(0, x - region_size)
#     region_top = max(0, y - region_size)
#     region_width = min(region_size * 2, screen_width - region_left)
#     region_height = min(region_size * 2, screen_height - region_top)
#
#     region_screenshot = pyautogui.screenshot(region=(region_left, region_top, region_width, region_height))
#
#     draw = ImageDraw.Draw(region_screenshot)
#     center_x = x - region_left
#     center_y = y - region_top
#     line_length = 20
#     draw.line((center_x - line_length, center_y, center_x + line_length, center_y), fill='red', width=2)
#     draw.line((center_x, center_y - line_length, center_x, center_y + line_length), fill='red', width=2)
#
#     buffer = io.BytesIO()
#     region_screenshot.save(buffer, format="JPEG")
#     img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
#
#     try:
#         verification_prompt = f"""
#         I'm about to click at the position marked with the red crosshair.
#         I'm trying to click on: "{target_description}"
#
#         Does the crosshair appear to be positioned correctly on or very near the target?
#         Respond ONLY with "YES" if it's correct or "NO" if it's wrong.
#         """
#
#         response = client.messages.create(
#             model="claude-3-7-sonnet-20250219",
#             messages=[{
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": verification_prompt},
#                     {
#                         "type": "image",
#                         "source": {
#                             "type": "base64",
#                             "media_type": "image/jpeg",
#                             "data": img_base64
#                         }
#                     }
#                 ]
#             }],
#             max_tokens=50,
#         )
#
#         verification_result = response.content[0].text.strip().upper()
#
#         print(f"[Click Verification] Target: {target_description}")
#         print(f"[Click Verification] Claude's response: {verification_result}")
#
#         region_screenshot.save("debug_last_click_verification.jpg")
#
#         return "YES" in verification_result
#
#     except Exception as e:
#         print(f"[Click Verification] Error during verification: {e}")
#         return False


import cv2
import numpy as np
import pyautogui
import os
import io
from PIL import Image, ImageDraw


def find_icon_on_screen(target_description):
    """
    Uses computer vision to find an icon or UI element that matches the target description.

    Args:
        target_description (str): Description of what we're trying to find (e.g., "sbc-images-main folder")

    Returns:
        tuple: (x_percent, y_percent) coordinates as percentages of screen width/height, or None if not found
    """
    # Take a screenshot of the entire screen
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    # Save the screenshot for debugging
    cv2.imwrite("debug_full_screen.jpg", screenshot_rgb)

    # Initialize results
    results = []

    # 1. Text detection for folder/file names (optional, requires pytesseract)
    try:
        import pytesseract
        gray = cv2.cvtColor(screenshot_rgb, cv2.COLOR_BGR2GRAY)

        # Extract text from the screenshot
        text_data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

        # Look for the target text in detected text
        target_words = target_description.lower().split()

        for i, text in enumerate(text_data['text']):
            if text and any(word in text.lower() for word in target_words):
                # Get coordinates for this text
                x = text_data['left'][i] + text_data['width'][i] // 2
                y = text_data['top'][i] + text_data['height'][i] // 2

                # Add to results with high confidence
                results.append((x, y, 0.9))  # 0.9 is confidence score

                # Draw a rectangle around the text for debugging
                x1, y1 = text_data['left'][i], text_data['top'][i]
                x2 = x1 + text_data['width'][i]
                y2 = y1 + text_data['height'][i]
                cv2.rectangle(screenshot_rgb, (x1, y1), (x2, y2), (0, 255, 0), 2)
    except (ImportError, Exception) as e:
        print(f"Text detection not available: {e}")

    # 2. Template matching for common desktop icons
    icon_folder = "icon_templates"
    if os.path.exists(icon_folder):
        for filename in os.listdir(icon_folder):
            if filename.endswith(('.png', '.jpg')):
                template_path = os.path.join(icon_folder, filename)
                template = cv2.imread(template_path)

                if template is None:
                    continue

                # Apply template matching
                template_h, template_w = template.shape[:2]
                res = cv2.matchTemplate(screenshot_rgb, template, cv2.TM_CCOEFF_NORMED)

                # Get locations where the match exceeds threshold
                threshold = 0.7
                loc = np.where(res >= threshold)

                for pt in zip(*loc[::-1]):
                    # Get center point of the match
                    x = pt[0] + template_w // 2
                    y = pt[1] + template_h // 2
                    confidence = res[pt[1], pt[0]]

                    # Add to results
                    results.append((x, y, confidence))

                    # Draw for debugging
                    cv2.rectangle(screenshot_rgb, pt, (pt[0] + template_w, pt[1] + template_h), (0, 0, 255), 2)

    # 3. Folder icon detection using color and shape (backup method)
    if not results:
        # Convert to HSV for better color segmentation
        hsv = cv2.cvtColor(screenshot_rgb, cv2.COLOR_BGR2HSV)

        # Define color ranges for common folder icons (yellow folders in Windows)
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([40, 255, 255])

        # Create mask for yellow color
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by size (folder icons are usually of similar size)
        min_area = 100
        max_area = 5000

        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                # Get center of contour
                M = cv2.moments(contour)
                if M["m00"] > 0:
                    x = int(M["m10"] / M["m00"])
                    y = int(M["m01"] / M["m00"])

                    # Add to results with lower confidence
                    results.append((x, y, 0.5))

                    # Draw for debugging
                    cv2.drawContours(screenshot_rgb, [contour], -1, (255, 0, 0), 2)

    # Save the annotated screenshot for debugging
    cv2.imwrite("debug_target_detection.jpg", screenshot_rgb)

    if results:
        # Sort by confidence
        results.sort(key=lambda x: x[2], reverse=True)
        best_match = results[0]

        # Convert to percentage of screen size
        screen_width, screen_height = screenshot.size
        x_percent = best_match[0] / screen_width
        y_percent = best_match[1] / screen_height

        return (x_percent, y_percent)

    return None


# def enhanced_click(target_description, model=None):
#     """
#     Enhanced clicking function that uses computer vision to find and click on targets.
#
#     Args:
#         target_description (str): Description of what to click on
#         model (str, optional): Model name for verification
#
#     Returns:
#         bool: True if click was successful, False otherwise
#     """
#     # Try to find the target using computer vision
#     coords = find_icon_on_screen(target_description)
#
#     if coords:
#         x_percent, y_percent = coords
#         print(f"[Visual Target Finder] Found target '{target_description}' at ({x_percent:.3f}, {y_percent:.3f})")
#
#         # Convert percentages to actual screen coordinates
#         screen_width, screen_height = pyautogui.size()
#         x_coord = int(x_percent * screen_width)
#         y_coord = int(y_percent * screen_height)
#
#         # Click on the found location
#         pyautogui.click(x_coord, y_coord)
#         return True
#     else:
#         print(f"[Visual Target Finder] Could not find target '{target_description}' on screen")
#         return False


import pyautogui
import platform
import ctypes
import subprocess


def get_scaling_factor():
    """
    Detect the current DPI scaling factor based on the operating system.
    Returns:
        scaling_factor (float): A multiplier to adjust coordinates.
    """
    os_name = platform.system()
    scaling_factor = 1.0

    if os_name == "Windows":
        try:
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            dc = user32.GetDC(0)
            logical_width = user32.GetDeviceCaps(dc, 8)  # HORZRES (logical width)
            physical_width = user32.GetDeviceCaps(dc, 118)  # DESKTOPHORZRES (physical width)
            scaling_factor = physical_width / logical_width
            user32.ReleaseDC(0, dc)
        except Exception as e:
            print("Windows scaling detection error:", e)
            scaling_factor = 1.0
    elif os_name == "Darwin":  # macOS
        try:
            output = subprocess.check_output(["system_profiler", "SPDisplaysDataType"])
            output = output.decode("utf-8")
            if "Retina" in output:
                scaling_factor = 2.0
            else:
                scaling_factor = 1.0
        except Exception as e:
            print("macOS scaling detection error:", e)
            scaling_factor = 1.0
    elif os_name == "Linux":
        try:
            output = subprocess.check_output(
                ["gsettings", "get", "org.gnome.desktop.interface", "scaling-factor"]
            )
            scaling_factor = float(output.decode("utf-8").strip())
        except Exception as e:
            print("Linux scaling detection error:", e)
            scaling_factor = 1.0

    return scaling_factor


def click_relative(x_percent, y_percent, x_divisor=1.50, y_multiplier=1.25):
    """
    Converts relative coordinates to absolute screen coordinates, applies DPI scaling,
    then divides the x-coordinate by x_divisor and multiplies the y-coordinate by y_multiplier before clicking.

    Args:
        x_percent (float): Relative x-coordinate (e.g., 0.10 for 10% across).
        y_percent (float): Relative y-coordinate (e.g., 0.20 for 20% down).
        x_divisor (float): Value to divide the computed x-coordinate by (default 1.50).
        y_multiplier (float): Value to multiply the computed y-coordinate by (default 1.25).
    """
    screen_width, screen_height = pyautogui.size()
    scaling_factor = get_scaling_factor()

    # Compute the base absolute coordinates.
    base_x = x_percent * screen_width * scaling_factor
    base_y = y_percent * screen_height * scaling_factor

    # Adjust: divide x-coordinate and multiply y-coordinate.
    adjusted_x = int(base_x / x_divisor)
    adjusted_y = int(base_y * y_multiplier)

    print(
        f"Clicking at ({adjusted_x}, {adjusted_y}) on a {screen_width}x{screen_height} screen with scaling factor {scaling_factor}")
    pyautogui.click(adjusted_x, adjusted_y)


def operate(operations, session_id, model=None):
    """
    Processes a list of operations and executes them.
    Supports click, doubleclick, rightclick, scroll, write, press, wait, and done operations.
    For click/doubleclick/rightclick operations, it uses the adjusted coordinate conversion:
    - x-coordinate divided by 1.50.
    - y-coordinate multiplied by 1.25.

    Returns:
        bool: True if "done" operation was encountered (task completed), otherwise False
    """
    import time

    for op in operations:
        if op.get("operation") in ["click", "doubleclick", "rightclick"]:
            try:
                x_percent = float(op.get("x", 0))
                y_percent = float(op.get("y", 0))
                screen_width, screen_height = pyautogui.size()
                scaling_factor = get_scaling_factor()

                # Compute the base absolute coordinates.
                base_x = x_percent * screen_width * scaling_factor
                base_y = y_percent * screen_height * scaling_factor

                # Adjust: divide x-coordinate and multiply y-coordinate.
                adjusted_x = int(base_x / 1.50)
                adjusted_y = int(base_y * 1.25)

                operation_type = op.get("operation")
                operation_name = {
                    "click": "Clicking",
                    "doubleclick": "Double-clicking",
                    "rightclick": "Right-clicking"
                }.get(operation_type, operation_type)

                print(
                    f"{operation_name} at ({adjusted_x}, {adjusted_y}) on a {screen_width}x{screen_height} screen "
                    f"with scaling factor {scaling_factor}"
                )

                if operation_type == "doubleclick":
                    pyautogui.doubleClick(adjusted_x, adjusted_y)
                elif operation_type == "rightclick":
                    pyautogui.rightClick(adjusted_x, adjusted_y)
                else:
                    pyautogui.click(adjusted_x, adjusted_y)
            except Exception as e:
                print(f"Error performing {op.get('operation')} operation:", e)


        elif op.get("operation") == "scroll":

            try:

                direction = op.get("direction", "")

                amount = int(op.get("amount", 0))

                # For vertical scrolling: positive for up, negative for down

                if direction == "up":

                    clicks = amount * 150

                elif direction == "down":

                    clicks = -amount * 150

                # For horizontal scrolling: negative for left, positive for right

                elif direction == "left":

                    clicks = -amount * 150

                elif direction == "right":

                    clicks = amount * 150

                else:

                    print(f"Invalid scroll direction: {direction}")

                    clicks = 0

                # Execute scroll based on direction type

                if direction in ["up", "down"]:

                    print(f"Scrolling {direction} by {amount} clicks")

                    pyautogui.scroll(clicks)

                elif direction in ["left", "right"]:

                    print(f"Scrolling {direction} by {amount} clicks")

                    pyautogui.hscroll(clicks)

            except Exception as e:

                print("Error performing scroll operation:", e)

        elif op.get("operation") == "write":
            content = op.get("content", "")
            pyautogui.write(content)

        elif op.get("operation") == "press":
            keys = op.get("keys", [])
            for key in keys:
                pyautogui.press(key)

        elif op.get("operation") == "wait":
            duration = float(op.get("duration", 1))
            time.sleep(duration)

        elif op.get("operation") == "done":
            print("Operation completed:", op.get("summary", ""))
            return True  # Signal that the task is completed

    return False  # Continue processing this task
