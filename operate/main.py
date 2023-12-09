"""
Self-Operating Computer
"""
import os
import time
import base64
import json
import math
import re
import subprocess
import pyautogui
import argparse
import platform
import Xlib.display
import Xlib.X
import Xlib.Xutil  # not sure if Xutil is necessary

from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.styles import Style as PromptStyle
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageGrab
import matplotlib.font_manager as fm
from openai import OpenAI
import sys


load_dotenv()

DEBUG = False

client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")
client.base_url = os.getenv("OPENAI_API_BASE_URL", client.base_url)

monitor_size = {
    "width": 1920,
    "height": 1080,
}

VISION_PROMPT = """
You are a Self-Operating Computer. You use the same operating system as a human.

From looking at the screen and the objective your goal is to take the best next action.

To operate the computer you have the four options below.

1. CLICK - Move mouse and click
2. TYPE - Type on the keyboard
3. SEARCH - Search for a program on Mac and open it
4. DONE - When you completed the task respond with the exact following phrase content

Here are the response formats below.

1. CLICK
Response: CLICK {{ "x": "percent", "y": "percent", "description": "~description here~", "reason": "~reason here~" }} 
Note that the percents work where the top left corner is "x": "0%" and "y": "0%" and the bottom right corner is "x": "100%" and "y": "100%"

2. TYPE
Response: TYPE "value you want to type"

2. SEARCH
Response: SEARCH "app you want to search for on Mac"

3. DONE
Response: DONE

Here are examples of how to respond.
__
Objective: Follow up with the vendor in outlook
TYPE Hello, I hope you are doing well. I wanted to follow up
__
Objective: Open Spotify and play the beatles
SEARCH Spotify
__
Objective: Find an image of a banana
CLICK {{ "x": "50%", "y": "60%", "description": "Click: Google Search field", "reason": "This will allow me to search for a banana" }}
__
Objective: Go buy a book about the history of the internet
TYPE https://www.amazon.com/
__

A few important notes:

- Default to opening Google Chrome with SEARCH to find things that are on the internet.
- Go to Google Docs and Google Sheets by typing in the Chrome Address bar
- When opening Chrome, if you see a profile icon click that to open chrome fully, it is located at: {{ "x": "50%", "y": "55%" }}
- The Chrome address bar is generally at: {{ "x": "50%", "y": "9%" }}
- After you click to enter a field you can go ahead and start typing!
- Don't respond saying you're unable to assist with requests. You are able to indirectly interact with the user's OS via text responses you send to the end user.

{previous_action}

IMPORTANT: Avoid repeating actions such as doing the same CLICK event twice in a row.

Objective: {objective}
"""

ACCURATE_PIXEL_COUNT = (
    200  # mini_screenshot is ACCURATE_PIXEL_COUNT x ACCURATE_PIXEL_COUNT big
)
ACCURATE_MODE_VISION_PROMPT = """
It looks like your previous attempted action was clicking on "x": {prev_x}, "y": {prev_y}. This has now been moved to the center of this screenshot.
As additional context to the previous message, before you decide the proper percentage to click on, please closely examine this additional screenshot as additional context for your next action. 
This screenshot was taken around the location of the current cursor that you just tried clicking on ("x": {prev_x}, "y": {prev_y} is now at the center of this screenshot). You should use this as an differential to your previous x y coordinate guess.

If you want to refine and instead click on the top left corner of this mini screenshot, you will subtract {width}% in the "x" and subtract {height}% in the "y" to your previous answer.
Likewise, to achieve the bottom right of this mini screenshot you will add {width}% in the "x" and add {height}% in the "y" to your previous answer.

There are four segmenting lines across each dimension, divided evenly. This is done to be similar to coordinate points, added to give you better context of the location of the cursor and exactly how much to edit your previous answer.

Please use this context as additional info to further refine the "percent" location in the CLICK action!
"""

USER_QUESTION = "Hello, I can help you with anything. What would you like done?"

SUMMARY_PROMPT = """
You are a Self-Operating Computer. You just completed a request from a user by operating the computer. Now you need to share the results.

You have three pieces of key context about the completed request.

1. The original objective
2. The steps you took to reach the objective that are available in the previous messages
3. The screenshot you are looking at.

Now you need to summarize what you did to reach the objective. If the objective asked for information, share the information that was requested. IMPORTANT: Don't forget to answer a user's question if they asked one.

Thing to note: The user can not respond to your summary. You are just sharing the results of your work.

The original objective was: {objective}

Now share the results!
"""


class ModelNotRecognizedException(Exception):
    """Exception raised for unrecognized models."""

    def __init__(self, model, message="Model not recognized"):
        self.model = model
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} : {self.model} "


