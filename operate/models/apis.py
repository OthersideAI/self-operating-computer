import os
import time
import json
import base64
import traceback
import io
import easyocr
import ollama

from PIL import Image
from ultralytics import YOLO

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
from operate.utils.ocr import get_text_element, get_text_coordinates


from operate.utils.label import (
    add_labels,
    get_click_position_in_percent,
    get_label_coordinates,
)
from operate.utils.style import ANSI_GREEN, ANSI_RED, ANSI_RESET, ANSI_BRIGHT_MAGENTA
import pkg_resources


# Load configuration
config = Config()


async def get_next_action(model, messages, objective, session_id):
    if config.verbose:
        print("[Self-Operating Computer][get_next_action]")
        print("[Self-Operating Computer][get_next_action] model", model)
    if model == "gpt-4":
        return call_gpt_4_vision_preview(messages), None
    if model == "gpt-4-with-som":
        operation = await call_gpt_4_vision_preview_labeled(messages, objective, model)
        return operation, None
    if model == "gpt-4-with-ocr":
        operation = await call_gpt_4_vision_preview_ocr(messages, objective, model)
        return operation, None
    elif model == "agent-1":
        return "coming soon"
    elif model == "gemini-pro-vision":
        return call_gemini_pro_vision(messages, objective), None
    elif model == "llava":
        operation = call_ollama_llava(messages), None
        return operation

    raise ModelNotRecognizedException(model)


def call_gpt_4_vision_preview(messages):
    if config.verbose:
        print("[call_gpt_4_v]")
    time.sleep(1)
    client = config.initialize_openai()
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

        if config.verbose:
            print(
                "[call_gpt_4_v] user_prompt",
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

        content = clean_json(content)

        assistant_message = {"role": "assistant", "content": content}
        if config.verbose:
            print(
                "[call_gpt_4_v] content",
                content,
            )
        content = json.loads(content)

        messages.append(assistant_message)

        return content

    except Exception as e:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA}[Operate] That did not work. Trying again {ANSI_RESET}",
            e,
        )
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] AI response was {ANSI_RESET}",
            content,
        )
        if config.verbose:
            traceback.print_exc()
        return call_gpt_4_vision_preview(messages)


def call_gemini_pro_vision(messages, objective):
    """
    Get the next action for Self-Operating Computer using Gemini Pro Vision
    """
    if config.verbose:
        print(
            "[Self Operating Computer][call_gemini_pro_vision]",
        )
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
        prompt = get_system_prompt("gemini-pro-vision", objective)

        model = config.initialize_google()
        if config.verbose:
            print("[call_gemini_pro_vision] model", model)

        response = model.generate_content([prompt, Image.open(screenshot_filename)])

        content = response.text[1:]
        if config.verbose:
            print("[call_gemini_pro_vision] response", response)
            print("[call_gemini_pro_vision] content", content)

        content = json.loads(content)
        if config.verbose:
            print(
                "[get_next_action][call_gemini_pro_vision] content",
                content,
            )

        return content

    except Exception as e:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA}[Operate] That did not work. Trying another method {ANSI_RESET}"
        )
        if config.verbose:
            print("[Self-Operating Computer][Operate] error", e)
            traceback.print_exc()
        return call_gpt_4_vision_preview(messages)


