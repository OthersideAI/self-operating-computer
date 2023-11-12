"""
Self Driving Computer
"""
import os
import time
import base64
import json
import math


from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.styles import Style as PromptStyle
from colorama import Style as ColoramaStyle
from dotenv import load_dotenv
from PIL import ImageGrab, Image, ImageDraw, ImageFont
import matplotlib.font_manager as fm
import pyautogui
import subprocess
import os


from openai import OpenAI


load_dotenv()

client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")


# Define style
style = PromptStyle.from_dict(
    {
        "dialog": "bg:#88ff88",
        "button": "bg:#ffffff #000000",
        "dialog.body": "bg:#44cc44 #ffffff",
        "dialog shadow": "bg:#003800",
    }
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "mouse_click",
            "description": "This function clicks fields, buttons, and windows on the screen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "A description of the click location.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "keyboard_type",
            "description": "This function types the specified text on the keyboard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "type_value": {
                        "type": "string",
                        "description": "The text to type on the keyboard.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mac_search",
            "description": "This function searches on Mac for programs",
            "parameters": {
                "type": "object",
                "properties": {
                    "type_value": {
                        "type": "string",
                        "description": "The text to do on Mac search.",
                    },
                },
            },
        },
    },
]


CLICK_PROMPT = """
From looking at a screenshot, your goal is to guess the X & Y location of a window or field on the screen in order to fire a click event. The X & Y location are in percentage (%) of screen width and height.

Your job is to click on windows or fields that will progress you towards your objective. 

Example are below.
__
Objective: Find a image of a banana
Click: {{ "x": "0.5", "y": "0.6", "explanation": "I can see a Google Search field, I'm going to click that so I can search." }} 
__
Objective: Write an email to Best buy and ask for computer support
Click: {{ "x": "0.2", "y": "0.1", "explanation": "It looks like this is where the email compose window is" }} 
__
Objective: Open Spotify and play the beatles
Click: {{ "x": "0.2", "y": "0.9", "explanation": "I see spotify is " }}
__


A few important notes: 
- Respond with nothing but the `{{ "x": "percent", "y": "percent",  "explanation": "explanation here" }}` and do not comment additionally.
- When entering a search field or document click a little to the right of where the field enters to ensure you are in the field.
- When clicking a button try to click in the lower middle of the button
- If opening Google Chrome, first click the Profile Button to open the Browser. The profile button is generally near the center of the screen around {{ "x": "0.5", "y": "0.55" }}

Objective: {objective}
Click:
"""


PROMPT_TYPE = """
You are a professional writer. Based on the objective below, decide what you should write. 

IMPORTANT: Respond directly with what you are going to write and nothing else!

Objective: {objective}
Writing:
"""

USER_QUESTION = "What would you like the computer to do?"

SYSTEM_PROMPT = """
You are a Self Operating Computer. You use the same visual and input interfaces (i.e. screenshot, click & type) as a human, except you are superhuman. 

You will receive an objective from the user and you will decide the exact click and keyboard type actions to accomplish that goal. 

You have the tools (i.e. functions) below to accomplish the task.

1. `mouse_click` Move mouse and click
2. `keyboard_type` Type on the keyboard
3. `mac_search` Search for a program on Mac

A few important notes: 
- It is important to know that before you use `keyboard_type` in a new program you just opened you often need to `mouse_click` at the location where you want to type. 
- Default to opening Google Chrome with `mac_search` to find things that are on the internet. 


When you completed the task respond with the exact following phrase content: DONE
"""

USER_TOOL_PROMPT = """
Objective: {objective}
"""

# def agent_loop():


def format_click_prompt(objective):
    return CLICK_PROMPT.format(objective=objective)


def format_prompt_tool(objective):
    return USER_TOOL_PROMPT.format(objective=objective)


def get_next_action(messages):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )

    return response.choices[0].message


def click_at_percentage(
    x_percentage, y_percentage, duration=0.5, circle_radius=50, circle_duration=0.5
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
    return "successfully clicked"


def mouse_click(objective):
    with open("screenshot.png", "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    click_prompt = format_click_prompt(objective)
    print("[mouse_click] click_prompt", click_prompt)
    # pdb break
    # import pdb

    # pdb.set_trace()

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": click_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                    },
                ],
            }
        ],
        max_tokens=300,
    )

    result = response.choices[0]
    content = result.message.content
    print("[mouse_click] content", content)
    parsed_result = extract_json_from_string(content)
    if parsed_result:
        click_at_percentage(parsed_result["x"], parsed_result["y"])
        return parsed_result.get("explanation", "successfully clicked")

    return "We failed to click"


