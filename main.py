"""
Self Driving Computer
"""
import os
import requests
import time
import base64
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import message_dialog, button_dialog
from prompt_toolkit.styles import Style as PromptStyle
from colorama import Fore, Style as ColoramaStyle
from dotenv import load_dotenv
from PIL import ImageGrab, Image, ImageDraw, ImageFont


load_dotenv()  # This method will load the variables from .env

# Now you can use the environment variables, e.g.,
replicate_api_key = os.getenv("REPLICATE_API_TOKEN")

PROMPT = """
Objective: {objective}
Based on this objective, what x & y location should we first click on this screenshot. Use this format below. 

{{ x: 'some x coordinate', y: 'some y coordinate' }}

Respond with the json object and nothing else. 
"""


def format_prompt(objective):
    return PROMPT.format(objective=objective)


def call_api(objective):
    print("Calling API")
    print("[replicate_api_key], ", replicate_api_key)
    visual_prompt = format_prompt(objective)
    # Load the image and convert it to base64
    with open("screenshot_with_labeled_grid.png", "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    # Prepare the payload
    payload = {
        "version": "2facb4a474a0462c15041b78b1ad70952ea46b5ec6ad29583c0b29dbd4249591",
        "input": {
            "image": f"data:image/png;base64,{img_base64}",
            "prompt": visual_prompt,
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
    print("initial request response", response.json())

    # Get the prediction ID
    prediction_id = response.json()["id"]

    # Poll the "get" URL until the prediction is ready
    while True:
        print("Polling prediction status")
        response = requests.get(
            f"https://api.replicate.com/v1/predictions/{prediction_id}", headers=headers
        )
        print("polling response", response.json())
        status = response.json()["status"]
        if status == "succeeded":
            print("Prediction succeeded")
            output = response.json()["output"]
            print(f"output, {output}")
            return output
            break
        elif status == "failed":
            print("Prediction failed")
            return "failed"
            break

        time.sleep(1)  # wait a second before checking again


# Define style
style = PromptStyle.from_dict(
    {
        "dialog": "bg:#88ff88",
        "button": "bg:#ffffff #000000",
        "dialog.body": "bg:#44cc44 #ffffff",
        "dialog shadow": "bg:#003800",
    }
)


def add_labeled_grid_to_image(image_path, grid_interval):
    # Load the image
    image = Image.open(image_path)

    # Create a drawing object
    draw = ImageDraw.Draw(image)

    # Get the image size
    width, height = image.size

    # Define a larger font for the labels
    font_size = 20
    try:
        # Try to use a default font
        font = ImageFont.truetype("arial.ttf", size=font_size)
    except IOError:
        # If the default font is not available, a fallback font will be used.
        font = ImageFont.load_default()

    # Calculate label background size based on the font size
    label_background_size = (font_size + 6, font_size + 6)

    # Function to draw text with a white rectangle background
    def draw_label_with_background(position, text, font_size):
        background_position = (
            position[0],
            position[1],
            position[0] + label_background_size[0],
            position[1] + label_background_size[1],
        )
        draw.rectangle(background_position, fill="white")
        draw.text((position[0] + 3, position[1] + 3), text, fill="black", font=font)

    # Draw vertical lines at every `grid_interval` pixels
    for x in range(0, width, grid_interval):
        line = ((x, 0), (x, height))
        draw.line(line, fill="blue")
        # Add the label to the right of the line with a white background
        draw_label_with_background((x + 2, 2), str(x), font_size)

    # Draw horizontal lines at every `grid_interval` pixels
    for y in range(0, height, grid_interval):
        line = ((0, y), (width, y))
        draw.line(line, fill="blue")
        # Add the label below the line with a white background
        draw_label_with_background((2, y + 2), str(y), font_size)

    # Save the image with the grid
    image.save("screenshot_with_labeled_grid.png")


# Assuming you have saved


def main():
    message_dialog(
        title="Self Driving Computer",
        text="Ask a computer to do anything.",
        style=style,
    ).run()

    os.system("clear")  # Clears the terminal screen

    bot_1_name = prompt("What would you like the computer to do? ")
    print(f"bot_1_name: {bot_1_name}")

    screen = ImageGrab.grab()

    # Save the image file
    screen.save("screenshot.png")

    add_labeled_grid_to_image("screenshot.png", 100)
    print("Screenshot saved")
    print("about to call api")

    result = call_api(bot_1_name)
    prompt(f"result: {result}")

    # os.system("clear")  # Clears the terminal screen


if __name__ == "__main__":
    main()
