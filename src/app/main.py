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
import platform
import Xlib.display
import Xlib.X
import Xlib.Xutil  # not sure if Xutil is necessary

from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.styles import Style as PromptStyle
from PIL import Image, ImageDraw, ImageGrab
from openai import OpenAI
import sys
from app.config import settings
from app.lib import prompts
from app.lib.exceptions import ModelNotRecognizedException
from app.lib import checks, terminal


client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_api_url)

monitor_size = {
    "width": 3840,
    "height": 2160,
}

ACCURATE_PIXEL_COUNT = (
    200  # mini_screenshot is ACCURATE_PIXEL_COUNT x ACCURATE_PIXEL_COUNT big
)

# Define style
style = PromptStyle.from_dict(
    {
        "dialog": "bg:#88ff88",
        "button": "bg:#ffffff #000000",
        "dialog.body": "bg:#44cc44 #ffffff",
        "dialog shadow": "bg:#003800",
    }
)


def main():
    """
    Main function for the Self-Operating Computer
    """
    mic = None

    # Initialize WhisperMic if voice mode enabled
    if settings.voice_mode:
        try:
            from whisper_mic import WhisperMic

            # Initialize WhisperMic if import is successful
            mic = WhisperMic()
        except ImportError:
            print(
                "Voice mode requires the 'whisper_mic' module. Please install it using 'pip install -r requirements-audio.txt'"
            )
            sys.exit(1)

    # Display an intro prompt
    message_dialog(
        title="Self-Operating Computer",
        text="Ask a computer to do anything.",
        style=style,
    ).run()

    print(f'Platform: {platform.system()}')

    # Clear the console
    terminal.clear_console()

    if settings.voice_mode:
        print(
            f"{terminal.ANSI_GREEN}[Self-Operating Computer]{terminal.ANSI_RESET} Listening for your command... (speak now)"
        )
        try:
            objective = mic.listen()
        except Exception as e:
            print(f"{terminal.ANSI_RED}Error in capturing voice input: {e}{terminal.ANSI_RESET}")
            return  # Exit if voice input fails
    else:
        print(f"{terminal.ANSI_GREEN}[Self-Operating Computer]\n{terminal.ANSI_RESET}{prompts.USER_QUESTION}")
        print(f"{terminal.ANSI_YELLOW}[User]{terminal.ANSI_RESET}")
        objective = prompt(style=style)

    assistant_message = {"role": "assistant", "content": prompts.USER_QUESTION}
    user_message = {
        "role": "user",
        "content": f"Objective: {objective}",
    }
    messages = [assistant_message, user_message]

    loop_count = 0

    while True:
        if settings.debug:
            print("[loop] messages before next action:\n\n\n", messages[1:])

        try:
            response = get_next_action(settings.openai_model, messages, objective, settings.accurate_mode)
            action = parse_oai_response(response)
            action_type = action.get("type")
            action_detail = action.get("data")

        except ModelNotRecognizedException as e:
            print(
                f"{terminal.ANSI_GREEN}[Self-Operating Computer]{terminal.ANSI_RED}[Error] -> {e} {terminal.ANSI_RESET}"
            )
            break
        except Exception as e:
            print(
                f"{terminal.ANSI_GREEN}[Self-Operating Computer]{terminal.ANSI_RED}[Error] -> {e} {terminal.ANSI_RESET}"
            )
            break

        if action_type == "DONE":
            print(
                f"{terminal.ANSI_GREEN}[Self-Operating Computer]{terminal.ANSI_BLUE} Objective complete {terminal.ANSI_RESET}"
            )
            summary = summarize(messages, objective)
            print(
                f"{terminal.ANSI_GREEN}[Self-Operating Computer]{terminal.ANSI_BLUE} Summary\n{terminal.ANSI_RESET}{summary}"
            )
            break

        if action_type != "UNKNOWN":
            print(
                f"{terminal.ANSI_GREEN}[Self-Operating Computer]{terminal.ANSI_BRIGHT_MAGENTA} [Act] {action_type} {terminal.ANSI_RESET}{action_detail}"
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
                f"{terminal.ANSI_GREEN}[Self-Operating Computer]{terminal.ANSI_RED}[Error] something went wrong :({terminal.ANSI_RESET}"
            )
            print(
                f"{terminal.ANSI_GREEN}[Self-Operating Computer]{terminal.ANSI_RED}[Error] AI response\n{terminal.ANSI_RESET}{response}"
            )
            break

        print(
            f"{terminal.ANSI_GREEN}[Self-Operating Computer]{terminal.ANSI_BRIGHT_MAGENTA} [Act] {action_type} COMPLETE {terminal.ANSI_RESET}{function_response}"
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
    prompt = prompts.SUMMARY_PROMPT.format(objective=objective)
    return prompt


def format_vision_prompt(objective, previous_action):
    """
    Format the vision prompt
    """
    if previous_action:
        previous_action = f"Here was the previous action you took: {previous_action}"
    else:
        previous_action = ""
    prompt = prompts.VISION_PROMPT.format(objective=objective, previous_action=previous_action)
    return prompt


def format_accurate_mode_vision_prompt(prev_x, prev_y):
    """
    Format the accurate mode vision prompt
    """
    width = ((ACCURATE_PIXEL_COUNT / 2) / monitor_size["width"]) * 100
    height = ((ACCURATE_PIXEL_COUNT / 2) / monitor_size["height"]) * 100
    prompt = prompts.ACCURATE_MODE_VISION_PROMPT.format(
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

                if settings.debug:
                    print(
                        f"Previous coords before accurate tuning: prev_x {prev_x} prev_y {prev_y}"
                    )
                content = accurate_mode_double_check(pseudo_messages, prev_x, prev_y)
                assert content != "ERROR", "ERROR: accurate_mode_double_check failed"

        return content

    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return "Failed take action after looking at the screenshot"


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
        print(f"Error in summarize: {e}")
        return "Failed to summarize the workflow"


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
    import time

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