async def call_gpt_4_vision_preview_ocr(messages, objective, model):
    if config.verbose:
        print("[call_gpt_4_vision_preview_ocr]")

    # Construct the path to the file within the package
    try:
        time.sleep(1)
        client = config.initialize_openai()

        confirm_system_prompt(messages, objective, model)
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
            temperature=0.7,
            max_tokens=3000,
        )

        content = response.choices[0].message.content

        content = clean_json(content)

        # used later for the messages
        content_str = content

        content = json.loads(content)

        processed_content = []

        for operation in content:
            if operation.get("operation") == "click":
                text_to_click = operation.get("text")
                if config.verbose:
                    print(
                        "[call_gpt_4_vision_preview_ocr][click] text_to_click",
                        text_to_click,
                    )
                # Initialize EasyOCR Reader
                reader = easyocr.Reader(["en"])

                # Read the screenshot
                result = reader.readtext(screenshot_filename)

                text_element_index = get_text_element(
                    result, text_to_click, screenshot_filename
                )
                coordinates = get_text_coordinates(
                    result, text_element_index, screenshot_filename
                )

                # add `coordinates`` to `content`
                operation["x"] = coordinates["x"]
                operation["y"] = coordinates["y"]

                if config.verbose:
                    print(
                        "[call_gpt_4_vision_preview_ocr][click] text_element_index",
                        text_element_index,
                    )
                    print(
                        "[call_gpt_4_vision_preview_ocr][click] coordinates",
                        coordinates,
                    )
                    print(
                        "[call_gpt_4_vision_preview_ocr][click] final operation",
                        operation,
                    )
                processed_content.append(operation)

            else:
                processed_content.append(operation)

        # wait to append the assistant message so that if the `processed_content` step fails we don't append a message and mess up message history
        assistant_message = {"role": "assistant", "content": content_str}
        messages.append(assistant_message)

        return processed_content

    except Exception as e:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA}[{model}] That did not work. Trying another method {ANSI_RESET}"
        )
        if config.verbose:
            print("[Self-Operating Computer][Operate] error", e)
            traceback.print_exc()
        return gpt_4_fallback(messages, objective, model)


async def call_gpt_4_vision_preview_labeled(messages, objective, model):
    time.sleep(1)

    try:
        client = config.initialize_openai()

        confirm_system_prompt(messages, objective, model)
        file_path = pkg_resources.resource_filename("operate.models.weights", "best.pt")
        yolo_model = YOLO(file_path)  # Load your trained model
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

        if config.verbose:
            print(
                "[call_gpt_4_vision_preview_labeled] user_prompt",
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
            max_tokens=3000,
        )

        content = response.choices[0].message.content

        content = clean_json(content)

        assistant_message = {"role": "assistant", "content": content}

        messages.append(assistant_message)

        content = json.loads(content)
        if config.verbose:
            print(
                "[call_gpt_4_vision_preview_labeled] content",
                content,
            )

        processed_content = []

        for operation in content:
            print(
                "[call_gpt_4_vision_preview_labeled] for operation in content",
                operation,
            )
            if operation.get("operation") == "click":
                label = operation.get("label")
                if config.verbose:
                    print(
                        "[Self Operating Computer][call_gpt_4_vision_preview_labeled] label",
                        label,
                    )

                coordinates = get_label_coordinates(label, label_coordinates)
                if config.verbose:
                    print(
                        "[Self Operating Computer][call_gpt_4_vision_preview_labeled] coordinates",
                        coordinates,
                    )
                image = Image.open(
                    io.BytesIO(base64.b64decode(img_base64))
                )  # Load the image to get its size
                image_size = image.size  # Get the size of the image (width, height)
                click_position_percent = get_click_position_in_percent(
                    coordinates, image_size
                )
                if config.verbose:
                    print(
                        "[Self Operating Computer][call_gpt_4_vision_preview_labeled] click_position_percent",
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
                if config.verbose:
                    print(
                        "[Self Operating Computer][call_gpt_4_vision_preview_labeled] new click operation",
                        operation,
                    )
                processed_content.append(operation)
            else:
                if config.verbose:
                    print(
                        "[Self Operating Computer][call_gpt_4_vision_preview_labeled] .append none click operation",
                        operation,
                    )

                processed_content.append(operation)

            if config.verbose:
                print(
                    "[Self Operating Computer][call_gpt_4_vision_preview_labeled] new processed_content",
                    processed_content,
                )
            return processed_content

    except Exception as e:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA}[{model}] That did not work. Trying another method {ANSI_RESET}"
        )
        if config.verbose:
            print("[Self-Operating Computer][Operate] error", e)
            traceback.print_exc()
        return call_gpt_4_vision_preview(messages)