def add_labeled_grid_to_image(image_path, grid_interval):
    # Load the image
    image = Image.open(image_path)

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

    font_size = grid_interval / 4  # Adjust this size as needed
    font = ImageFont.truetype(font_path, size=font_size)

    # Define the estimated background size based on the font size
    background_width = (
        font_size * 3
    )  # Estimate that each character is approximately 3 times the font size wide
    background_height = (
        font_size  # The height of the background is the same as the font size
    )

    # Function to draw text with a white rectangle background
    def draw_label_with_background(position, text, draw, font, bg_width, bg_height):
        background_position = (
            position[0],
            position[1],
            position[0] + bg_width,
            position[1] + bg_height,
        )
        draw.rectangle(background_position, fill="white")
        draw.text((position[0] + 3, position[1]), text, fill="black", font=font)

    # Draw vertical lines at every `grid_interval` pixels
    for x in range(0, width, grid_interval):
        line = ((x, 0), (x, height))
        draw.line(line, fill="blue")
        # Add the label to the right of the line with a white background
        draw_label_with_background(
            (x + 2, 2), str(x), draw, font, background_width, background_height
        )

    # Draw horizontal lines at every `grid_interval` pixels
    for y in range(0, height, grid_interval):
        line = ((0, y), (width, y))
        draw.line(line, fill="blue")
        # Add the label below the line with a white background
        draw_label_with_background(
            (2, y + 2), str(y), draw, font, background_width, background_height
        )

    # Save the image with the grid
    image.save("screenshot_with_grid.png")


def add_labeled_cross_grid_to_image(image_path, grid_interval):
    # Load the image
    image = Image.open(image_path)

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

    font_size = grid_interval // 7  # Adjust this size as needed
    font = ImageFont.truetype(font_path, size=int(font_size))

    # Calculate the background size based on the font size
    # Reduce the background to be just larger than the text
    bg_width = int(font_size * 5)  # Adjust as necessary
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

    # Calculate the background size based on the font size

    # Draw vertical lines and labels at every `grid_interval` pixels
    for x in range(grid_interval, width, grid_interval):
        line = ((x, 0), (x, height))
        draw.line(line, fill="blue")
        for y in range(grid_interval, height, grid_interval):
            draw_label_with_background(
                (x - bg_width // 2, y - bg_height // 2),
                f"{x},{y}",
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
    image.save("screenshot_with_grid.png")


def keyboard_type(text):
    for char in text:
        pyautogui.write(char)
    return "successfully typed " + text


def mac_search(text):
    # Press and release Command and Space separately
    pyautogui.keyDown("command")
    pyautogui.press("space")
    pyautogui.keyUp("command")
    # Now type the text
    for char in text:
        pyautogui.write(char)

    time.sleep(1)
    pyautogui.press("enter")
    return "successfully opened " + text + " on Mac"


available_functions = {
    "mouse_click": mouse_click,
    "keyboard_type": keyboard_type,
    "mac_search": mac_search,
}  # only one function in this example, but you can have multiple


def main():
    message_dialog(
        title="Self Operating Computer",
        text="Ask a computer to do anything.",
        style=style,
    ).run()

    os.system("clear")  # Clears the terminal screen

    user_response = prompt(USER_QUESTION + "\n")

    system_prompt = {"role": "system", "content": SYSTEM_PROMPT}
    user_prompt = {
        "role": "user",
        "content": USER_TOOL_PROMPT.format(objective=user_response),
    }
    messages = [system_prompt, user_prompt]

    looping = True
    loop_count = 0

    while looping:
        time.sleep(2)
        response = get_next_action(messages)

        tool_calls = response.tool_calls
        messages.append(response)
        # print("response", response)

        if response.content:
            if response.content == "DONE":
                print("DONE")
                looping = False
                break
            print("[Self Operating Computer] ", response.content)

        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name

                function_args = json.loads(tool_call.function.arguments)
                print("[Use Tool] name: ", function_name)
                print("[Use Tool] args: ", function_args)
                if function_name == "mouse_click":
                    # Call the function to capture the screen with the cursor
                    capture_screen_with_cursor("screenshot.png")
                    # import pdb

                    # pdb.set_traceapple photo()

                    # add_labeled_cross_grid_to_image("screenshot.png", 400)
                    function_response = mouse_click(user_response)

                elif function_name == "keyboard_type":
                    function_response = keyboard_type(function_args["type_value"])
                else:
                    function_response = mac_search(function_args["type_value"])
                print(
                    "[Self Operating Computer] function_response: ", function_response
                )
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

        loop_count += 1
        if loop_count > 10:
            looping = False


def capture_screen_with_cursor(file_path="screenshot_with_cursor.png"):
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


if __name__ == "__main__":
    main()
