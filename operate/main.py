"""
Self-Operating Computer
"""
import os
import time
import base64
import json
import math
import re
import pyautogui

from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.styles import Style as PromptStyle
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import matplotlib.font_manager as fm
import subprocess
from openai import OpenAI

load_dotenv()

DEBUG = False

client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

VISION_PROMPT = """
You are a Self-Operating Computer. You use the same operating system (i.e. screen user interface, click & type, etc.) as a human.

From looking at the screen, the objective and you previous steps, your goal is to take the best next action to reach the objective. 

To complete emulate a human operator you only need three actions. These are the actions available to you below. 

1. CLICK - Move mouse and click
2. TYPE - Type on the keyboard
3. SEARCH - Search for a program on Mac and open it
4. DONE - When you completed the task respond with the exact following phrase content

Here are your formats for how to respond. 

1. CLICK
Response: CLICK {{ "x": "percent", "y": "percent", "description": "~description of what you're clicking~" }} 

2. TYPE
Response: TYPE "value you want to type"

2. SEARCH
Response: SEARCH "app you want to search for on Mac"

3. DONE
Response: DONE

Here are examples of how to respond which depend on which step you are on.
__
Objective: Open Notes
DONE
__
Objective: Find a image of a banana
CLICK {{ "x": "50%", "y": "60%", "description": "Clicking the Google Search field" }} 
__
Objective: Follow up with the vendor in outlook
TYPE "Hello, I hope you are doing well. I wanted to follow up"
__
Objective: Open Spotify and play the beatles
CLICK {{ "x": "20%", "y": "92%", "description": "Clicking the play button under the beatles song" }}
__
Objective: Open Spotify and play the beatles
SEARCH "Spotify"
__


A few important notes: 
- Use grid with percentages as a guide to guess the X & Y location, but avoid clicking exactly at the grid cross hairs since they are unlikely to be the exact location.
- When opening Google Chrome if you see profile buttons, click the profile button at the following location {{ "x": "50%", "y": "55%" }} to fully open Chrome.
- The address bar for Chrome while in full screen is around {{ "x": "50%", "y": "8%" }}.
- Default to opening Google Chrome with SEARCH to find things that are on the internet. 
- Make sure that a field is active before using TYPE
- When doing TYPE in a field that requires a submission do not forget to press enter after typing (such as in Google Search)

VERY IMPORTANT: Look closely at the image and question what you see. Always use the screen to evaluate where you are and make the best next action.

Objective: {objective}
"""

USER_QUESTION = "Hello, I can help you with anything. What would you like done?"

SUMMARY_PROMPT = """"""

# Define style
style = PromptStyle.from_dict(
    {
        "dialog": "bg:#88ff88",
        "button": "bg:#ffffff #000000",
        "dialog.body": "bg:#44cc44 #ffffff",
        "dialog shadow": "bg:#003800",
    }
)
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


def main():
    """
    Main function for the Self-Operating Computer
    """
    message_dialog(
        title="Self-Operating Computer",
        text="Ask a computer to do anything.",
        style=style,
    ).run()

    os.system("clear")  # Clears the terminal screen

    print(f"{ANSI_GREEN}[Self-Operating Computer]\n{ANSI_RESET}{USER_QUESTION}")
    print(f"{ANSI_YELLOW}[User]{ANSI_RESET}")

    objective = prompt(
        style=style,
    )

    assistant_message = {"role": "assistant", "content": USER_QUESTION}
    user_message = {
        "role": "user",
        "content": objective,
    }
    messages = [assistant_message, user_message]

    looping = True
    loop_count = 0

    while looping:
        if DEBUG:
            print("[loop] messages before next action:\n\n\n", messages[1:])
        response = get_next_action(messages, objective)

        action = parse_oai_response(response)
        action_type = action.get("type")
        action_detail = action.get("data")

        if action_type == "DONE":
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BLUE} Objective complete {ANSI_RESET}"
            )
            looping = False
            break
            # summary = summarize(messages, objective)
            # print(
            #     f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BLUE} Summary\n{ANSI_RESET}{summary}"
            # )

        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BLUE}[Act] {action_type} {ANSI_RESET}{action_detail}"
        )

        function_response = ""
        if action_type == "SEARCH":
            function_response = mac_search(action_detail)
        elif action_type == "TYPE":
            function_response = keyboard_type(action_detail)
        elif action_type == "CLICK":
            function_response = mouse_click(action_detail)
        else:
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]\n{ANSI_RESET}Oh no, I broke :("
            )
            looping = False
            break
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BLUE}[Act] Result {ANSI_RESET}{function_response}"
        )

        message = {
            "role": "assistant",
            "content": function_response,
        }
        messages.append(message)

        loop_count += 1
        if loop_count > 10:
            looping = False


