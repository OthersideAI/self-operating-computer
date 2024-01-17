import os
import time
import json
import base64
import traceback
import io
import requests


from PIL import Image
from ultralytics import YOLO
import google.generativeai as genai
from operate.config import Config
from operate.exceptions import ModelNotRecognizedException
from operate.utils.screenshot import (
    capture_screen_with_cursor,
)
from operate.models.prompts import (
    get_user_first_message_prompt,
    get_user_prompt,
    get_system_prompt,
)


from operate.utils.label import (
    add_labels,
    get_click_position_in_percent,
    get_label_coordinates,
)
from operate.utils.style import (
    ANSI_GREEN,
    ANSI_RED,
    ANSI_RESET,
)


# Load configuration
VERBOSE = Config().verbose


async def get_next_action(model, messages, objective, session_id):
    if model == "gpt-4":
        return call_gpt_4_vision_preview(messages), None
    if model == "gpt-4-with-som":
        operation = await call_gpt_4_vision_preview_labeled(messages, objective)
        return operation, None
    elif model == "agent-1":
        operation, session_id = call_agent_1(session_id, objective, messages)
        return operation, session_id
    elif model == "gemini-pro-vision":
        return call_gemini_pro_vision(messages, objective), None

    raise ModelNotRecognizedException(model)


def call_gpt_4_vision_preview(messages):
    config = Config()
    client = config.initialize_openai()
    if VERBOSE:
        print("[Self Operating Computer][get_next_action][call_gpt_4_v]")
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

        if len(messages) == 1:
            user_prompt = get_user_first_message_prompt()
        else:
            user_prompt = get_user_prompt()

        if VERBOSE:
            print(
                "[Self Operating Computer][get_next_action][call_gpt_4_v] user_prompt",
                user_prompt,
            )

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
            max_tokens=3000,
        )

        content = response.choices[0].message.content

        if content.startswith("```json"):
            content = content[len("```json") :]  # Remove starting ```json
            if content.endswith("```"):
                content = content[: -len("```")]  # Remove ending

        assistant_message = {"role": "assistant", "content": content}
        if VERBOSE:
            print(
                "[Self Operating Computer][get_next_action][call_gpt_4_v] content",
                content,
            )
        content = json.loads(content)

        messages.append(assistant_message)

        return content

    except Exception as e:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] Something went wrong. Trying again {ANSI_RESET}",
            e,
        )
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] AI response was {ANSI_RESET}",
            content,
        )
        traceback.print_exc()
        return call_gpt_4_vision_preview(messages)


def call_agent_1(session_id, objective, messages):
    print("[call_agent_1]")
    time.sleep(1)
    response = ""
    try:
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")

        print("[call_agent_1] screenshot_filename", screenshot_filename)

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
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] Something went wrong. Trying again {ANSI_RESET}",
            e,
        )
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] AI response was {ANSI_RESET}",
            response,
        )
        traceback.print_exc()
        return call_gpt_4_vision_preview(messages)


def call_gemini_pro_vision(messages, objective):
    """
    Get the next action for Self-Operating Computer using Gemini Pro Vision
    """
    config = Config()
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
        prompt = get_system_prompt(objective)

        model = genai.GenerativeModel("gemini-pro-vision")

        response = model.generate_content([prompt, Image.open(screenshot_filename)])

        content = response.text[1:]

        content = json.loads(content)
        if VERBOSE:
            print(
                "[Self Operating Computer][get_next_action][call_gemini_pro_vision] content",
                content,
            )

        return content

    except Exception as e:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] Something went wrong. Trying another method {ANSI_RESET}",
            e,
        )
        return call_gpt_4_vision_preview(messages)


async def call_gpt_4_vision_preview_labeled(messages, objective):
    config = Config()
    client = config.initialize_openai()
    time.sleep(1)
    try:
        yolo_model = YOLO("./operate/models/weights/best.pt")  # Load your trained model
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")
        # Call the function to capture the screen with the cursor
        capture_screen_with_cursor(screenshot_filename)

        with open(screenshot_filename, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        img_base64_labeled, label_coordinates = add_labels(img_base64, yolo_model)

        if len(messages) == 1:
            user_prompt = get_user_first_message_prompt()
        else:
            user_prompt = get_user_prompt()

        if VERBOSE:
            print(
                "[Self Operating Computer][get_next_action][call_gpt_4_vision_preview_labeled] user_prompt",
                user_prompt,
            )

        vision_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": user_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_base64_labeled}"
                    },
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
        if VERBOSE:
            print(
                "[Self Operating Computer][get_next_action][call_gpt_4_vision_preview_labeled] content",
                content,
            )
        messages.append(assistant_message)

        content = json.loads(content)

        processed_content = []

        for operation in content:
            if operation.get("operation") == "click":
                label = operation.get("label")
                if VERBOSE:
                    print(
                        "[Self Operating Computer][get_next_action][call_gpt_4_vision_preview_labeled] label",
                        label,
                    )

                coordinates = get_label_coordinates(label, label_coordinates)
                if VERBOSE:
                    print(
                        "[Self Operating Computer][get_next_action][call_gpt_4_vision_preview_labeled] coordinates",
                        coordinates,
                    )
                image = Image.open(
                    io.BytesIO(base64.b64decode(img_base64))
                )  # Load the image to get its size
                image_size = image.size  # Get the size of the image (width, height)
                click_position_percent = get_click_position_in_percent(
                    coordinates, image_size
                )
                if VERBOSE:
                    print(
                        "[Self Operating Computer][get_next_action][call_gpt_4_vision_preview_labeled] click_position_percent",
                        click_position_percent,
                    )
                if not click_position_percent:
                    print(
                        f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] Failed to get click position in percent. Trying another method {ANSI_RESET}"
                    )
                    return call_gpt_4_vision_preview(messages)

                x_percent = f"{click_position_percent[0]:.2f}"
                y_percent = f"{click_position_percent[1]:.2f}"
                operation["x"] = x_percent
                operation["y"] = y_percent
                if VERBOSE:
                    print(
                        "[Self Operating Computer][get_next_action][call_gpt_4_vision_preview_labeled] new click operation",
                        operation,
                    )
                processed_content.append(operation)
            else:
                processed_content.append(operation)

            if VERBOSE:
                print(
                    "[Self Operating Computer][get_next_action][call_gpt_4_vision_preview_labeled] new processed_content",
                    processed_content,
                )
            return processed_content

    except Exception as e:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] Something went wrong. Trying another method {ANSI_RESET}",
            e,
        )
        return call_gpt_4_vision_preview(messages)


def fetch_agent_1_response(session_id, objective, base64_image):
    if VERBOSE:
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
    response_dict = response.json()
    operations = response_dict.get("operations")
    session_id = response_dict.get("session_id")

    return operations, session_id


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
