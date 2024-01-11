import os
import time
import json
import base64
import re
import io
import asyncio
import aiohttp
import requests

from PIL import Image
from ultralytics import YOLO
import google.generativeai as genai
from operate.settings import Config
from operate.exceptions import ModelNotRecognizedException
from operate.utils.screenshot import (
    capture_screen_with_cursor,
    add_grid_to_image,
    capture_mini_screenshot_with_cursor,
)
from operate.utils.os import get_last_assistant_message
from operate.prompts import (
    format_vision_prompt,
    format_accurate_mode_vision_prompt,
    format_summary_prompt,
    format_decision_prompt,
    format_label_prompt,
)


from operate.utils.label import (
    add_labels,
    parse_click_content,
    get_click_position_in_percent,
    get_label_coordinates,
)
from operate.utils.style import (
    ANSI_GREEN,
    ANSI_RED,
    ANSI_RESET,
)


# Load configuration
config = Config()

client = config.initialize_openai_client()

yolo_model = YOLO("./operate/model/weights/best.pt")  # Load your trained model


async def get_next_action(model, messages, objective, session_id):
    if model == "gpt-4":
        return [call_gpt_4_v(messages, objective)]
    if model == "gpt-4-with-som":
        return await [call_gpt_4_v_labeled(messages, objective)]
    elif model == "agent-1":
        return [call_agent_1(session_id, objective)]
    elif model == "gemini-pro-vision":
        return [call_gemini_pro_vision(messages, objective)]

    raise ModelNotRecognizedException(model)


def call_agent_1(session_id, objective):
    print("[call_agent_1]")
    time.sleep(1)
    try:
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")

        capture_screen_with_cursor(screenshot_filename)

        with open(screenshot_filename, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode("utf-8")

        print("[call_agent_1] about to fetch_agent_1_response")
        response = fetch_agent_1_response(session_id, objective, base64_image)
        print("[call_agent_1] response", response)

        return response
    except Exception as e:
        print(f"Error: {e}")
        return "Failed take action after looking at the screenshot"


def call_gpt_4_v(messages, objective):
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

        return content

    except Exception as e:
        print(f"Error: {e}")
        return "Failed take action after looking at the screenshot"


def call_gemini_pro_vision(messages, objective):
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
        print(f"Error: {e}")
        return "Failed take action after looking at the screenshot"


# This function is not used. `-accurate` mode was removed for now until a new PR fixes it.
def accurate_mode_double_check(model, pseudo_messages, prev_x, prev_y):
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


async def call_gpt_4_v_labeled(messages, objective):
    time.sleep(1)
    try:
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")
        # Call the function to capture the screen with the cursor
        capture_screen_with_cursor(screenshot_filename)

        with open(screenshot_filename, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        previous_action = get_last_assistant_message(messages)

        img_base64_labeled, img_base64_original, label_coordinates = add_labels(
            img_base64, yolo_model
        )

        decision_prompt = format_decision_prompt(objective, previous_action)
        labeled_click_prompt = format_label_prompt(objective)

        click_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": labeled_click_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_base64_labeled}"
                    },
                },
            ],
        }
        decision_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": decision_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_base64_original}"
                    },
                },
            ],
        }

        click_messages = messages.copy()
        click_messages.append(click_message)
        decision_messages = messages.copy()
        decision_messages.append(decision_message)

        click_future = fetch_openai_response_async(click_messages)
        decision_future = fetch_openai_response_async(decision_messages)

        click_response, decision_response = await asyncio.gather(
            click_future, decision_future
        )

        # Extracting the message content from the ChatCompletionMessage object
        click_content = click_response.get("choices")[0].get("message").get("content")

        decision_content = (
            decision_response.get("choices")[0].get("message").get("content")
        )

        if not decision_content.startswith("CLICK"):
            return decision_content

        label_data = parse_click_content(click_content)

        if label_data and "label" in label_data:
            coordinates = get_label_coordinates(label_data["label"], label_coordinates)
            image = Image.open(
                io.BytesIO(base64.b64decode(img_base64))
            )  # Load the image to get its size
            image_size = image.size  # Get the size of the image (width, height)
            click_position_percent = get_click_position_in_percent(
                coordinates, image_size
            )
            if not click_position_percent:
                print(
                    f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] Failed to get click position in percent. Trying another method {ANSI_RESET}"
                )
                return call_gpt_4_v(messages, objective)

            x_percent = f"{click_position_percent[0]:.2f}%"
            y_percent = f"{click_position_percent[1]:.2f}%"
            click_action = f'CLICK {{ "x": "{x_percent}", "y": "{y_percent}", "description": "{label_data["decision"]}", "reason": "{label_data["reason"]}" }}'

        else:
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] No label found. Trying another method {ANSI_RESET}"
            )
            return call_gpt_4_v(messages, objective)

        return click_action

    except:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] Something went wrong. Trying another method {ANSI_RESET}"
        )
        return call_gpt_4_v(messages, objective)


def fetch_agent_1_response(session_id, objective, base64_image):
    print("[call_agent_1][fetch_agent_1_response]")
    url = "http://127.0.0.1:5000/agent/v1/action"
    api_token = os.environ.get("AGENT_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }
    data = {
        "session_id": session_id,
        "objective": objective,
        "image": f"data:image/jpeg;base64,{base64_image}",
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("[call_agent_1][fetch_agent_1_response] response", response.text)
    return response.text


async def fetch_openai_response_async(messages):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.openai_api_key}",
    }
    data = {
        "model": "gpt-4-vision-preview",
        "messages": messages,
        "frequency_penalty": 1,
        "presence_penalty": 1,
        "temperature": 0.7,
        "max_tokens": 300,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, headers=headers, data=json.dumps(data)
        ) as response:
            return await response.json()
