import pyautogui
import time
import math
import platform
from operate.utils import convert_percent_to_decimal

def mouse_click(click_detail):
    try:
        x = convert_percent_to_decimal(click_detail["x"])
        y = convert_percent_to_decimal(click_detail["y"])

        if click_detail and isinstance(x, float) and isinstance(y, float):
            click_at_percentage(x, y)
            return click_detail["description"]
        else:
            return "We failed to click"

    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return "We failed to click"
    
def click_at_percentage(
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

def keyboard_type(text):
    text = text.replace("\\n", "\n")
    for char in text:
        pyautogui.write(char)
    pyautogui.press("enter")
    return "Type: " + text


def search(text):
    if platform.system() == "Windows": 
        pyautogui.press('win')
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