# Define style
style = PromptStyle.from_dict(
    {
        "dialog": "bg:#88ff88",
        "button": "bg:#ffffff #000000",
        "dialog.body": "bg:#44cc44 #ffffff",
        "dialog shadow": "bg:#003800",
    }
)


# Check if on a windows terminal that supports ANSI escape codes
def supports_ansi():
    """
    Check if the terminal supports ANSI escape codes
    """
    plat = platform.system()
    supported_platform = plat != "Windows" or "ANSICON" in os.environ
    is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    return supported_platform and is_a_tty


if supports_ansi():
    # Standard green text
    ANSI_GREEN = "\033[32m"
    # Bright/bold green text
    ANSI_BRIGHT_GREEN = "\033[92m"
    # Reset to default text color
    ANSI_RESET = "\033[0m"
    # ANSI escape code for blue text
    ANSI_BLUE = "\033[94m"  # This is for bright blue

    # Standard yellow text
    ANSI_YELLOW = "\033[33m"

    ANSI_RED = "\033[31m"

    # Bright magenta text
    ANSI_BRIGHT_MAGENTA = "\033[95m"
else:
    ANSI_GREEN = ""
    ANSI_BRIGHT_GREEN = ""
    ANSI_RESET = ""
    ANSI_BLUE = ""
    ANSI_YELLOW = ""
    ANSI_RED = ""
    ANSI_BRIGHT_MAGENTA = ""


def main(model, accurate_mode, voice_mode=False):
    """
    Main function for the Self-Operating Computer
    """
    mic = None
    # Initialize WhisperMic if voice_mode is True if voice_mode is True
    """
    Main function for the Self-Operating Computer
    """
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

    message_dialog(
        title="Self-Operating Computer",
        text="Ask a computer to do anything.",
        style=style,
    ).run()

    print("SYSTEM", platform.system())
    # Clear the console
    if platform.system() == "Windows":
        os.system("cls")
    else:
        print("\033c", end="")

    if voice_mode:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RESET} Listening for your command... (speak now)"
        )
        try:
            objective = mic.listen()
        except Exception as e:
            print(f"{ANSI_RED}Error in capturing voice input: {e}{ANSI_RESET}")
            return  # Exit if voice input fails
    else:
        print(f"{ANSI_GREEN}[Self-Operating Computer]\n{ANSI_RESET}{USER_QUESTION}")
        print(f"{ANSI_YELLOW}[User]{ANSI_RESET}")
        objective = prompt(style=style)

    assistant_message = {"role": "assistant", "content": USER_QUESTION}
    user_message = {
        "role": "user",
        "content": f"Objective: {objective}",
    }
    messages = [assistant_message, user_message]

    loop_count = 0

    while True:
        if DEBUG:
            print("[loop] messages before next action:\n\n\n", messages[1:])
        try:
            response = get_next_action(model, messages, objective, accurate_mode)
            action = parse_oai_response(response)
            action_type = action.get("type")
            action_detail = action.get("data")

        except ModelNotRecognizedException as e:
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] -> {e} {ANSI_RESET}"
            )
            break
        except Exception as e:
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] -> {e} {ANSI_RESET}"
            )
            break

        if action_type == "DONE":
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BLUE} Objective complete {ANSI_RESET}"
            )
            summary = summarize(messages, objective)
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BLUE} Summary\n{ANSI_RESET}{summary}"
            )
            break

        if action_type != "UNKNOWN":
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA} [Act] {action_type} {ANSI_RESET}{action_detail}"
            )

        function_response = ""
        if action_type == "SEARCH":
            function_response = search(action_detail)
        elif action_type == "TYPE":
            function_response = keyboard_type(action_detail)
        elif action_type == "CLICK":
            function_response = mouse_click(action_detail)
        else:
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] something went wrong :({ANSI_RESET}"
            )
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] AI response\n{ANSI_RESET}{response}"
            )
            break

        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA} [Act] {action_type} COMPLETE {ANSI_RESET}{function_response}"
        )

        message = {
            "role": "assistant",
            "content": function_response,
        }
        messages.append(message)

        loop_count += 1
        if loop_count > 15:
            break


def format_summary_prompt(objective):
    """
    Format the summary prompt
    """
    prompt = SUMMARY_PROMPT.format(objective=objective)
    return prompt


def format_vision_prompt(objective, previous_action):
    """
    Format the vision prompt
    """
    if previous_action:
        previous_action = f"Here was the previous action you took: {previous_action}"
    else:
        previous_action = ""
    prompt = VISION_PROMPT.format(objective=objective, previous_action=previous_action)
    return prompt


