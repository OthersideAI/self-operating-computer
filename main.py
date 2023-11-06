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
from PIL import ImageGrab


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
    with open("screenshot.png", "rb") as img_file:
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
    print("Screenshot saved")
    print("about to call api")

    result = call_api(bot_1_name)
    prompt(f"result: {result}")

    # os.system("clear")  # Clears the terminal screen


if __name__ == "__main__":
    main()
