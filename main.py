"""
Self Driving Computer
"""
import os
import time
import base64
import json
import math
import time
import requests


from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import message_dialog, button_dialog
from prompt_toolkit.styles import Style as PromptStyle
from colorama import Fore, Style as ColoramaStyle
from dotenv import load_dotenv
from PIL import ImageGrab, Image, ImageDraw, ImageFont
import matplotlib.font_manager as fm
import pyautogui


load_dotenv()  # This method will load the variables from .env

# Now you can use the environment variables, e.g.,
replicate_api_key = os.getenv("REPLICATE_API_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Define style
style = PromptStyle.from_dict(
    {
        "dialog": "bg:#88ff88",
        "button": "bg:#ffffff #000000",
        "dialog.body": "bg:#44cc44 #ffffff",
        "dialog shadow": "bg:#003800",
    }
)

PROMPT_POSITION = """
From looking at a screenshot, your goal is to guess the X & Y location on the screen in order to fire a click event. The X & Y location are in percentage (%) of screen width and height.

Example are below. 
__
Objective: Click on the Banana 
Location: {{ "x": "0.5", "y": "0.6" }} # this means 50% of the way across the page and 60% of the way down the page
__
Objective: Write an email in Outlook
Location: {{ "x": "0.2", "y": "0.1" }} # this is the location of the outlook app
__
Objective: Open Spotify
Location: {{ "x": "0.2", "y": "0.9" }} 
__

IMPORTANT: respond with nothing but the `Location: {{ "x": "percent", "y": "percent" }}` and do not comment.

Ok, here the real test. 

Objective: {objective}

"""

PROMPT_TYPE = """
You are a professional writer. Based on the objective below, decide what you should write. 

IMPORTANT: Respond directly with what you are going to write and nothing else!

Objective: {objective}
Writing:
"""

USER_QUESTION = "What would you like the computer to do?"


def format_prompt_click(objective):
    return PROMPT_POSITION.format(objective=objective)


def format_prompt_type(objective):
    return PROMPT_TYPE.format(objective=objective)


def call_openai_api_for_click(objective):
    # Function to encode the image

    with open("screenshot_with_grid.png", "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    # Path to your image

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }
    v_prompt = format_prompt_click(objective)
    # print("format_prompt_click", v_prompt)
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": v_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                    },
                ],
            }
        ],
        "max_tokens": 300,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    result = response.json()
    content = result["choices"][0]["message"]["content"]
    return content


def call_openai_api_for_type(objective):
    # Function to encode the image

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }
    v_prompt = format_prompt_type(objective)

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": v_prompt,
            }
        ],
        "max_tokens": 1000,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    result = response.json()
    content = result["choices"][0]["message"]["content"]
    return content


def call_replicate_api(objective):
    v_prompt = format_prompt_click(objective)

    # Load the image and convert it to base64
    with open("screenshot_with_grid.png", "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    # Prepare the payload
    payload = {
        "version": "2facb4a474a0462c15041b78b1ad70952ea46b5ec6ad29583c0b29dbd4249591",
        "input": {
            "image": f"data:image/png;base64,{img_base64}",
            "prompt": v_prompt,
        },
    }

    # Prepare the headers
    headers = {
        "Authorization": f"Token {replicate_api_key}",
        "Content-Type": "application/json",
    }

    # Make the request
    response = requests.post(
        "https://api.replicate.com/v1/predictions", json=payload, headers=headers
    )

    # Get the prediction ID
    prediction_id = response.json()["id"]

    # Poll the "get" URL until the prediction is ready
    while True:
        response = requests.get(
            f"https://api.replicate.com/v1/predictions/{prediction_id}", headers=headers
        )
        status = response.json()["status"]

        # print("polling response, status", status)
        if status == "succeeded":
            output = response.json()["output"]
            # concatinate array into string
            final_output = " ".join(output)

            return final_output
            break
        elif status == "failed":
            # print("Prediction failed")
            return "failed"
            break

        time.sleep(1)  # wait a second before checking again


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


def keyboard_type(text, delay=0.00005):
    for char in text:
        pyautogui.write(char)
        # Add a random delay to make it look more like natural typing
        time.sleep(delay)


# Assuming you have saved


def main():
    message_dialog(
        title="Self Operating Computer",
        text="Ask a computer to do anything.",
        style=style,
    ).run()

    os.system("clear")  # Clears the terminal screen

    user_response = prompt(USER_QUESTION + "\n")

    screen = ImageGrab.grab()

    # Save the image file
    screen.save("screenshot.png")

    add_labeled_cross_grid_to_image("screenshot.png", 400)

    click_result = call_openai_api_for_click(user_response)
    type_result = call_openai_api_for_type(user_response)

    try:
        # print(f"click_result: {click_result}")
        # print(f"type_result: {type_result}")

        parsed_result = extract_json_from_string(click_result)
        if parsed_result:
            click_at_percentage(parsed_result["x"], parsed_result["y"])
            keyboard_type(type_result)
        else:
            print("Failed to parse the result")
    except:
        print("failed to handle result")

    # os.system("clear")  # Clears the terminal screen


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
