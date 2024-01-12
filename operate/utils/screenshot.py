import os
import platform
import subprocess
import pyautogui
from PIL import Image, ImageDraw, ImageGrab
import Xlib.display
import Xlib.X
import Xlib.Xutil  # not sure if Xutil is necessary
from operate.settings import Config

# Load configuration
config = Config()
monitor_size = config.monitor_size


def add_grid_to_image(original_image_path, new_image_path, grid_interval):
    """
    Add a grid to an image.

    Args:
        original_image_path (str): The file path of the original image.
        new_image_path (str): The file path to save the new image with the grid.
        grid_interval (int): The interval between grid lines in pixels.

    Returns:
        None: The function saves the new image with the grid at the specified path.
    """
    # Load the image
    image = Image.open(original_image_path)

    # Create a drawing object
    draw = ImageDraw.Draw(image)

    # Get the image size
    width, height = image.size

    # Reduce the font size a bit
    font_size = int(grid_interval / 10)  # Reduced font size

    # Calculate the background size based on the font size
    bg_width = int(font_size * 4.2)  # Adjust as necessary
    bg_height = int(font_size * 1.2)  # Adjust as necessary

    # Function to draw text with a white rectangle background
    def draw_label_with_background(
        position, text, draw, font_size, bg_width, bg_height
    ):
        # Adjust the position based on the background size
        text_position = (position[0] + bg_width // 2, position[1] + bg_height // 2)
        # Draw the text background
        draw.rectangle(
            [position[0], position[1], position[0] + bg_width, position[1] + bg_height],
            fill="white",
        )
        # Draw the text
        draw.text(text_position, text, fill="black", font_size=font_size, anchor="mm")

    # Draw vertical lines and labels at every `grid_interval` pixels
    for x in range(grid_interval, width, grid_interval):
        line = ((x, 0), (x, height))
        draw.line(line, fill="blue")
        for y in range(grid_interval, height, grid_interval):
            # Calculate the percentage of the width and height
            x_percent = round((x / width) * 100)
            y_percent = round((y / height) * 100)
            draw_label_with_background(
                (x - bg_width // 2, y - bg_height // 2),
                f"{x_percent}%,{y_percent}%",
                draw,
                font_size,
                bg_width,
                bg_height,
            )

    # Draw horizontal lines - labels are already added with vertical lines
    for y in range(grid_interval, height, grid_interval):
        line = ((0, y), (width, y))
        draw.line(line, fill="blue")

    # Save the image with the grid
    image.save(new_image_path)


def capture_screen_with_cursor(file_path):
    """
    Capture the screen with the cursor and save it to the specified file path.

    Args:
        file_path (str): The file path where the screenshot will be saved.

    Raises:
        None

    Returns:
        None
    """
    user_platform = platform.system()

    if user_platform == "Windows":
        screenshot = pyautogui.screenshot()
        screenshot.save(file_path)
    elif user_platform == "Linux":
        # Use xlib to prevent scrot dependency for Linux
        screen = Xlib.display.Display().screen()
        size = screen.width_in_pixels, screen.height_in_pixels
        monitor_size["width"] = size[0]
        monitor_size["height"] = size[1]
        screenshot = ImageGrab.grab(bbox=(0, 0, size[0], size[1]))
        screenshot.save(file_path)
    elif user_platform == "Darwin":  # (Mac OS)
        # Use the screencapture utility to capture the screen with the cursor
        subprocess.run(["screencapture", "-C", file_path])
    else:
        print(f"The platform you're using ({user_platform}) is not currently supported")