def format_summary_prompt():
    """
    Format the summary prompt
    """
    return SUMMARY_PROMPT


def format_vision_prompt(objective):
    prompt = VISION_PROMPT.format(objective=objective)
    if DEBUG:
        print("[format_vision_prompt] prompt", prompt)

    return prompt


def get_next_action(messages, objective):
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

        new_screenshot_filename = "screenshots/screenshot_with_grid.png"

        add_grid_to_image(screenshot_filename, new_screenshot_filename, 650)

        with open(new_screenshot_filename, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        vision_prompt = format_vision_prompt(objective)

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

        messages.append(
            {
                "role": "user",
                "content": "~User shared a screenshot with you which has since been archived~",
            }
        )

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=pseudo_messages,
            max_tokens=300,
        )

        content = response.choices[0].message.content
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

    else:
        return {"type": "UNKNOWN", "data": None}


def summarize(messages):
    summary_prompt = format_summary_prompt(objective)

    messages.append({"role": "user", "content": summary_prompt})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=300,
    )

    result = response.choices[0]
    content = result.message.content

    return content


def mouse_click(click_detail):
    try:
        x = convert_percent_to_decimal(click_detail["x"])
        y = convert_percent_to_decimal(click_detail["y"])

        if click_detail and isinstance(x, float) and isinstance(y, float):
            click_at_percentage(x, y)
            return "CLICK SUCCESSFUL:" + click_detail["description"]
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

    # Get the path to a TrueType font included with matplotlib
    font_paths = fm.findSystemFonts(fontpaths=None, fontext="ttf")
    # Filter for specific font name (e.g., 'Arial.ttf')
    font_path = next((path for path in font_paths if "Arial" in path), None)
    if not font_path:
        raise RuntimeError(
            "Specific TrueType font not found; install the font or check the font name."
        )

    # Reduce the font size a bit
    font_size = int(grid_interval / 10)  # Reduced font size
    font = ImageFont.truetype(font_path, size=font_size)

    # Calculate the background size based on the font size
    bg_width = int(font_size * 4)  # Adjust as necessary
    bg_height = int(font_size * 1.2)  # Adjust as necessary

    # Function to draw text with a white rectangle background
    def draw_label_with_background(position, text, draw, font, bg_width, bg_height):
        # Adjust the position based on the background size
        text_position = (position[0] + bg_width // 2, position[1] + bg_height // 2)
        # Draw the text background
        draw.rectangle(
            [position[0], position[1], position[0] + bg_width, position[1] + bg_height],
            fill="white",
        )
        # Draw the text
        draw.text(text_position, text, fill="black", font=font, anchor="mm")

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
                font,
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
    for char in text:
        pyautogui.write(char)
    return "Successfully typed: " + text


def mac_search(text):
    # Press and release Command and Space separately
    pyautogui.keyDown("command")
    pyautogui.press("space")
    pyautogui.keyUp("command")
    # Now type the text
    for char in text:
        pyautogui.write(char)

    pyautogui.press("enter")
    return "successfully opened " + text + " on Mac"


def capture_screen_with_cursor(file_path="screenshots/screenshot_with_cursor.png"):
    # Use the screencapture utility to capture the screen with the cursor
    subprocess.run(["screencapture", "-C", file_path])


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


if __name__ == "__main__":
    main()
