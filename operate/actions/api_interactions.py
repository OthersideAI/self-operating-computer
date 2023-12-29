import os
import time
import json
import base64
import re
from PIL import Image
import google.generativeai as genai
from operate.config.settings import Config
from operate.exceptions.exceptions import ModelNotRecognizedException
from operate.utils.screenshot_util import capture_screen_with_cursor, add_grid_to_image, capture_mini_screenshot_with_cursor
from operate.utils.action_util import get_last_assistant_message
from operate.utils.prompt_util import format_vision_prompt, format_accurate_mode_vision_prompt,format_summary_prompt

# Load configuration
config = Config()
client = config.initialize_openai_client()


def get_next_action(model, messages, objective, accurate_mode):
    if model == "gpt-4-vision-preview":
        content = get_next_action_from_openai(
            messages, objective, accurate_mode)
        return content
    elif model == "agent-1":
        return "coming soon"
    elif model == "gemini-pro-vision":
        content = get_next_action_from_gemini_pro_vision(
            messages, objective
        )
        return content

    raise ModelNotRecognizedException(model)


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

                if config.debug:
                    print(
                        f"Previous coords before accurate tuning: prev_x {prev_x} prev_y {prev_y}"
                    )
                content = accurate_mode_double_check(
                    "gpt-4-vision-preview", pseudo_messages, prev_x, prev_y
                )
                assert content != "ERROR", "ERROR: accurate_mode_double_check failed"

        return content

    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return "Failed take action after looking at the screenshot"


def get_next_action_from_gemini_pro_vision(messages, objective):
    """
    Get the next action for Self-Operating Computer using Gemini Pro Vision
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

        previous_action = get_last_assistant_message(messages)

        vision_prompt = format_vision_prompt(objective, previous_action)

        model = genai.GenerativeModel("gemini-pro-vision")

        response = model.generate_content(
            [vision_prompt, Image.open(new_screenshot_filename)]
        )

        # create a copy of messages and save to pseudo_messages
        pseudo_messages = messages.copy()
        pseudo_messages.append(response.text)

        messages.append(
            {
                "role": "user",
                "content": "`screenshot.png`",
            }
        )
        content = response.text[1:]

        return content

    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return "Failed take action after looking at the screenshot"


def accurate_mode_double_check(model, pseudo_messages, prev_x, prev_y):
    """
    Reprompt OAI with additional screenshot of a mini screenshot centered around the cursor for further finetuning of clicked location
    """
    print("[get_next_action_from_gemini_pro_vision] accurate_mode_double_check")
    try:
        screenshot_filename = os.path.join(
            "screenshots", "screenshot_mini.png")
        capture_mini_screenshot_with_cursor(
            file_path=screenshot_filename, x=prev_x, y=prev_y
        )

        new_screenshot_filename = os.path.join(
            "screenshots", "screenshot_mini_with_grid.png"
        )

        with open(new_screenshot_filename, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        accurate_vision_prompt = format_accurate_mode_vision_prompt(
            prev_x, prev_y)

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

    except Exception as e:
        print(f"Error reprompting model for accurate_mode: {e}")
        return "ERROR"


def summarize(model, messages, objective):
    try:
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        screenshot_filename = os.path.join(screenshots_dir, "summary_screenshot.png")
        # Call the function to capture the screen with the cursor
        capture_screen_with_cursor(screenshot_filename)

        summary_prompt = format_summary_prompt(objective)
        
        if model == "gpt-4-vision-preview":
            with open(screenshot_filename, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

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
        elif model == "gemini-pro-vision":
            model = genai.GenerativeModel("gemini-pro-vision")
            summary_message = model.generate_content(
                [summary_prompt, Image.open(screenshot_filename)]
            )
            content = summary_message.text
        return content
    
    except Exception as e:
        print(f"Error in summarize: {e}")
        return "Failed to summarize the workflow"