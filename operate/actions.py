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
)
from operate.prompts import (
    format_vision_prompt,
    format_summary_prompt,
    format_decision_prompt,
    format_label_prompt,
    get_user_first_message_prompt,
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
    print("[get_next_action]")
    if model == "gpt-4":
        return call_gpt_4_v(messages), None
    if model == "gpt-4-with-som":
        operation = await call_gpt_4_v_labeled(messages, objective)
        return [operation], None
    elif model == "agent-1":
        operation, session_id = call_agent_1(session_id, objective)
        print("[get_next_action] returning operation", operation)
        print("[get_next_action] returning session_id", session_id)
        return operation, session_id
    elif model == "gemini-pro-vision":
        return [call_gemini_pro_vision(messages, objective)], None

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
        response, session_id = fetch_agent_1_response(
            session_id, objective, base64_image
        )
        print("[call_agent_1] response", response)

        return response, session_id
    except Exception as e:
        print(f"Error: {e}")
        return "Failed take action after looking at the screenshot"


def call_gpt_4_v(messages):
    """
    Get the next action for Self-Operating Computer
    """
    print("[call_gpt_4_v]")
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

        user_prompt = get_user_first_message_prompt()

        print("[call_gpt_4_v] user_message", user_prompt)

        vision_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": user_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                },
            ],
        }
        messages.append(vision_message)

        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            presence_penalty=1,
            frequency_penalty=1,
            temperature=0.7,
            max_tokens=1000,
        )

        content = response.choices[0].message.content

        if content.startswith("```json"):
            content = content[len("```json") :]  # Remove starting ```json
            if content.endswith("```"):
                content = content[: -len("```")]  # Remove ending

        assistant_message = {"role": "assistant", "content": content}
        print("[call_gpt_4_v] content", content)
        messages.append(assistant_message)

        content = json.loads(content)

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
        # sleep for a second
        time.sleep(1)

        previous_action = get_last_assistant_message(messages)

        vision_prompt = format_vision_prompt(objective, previous_action)

        model = genai.GenerativeModel("gemini-pro-vision")

        response = model.generate_content(
            [vision_prompt, Image.open(screenshot_filename)]
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
                return call_gpt_4_v(messages)

            x_percent = f"{click_position_percent[0]:.2f}%"
            y_percent = f"{click_position_percent[1]:.2f}%"
            click_action = f'CLICK {{ "x": "{x_percent}", "y": "{y_percent}", "description": "{label_data["decision"]}", "reason": "{label_data["reason"]}" }}'

        else:
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] No label found. Trying another method {ANSI_RESET}"
            )
            return call_gpt_4_v(messages)

        return click_action

    except:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] Something went wrong. Trying another method {ANSI_RESET}"
        )
        return call_gpt_4_v(messages)


def fetch_agent_1_response(session_id, objective, base64_image):
    print("[call_agent_1][fetch_agent_1_response]")
    url = "http://127.0.0.1:5000/agent/v2/action"
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
    response_dict = response.json()
    operations = response_dict.get("operations")
    session_id = response_dict.get("session_id")

    return operations, session_id


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
