import base64
import json
import os
import re
import time
import typing

from openai import OpenAI
from app.config import settings
from app.lib import prompts
from app.lib.exceptions import ModelNotRecognizedException
from app.lib.actions import KeyboardAction, MouseAction, ScreenshotAction, SearchAction
from app.lib.prompts import Prompt
from app.lib.terminal import Terminal
from app.lib.util import ImageUtil


class ModelMessage(object):
    """Provides a consistent message format for the OpenAI API"""
    ROLE_ASSISTANT = "assistant"
    ROLE_USER = "user"

    role: str
    content: typing.Any

    def __init__(self, role: str, content: typing.Any):
        self.role = role
        self.content = content

    def __str__(self):
        return f'[{self.role}] {self.content}'

    def __repr__(self):
        return self.__str__()


class ModelResponse(object):
    """Provides a consistent response format for the OpenAI API"""
    ACTION_CLICK = "CLICK"
    ACTION_DONE = "DONE"
    ACTION_SEARCH = "SEARCH"
    ACTION_TYPE = "TYPE"
    ACTION_UNKNOWN = "UNKNOWN"

    action: str
    data: re.Match or str or None

    def __init__(self, action: str, data: re.Match or None):
        self.action = action
        self.data = data

    def __str__(self):
        return f'[{self.action}] {self.data}'

    def __repr__(self):
        return self.__str__()