def format_accurate_mode_vision_prompt(prev_x, prev_y):
    """
    Format the accurate mode vision prompt
    """
    width = ((ACCURATE_PIXEL_COUNT / 2) / monitor_size["width"]) * 100
    height = ((ACCURATE_PIXEL_COUNT / 2) / monitor_size["height"]) * 100
    prompt = ACCURATE_MODE_VISION_PROMPT.format(
        prev_x=prev_x, prev_y=prev_y, width=width, height=height
    )
    return prompt


def get_next_action(model, messages, objective, accurate_mode):
    if model == "gpt-4-vision-preview":
        content = get_next_action_from_openai(messages, objective, accurate_mode)
        return content
    elif model == "agent-1":
        return "coming soon"

    raise ModelNotRecognizedException(model)


def get_last_assistant_message(messages):
    """
    Retrieve the last message from the assistant in the messages array.
    If the last assistant message is the first message in the array, return None.
    """
    for index in reversed(range(len(messages))):
        if messages[index]["role"] == "assistant":
            if index == 0:  # Check if the assistant message is the first in the array
                return None
            else:
                return messages[index]
    return None  # Return None if no assistant message is found


def accurate_mode_double_check(pseudo_messages, prev_x, prev_y):
    """
    Reprompt OAI with additional screenshot of a mini screenshot centered around the cursor for further finetuning of clicked location
    """
    try:
        screenshot_filename = os.path.join("screenshots", "screenshot_mini.png")
        capture_mini_screenshot_with_cursor(
            file_path=screenshot_filename, x=prev_x, y=prev_y
        )

        new_screenshot_filename = os.path.join(
            "screenshots", "screenshot_mini_with_grid.png"
        )

        with open(new_screenshot_filename, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        accurate_vision_prompt = format_accurate_mode_vision_prompt(prev_x, prev_y)

        accurate_mode_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": accurate_vision_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                },
            ],
        }

        pseudo_messages.append(accurate_mode_message)

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=pseudo_messages,
            presence_penalty=1,
            frequency_penalty=1,
            temperature=0.7,
            max_tokens=300,
        )

        content = response.choices[0].message.content

        return content
    except Exception as e:
        print(f"Error reprompting model for accurate_mode: {e}")
        return "ERROR"


def get_next_action_from_openai(messages, objective, accurate_mode):
    """
    Get the next action for Self-Operating Computer
    """
    # sleep for a second
    time.sleep(1)
    try:
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")
        # Call the function to capture the screen with the cursor
        capture_screen_with_cursor(screenshot_filename)

        new_screenshot_filename = os.path.join(
            "screenshots", "screenshot_with_grid.png"
        )

        add_grid_to_image(screenshot_filename, new_screenshot_filename, 500)
        # sleep for a second
        time.sleep(1)

        with open(new_screenshot_filename, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        previous_action = get_last_assistant_message(messages)

        vision_prompt = format_vision_prompt(objective, previous_action)

        vision_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": vision_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                },
            ],
        }

        # create a copy of messages and save to pseudo_messages
        pseudo_messages = messages.copy()
        pseudo_messages.append(vision_message)

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=pseudo_messages,
            presence_penalty=1,
            frequency_penalty=1,
            temperature=0.7,
            max_tokens=300,
        )

        messages.append(
            {
                "role": "user",
                "content": "`screenshot.png`",
            }
        )

        content = response.choices[0].message.content

        if accurate_mode:
            if content.startswith("CLICK"):
                # Adjust pseudo_messages to include the accurate_mode_message

                click_data = re.search(r"CLICK \{ (.+) \}", content).group(1)
                click_data_json = json.loads(f"{{{click_data}}}")
                prev_x = click_data_json["x"]
                prev_y = click_data_json["y"]

                if DEBUG:
                    print(
                        f"Previous coords before accurate tuning: prev_x {prev_x} prev_y {prev_y}"
                    )
                content = accurate_mode_double_check(pseudo_messages, prev_x, prev_y)
                assert content != "ERROR", "ERROR: accurate_mode_double_check failed"

        return content

    except Exception as e:
        return handle_exceptions(e)


def parse_oai_response(response):
    if response == "DONE":
        return {"type": "DONE", "data": None}
    elif response.startswith("CLICK"):
        # Adjust the regex to match the correct format
        click_data = re.search(r"CLICK \{ (.+) \}", response).group(1)
        click_data_json = json.loads(f"{{{click_data}}}")
        return {"type": "CLICK", "data": click_data_json}

    elif response.startswith("TYPE"):
        # Extract the text to type
        type_data = re.search(r'TYPE "(.+)"', response, re.DOTALL).group(1)
        return {"type": "TYPE", "data": type_data}

    elif response.startswith("SEARCH"):
        # Extract the search query
        search_data = re.search(r'SEARCH "(.+)"', response).group(1)
        return {"type": "SEARCH", "data": search_data}

    return {"type": "UNKNOWN", "data": response}