def call_ollama_llava(messages):
    if config.verbose:
        print("[call_ollama_llava]")
    time.sleep(1)
    try:
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")
        # Call the function to capture the screen with the cursor
        capture_screen_with_cursor(screenshot_filename)

        if len(messages) == 1:
            user_prompt = get_user_first_message_prompt()
        else:
            user_prompt = get_user_prompt()

        if config.verbose:
            print(
                "[call_ollama_llava] user_prompt",
                user_prompt,
            )

        vision_message = {
            "role": "user",
            "content": user_prompt,
            "images": [screenshot_filename],
        }
        messages.append(vision_message)

        response = ollama.chat(
            model="llava",
            messages=messages,
        )

        # Important: Remove the image path from the message history.
        # Ollama will attempt to load each image reference and will
        # eventually timeout.
        messages[-1]["images"] = None

        content = response["message"]["content"].strip()

        content = clean_json(content)

        assistant_message = {"role": "assistant", "content": content}
        if config.verbose:
            print(
                "[call_ollama_llava] content",
                content,
            )
        content = json.loads(content)

        messages.append(assistant_message)

        return content

    except ollama.ResponseError as e:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Operate] Couldn't connect to Ollama. With Ollama installed, run `ollama pull llava` then `ollama serve`{ANSI_RESET}",
            e,
        )

    except Exception as e:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA}[llava] That did not work. Trying again {ANSI_RESET}",
            e,
        )
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] AI response was {ANSI_RESET}",
            content,
        )
        if config.verbose:
            traceback.print_exc()
        return call_ollama_llava(messages)


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


def gpt_4_fallback(messages, objective, model):
    if config.verbose:
        print("[gpt_4_fallback]")
    system_prompt = get_system_prompt("gpt-4-vision-preview", objective)
    new_system_message = {"role": "system", "content": system_prompt}
    # remove and replace the first message in `messages` with `new_system_message`

    messages[0] = new_system_message

    if config.verbose:
        print("[gpt_4_fallback][updated]")
        print("[gpt_4_fallback][updated] len(messages)", len(messages))

    return call_gpt_4_vision_preview(messages)


def confirm_system_prompt(messages, objective, model):
    """
    On `Exception` we default to `call_gpt_4_vision_preview` so we have this function to reassign system prompt in case of a previous failure
    """
    if config.verbose:
        print("[confirm_system_prompt] model", model)

    system_prompt = get_system_prompt(model, objective)
    new_system_message = {"role": "system", "content": system_prompt}
    # remove and replace the first message in `messages` with `new_system_message`

    messages[0] = new_system_message

    if config.verbose:
        print("[confirm_system_prompt]")
        print("[confirm_system_prompt] len(messages)", len(messages))
        for m in messages:
            if m["role"] != "user":
                print("--------------------[message]--------------------")
                print("[confirm_system_prompt][message] role", m["role"])
                print("[confirm_system_prompt][message] content", m["content"])
                print("------------------[end message]------------------")


def clean_json(content):
    if config.verbose:
        print("\n\n[clean_json] content before cleaning", content)
    if content.startswith("```json"):
        content = content[
            len("```json") :
        ].strip()  # Remove starting ```json and trim whitespace
    elif content.startswith("```"):
        content = content[
            len("```") :
        ].strip()  # Remove starting ``` and trim whitespace
    if content.endswith("```"):
        content = content[
            : -len("```")
        ].strip()  # Remove ending ``` and trim whitespace

    # Normalize line breaks and remove any unwanted characters
    content = "\n".join(line.strip() for line in content.splitlines())

    if config.verbose:
        print("\n\n[clean_json] content after cleaning", content)

    return content