class OpenAIWrapper:
    _client: OpenAI
    """The OpenAI client"""

    _messages: list = []
    """The message cache of messages sent to the model."""

    _loop_count: int = 0
    """The number of times the loop has run. Used to prevent infinite loops."""

    def __init__(self, api_key: str or None = None, api_url: str or None = None):
        self._client = OpenAI(
            api_key=settings.openai_api_key if api_key is None else api_key,
            base_url=settings.openai_api_url if api_url is None else api_url
        )

    def execute_objective(self, objective: str):
        """Process the objective by sending and processing messages to and from the model"""

        self.create_message(ModelMessage.ROLE_ASSISTANT, prompts.USER_QUESTION)
        self.create_message(ModelMessage.ROLE_USER, f'Objective: {objective}')

        while True:
            if settings.debug:
                Terminal.print_message('[loop] messages before next action:', self._messages[1:])

            try:
                response = self.get_next_action(objective)
                model_response: ModelResponse = self.parse_oai_response(response)

            except ModelNotRecognizedException as e:
                Terminal.print_error(str(e))
                break
            except Exception as e:
                Terminal.print_error(str(e))
                break

            if model_response.action == ModelResponse.ACTION_DONE:
                Terminal.print_message('Objective Complete!')
                Terminal.print_message('Summary:', self.summarize(objective))
                break

            if model_response.action != ModelResponse.ACTION_UNKNOWN:
                Terminal.print_action(model_response.action, model_response.data)

            function_response: str = ''
            if model_response.action == ModelResponse.ACTION_SEARCH:
                function_response = SearchAction.search(model_response.data)
            elif model_response.action == ModelResponse.ACTION_TYPE:
                function_response = KeyboardAction.type(model_response.data)
            elif model_response.action == ModelResponse.ACTION_CLICK:
                function_response = MouseAction.click(model_response.data)
            else:
                Terminal.print_error('Something went wrong!')
                Terminal.print_error('AI Response:', response)
                break

            Terminal.print_action(f'{model_response.action} COMPLETE', function_response)

            self.create_message(ModelMessage.ROLE_ASSISTANT, function_response)

            self._loop_count += 1
            if self._loop_count > 15:
                break

    def create_message(self, role: str, content: typing.Any, append: bool = True) -> ModelMessage:
        """Creates a new message to send to the model and caches it in the messages array"""
        message: ModelMessage = ModelMessage(role, content)
        if append:
            self._messages.append(message)
        return message

    def get_messages_as_objects(self) -> list[dict]:
        """Returns the messages array as a list of objects"""
        return [message.__dict__ for message in self._messages]

    def get_next_action(self, objective):
        if settings.openai_model == "gpt-4-vision-preview":
            return self.get_next_action_from_openai(objective)
        elif settings.openai_model == "agent-1":
            return "coming soon"

        raise ModelNotRecognizedException(settings.openai_model)

    def get_next_action_from_openai(self, objective):
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
            ScreenshotAction.capture_screen_with_cursor(screenshot_filename)

            new_screenshot_filename = os.path.join("screenshots", "screenshot_with_grid.png")

            ImageUtil.add_grid_to_image(screenshot_filename, new_screenshot_filename, 500)

            # sleep for a second
            time.sleep(1)

            with open(new_screenshot_filename, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

            previous_action = self.get_last_assistant_message()

            vision_prompt = Prompt.format_vision_prompt(objective, previous_action)

            vision_message: ModelMessage = self.create_message(ModelMessage.ROLE_USER, [
                {"type": "text", "text": vision_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                },
            ], append=False)

            # create a copy of messages and save to pseudo_messages
            pseudo_messages = self.get_messages_as_objects().copy()
            pseudo_messages.append(vision_message.__dict__)

            response = self._client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=pseudo_messages,
                presence_penalty=1,
                frequency_penalty=1,
                temperature=0.7,
                max_tokens=300,
            )

            self.create_message(ModelMessage.ROLE_USER, '`screenshot.png`')

            content = response.choices[0].message.content

            if settings.accurate_mode:
                if content.startswith(ModelResponse.ACTION_CLICK):
                    # Adjust pseudo_messages to include the accurate_mode_message

                    click_data = re.search(r"CLICK \{ (.+) \}", content).group(1)
                    click_data_json = json.loads(f"{{{click_data}}}")
                    prev_x = click_data_json["x"]
                    prev_y = click_data_json["y"]

                    if settings.debug:
                        print(f"Previous coords before accurate tuning: prev_x {prev_x} prev_y {prev_y}")

                    content = self.accurate_mode_double_check(pseudo_messages, prev_x, prev_y)
                    assert content != "ERROR", "ERROR: accurate_mode_double_check failed"

            return content

        except Exception as e:
            Terminal.print_error('Error parsing JSON:', str(e))
            return "Failed take action after looking at the screenshot"

    def accurate_mode_double_check(self, pseudo_messages, prev_x, prev_y):
        """
        Re-prompt OAI with additional screenshot of a mini screenshot centered around the cursor
        for further fine-tuning of clicked location
        """
        try:
            screenshot_filename = os.path.join("screenshots", "screenshot_mini.png")
            ScreenshotAction.capture_mini_screenshot_with_cursor(
                file_path=screenshot_filename, x=prev_x, y=prev_y
            )

            new_screenshot_filename = os.path.join(
                "screenshots", "screenshot_mini_with_grid.png"
            )

            with open(new_screenshot_filename, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

            accurate_vision_prompt = Prompt.format_accurate_mode_vision_prompt(prev_x, prev_y)

            accurate_mode_message: ModelMessage = self.create_message(ModelMessage.ROLE_USER, [
                {"type": "text", "text": accurate_vision_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                },
            ], append=False)

            pseudo_messages.append(accurate_mode_message.__dict__)

            response = self._client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=pseudo_messages,
                presence_penalty=1,
                frequency_penalty=1,
                temperature=0.7,
                max_tokens=300,
            )

            content = response.choices[0].message.content

            return content
        except Exception as e:
            Terminal.print_error('Error re-prompting model for accurate_mode:', str(e))
            return "ERROR"

    def get_last_assistant_message(self):
        """
        Retrieve the last message from the assistant in the messages array.
        If the last assistant message is the first message in the array, return None.
        """
        for index in reversed(range(len(self._messages))):
            if self._messages[index].role == ModelMessage.ROLE_ASSISTANT:
                if index == 0:  # Check if the assistant message is the first in the array
                    return None
                else:
                    return self._messages[index]
        return None  # Return None if no assistant message is found

    def summarize(self, objective):
        try:
            screenshots_dir = "screenshots"

            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)

            screenshot_filename = os.path.join(screenshots_dir, "summary_screenshot.png")

            # Call the function to capture the screen with the cursor
            ScreenshotAction.capture_screen_with_cursor(screenshot_filename)

            with open(screenshot_filename, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

            summary_prompt = Prompt.format_summary_prompt(objective)

            self.create_message(ModelMessage.ROLE_USER, [
                {"type": "text", "text": summary_prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                },
            ], append=False)

            response = self._client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=self.get_messages_as_objects(),
                max_tokens=500,
            )

            content = response.choices[0].message.content
            return content

        except Exception as e:
            Terminal.print_error('Error with summarizing:', str(e))
            return "Failed to summarize the workflow"

    def parse_oai_response(self, response) -> ModelResponse:
        action: str = ModelResponse.ACTION_UNKNOWN
        data: re.Match or str or None = response

        if response == ModelResponse.ACTION_DONE:
            action = ModelResponse.ACTION_DONE
            data = None
        elif response.startswith(ModelResponse.ACTION_CLICK):
            # Adjust the regex to match the correct format
            click_data = re.search(r"CLICK \{ (.+) \}", response).group(1)
            action = ModelResponse.ACTION_CLICK
            data = json.loads(f"{{{click_data}}}")

        elif response.startswith(ModelResponse.ACTION_TYPE):
            # Extract the text to type
            action = ModelResponse.ACTION_TYPE
            data = re.search(r'TYPE "(.+)"', response, re.DOTALL).group(1)

        elif response.startswith(ModelResponse.ACTION_SEARCH):
            # Extract the search query
            action = ModelResponse.ACTION_SEARCH
            data = re.search(r'SEARCH "(.+)"', response).group(1)

        return ModelResponse(action, data)