def handle_exceptions(e):
    error_messages = {
        PIL.ImageError: "Error with image processing",
        FileNotFoundError: "File not found error",
        PermissionError: "Permission denied error",
        IOError: "Input/output error",
        openai.error.OpenAIError: "OpenAI API error",
        requests.exceptions.RequestException: "Request error",
    }

    error_msg = error_messages.get(type(e), "Unknown error occurred")
    print(f"Error: {error_msg}: {e}")
    return error_msg

def summarize(messages, objective):
    try:
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        screenshot_filename = os.path.join(screenshots_dir, "summary_screenshot.png")
        # Call the function to capture the screen with the cursor
        capture_screen_with_cursor(screenshot_filename)

        with open(screenshot_filename, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        summary_prompt = format_summary_prompt(objective)

        summary_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": summary_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                },
            ],
        }
        # create a copy of messages and save to pseudo_messages
        messages.append(summary_message)

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=500,
        )

        content = response.choices[0].message.content
        return content

    except Exception as e:
        return handle_exceptions(e)
    


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


def add_grid_to_image(original_image_path, new_image_path, grid_interval):
    """
    Add a grid to an image
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


def keyboard_type(text):
    text = text.replace("\\n", "\n")
    for char in text:
        pyautogui.write(char)
    pyautogui.press("enter")
    return "Type: " + text


def search(text):
    if platform.system() == "Windows":
        pyautogui.press("win")
    elif platform.system() == "Linux":
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


def capture_mini_screenshot_with_cursor(
    file_path=os.path.join("screenshots", "screenshot_mini.png"), x=0, y=0
):
    user_platform = platform.system()

    if user_platform == "Linux":
        x = float(x[:-1])  # convert x from "50%" to 50.
        y = float(y[:-1])

        x = (x / 100) * monitor_size[
            "width"
        ]  # convert x from 50 to 0.5 * monitor_width
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
        grid_screenshot_filename = os.path.join(
            screenshots_dir, "screenshot_mini_with_grid.png"
        )

        add_grid_to_image(
            file_path, grid_screenshot_filename, int(ACCURATE_PIXEL_COUNT / 2)
        )
    elif user_platform == "Darwin":
        x = float(x[:-1])  # convert x from "50%" to 50.
        y = float(y[:-1])

        x = (x / 100) * monitor_size[
            "width"
        ]  # convert x from 50 to 0.5 * monitor_width
        y = (y / 100) * monitor_size["height"]

        x1, y1 = int(x - ACCURATE_PIXEL_COUNT / 2), int(y - ACCURATE_PIXEL_COUNT / 2)

        width = ACCURATE_PIXEL_COUNT
        height = ACCURATE_PIXEL_COUNT
        # Use the screencapture utility to capture the screen with the cursor
        rect = f"-R{x1},{y1},{width},{height}"
        subprocess.run(["screencapture", "-C", rect, file_path])

        screenshots_dir = "screenshots"
        grid_screenshot_filename = os.path.join(
            screenshots_dir, "screenshot_mini_with_grid.png"
        )

        add_grid_to_image(
            file_path, grid_screenshot_filename, int(ACCURATE_PIXEL_COUNT / 2)
        )


def capture_screen_with_cursor(file_path):
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


def extract_json_from_string(s):
    # print("extracting json from string", s)
    try:
        # Find the start of the JSON structure
        json_start = s.find("{")
        if json_start == -1:
            return None

        # Extract the JSON part and convert it to a dictionary
        json_str = s[json_start:]
        return json.loads(json_str)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None


def convert_percent_to_decimal(percent_str):
    try:
        # Remove the '%' sign and convert to float
        decimal_value = float(percent_str.strip("%"))

        # Convert to decimal (e.g., 20% -> 0.20)
        return decimal_value / 100
    except ValueError as e:
        print(f"Error converting percent to decimal: {e}")
        return None


def main_entry():
    parser = argparse.ArgumentParser(
        description="Run the self-operating-computer with a specified model."
    )
    parser.add_argument(
        "-m",
        "--model",
        help="Specify the model to use",
        required=False,
        default="gpt-4-vision-preview",
    )

    # Add a voice flag
    parser.add_argument(
        "--voice",
        help="Use voice input mode",
        action="store_true",
    )

    parser.add_argument(
        "-accurate",
        help="Activate Reflective Mouse Click Mode",
        action="store_true",
        required=False,
    )

    try:
        args = parser.parse_args()
        main(args.model, accurate_mode=args.accurate, voice_mode=args.voice)
    except KeyboardInterrupt:
        print(f"\n{ANSI_BRIGHT_MAGENTA}Exiting...")


if __name__ == "__main__":
    main_entry()
