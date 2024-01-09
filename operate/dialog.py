import sys
import os
import platform
import asyncio
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit import prompt
from operate.exceptions import ModelNotRecognizedException
from operate.prompts import USER_QUESTION
from operate.settings import Config
from operate.utils.style import (
    ANSI_GREEN,
    ANSI_RESET,
    ANSI_BLUE,
    ANSI_YELLOW,
    ANSI_RED,
    ANSI_BRIGHT_MAGENTA,
    style,
)
from operate.utils.os import (
    keyboard_type,
    search,
    click,
)
from operate.actions import get_next_action, summarize
from operate.utils.misc import parse_response

# Load configuration
config = Config()


def main(model, terminal_prompt, voice_mode=False):
    """
    Main function for the Self-Operating Computer.

    Parameters:
    - model: The model used for generating responses.
    - terminal_prompt: A string representing the prompt provided in the terminal.
    - voice_mode: A boolean indicating whether to enable voice mode.

    Returns:
    None
    """
    mic = None
    # Initialize `WhisperMic`, if `voice_mode` is True

    validation(model, voice_mode)

    if voice_mode:
        try:
            from whisper_mic import WhisperMic

            # Initialize WhisperMic if import is successful
            mic = WhisperMic()
        except ImportError:
            print(
                "Voice mode requires the 'whisper_mic' module. Please install it using 'pip install -r requirements-audio.txt'"
            )
            sys.exit(1)

    # Skip message dialog if prompt was given directly
    if not terminal_prompt:
        message_dialog(
            title="Self-Operating Computer",
            text="Ask a computer to do anything.",
            style=style,
        ).run()
    else:
        print("Running direct prompt...")

    print("SYSTEM", platform.system())
    # Clear the console
    if platform.system() == "Windows":
        os.system("cls")
    else:
        print("\033c", end="")

    if terminal_prompt:  # Skip objective prompt if it was given as an argument
        objective = terminal_prompt
    elif voice_mode:
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RESET} Listening for your command... (speak now)"
        )
        try:
            objective = mic.listen()
        except Exception as e:
            print(f"{ANSI_RED}Error in capturing voice input: {e}{ANSI_RESET}")
            return  # Exit if voice input fails
    else:
        print(f"{ANSI_GREEN}[Self-Operating Computer]\n{ANSI_RESET}{USER_QUESTION}")
        print(f"{ANSI_YELLOW}[User]{ANSI_RESET}")
        objective = prompt(style=style)

    assistant_message = {"role": "assistant", "content": USER_QUESTION}
    user_message = {
        "role": "user",
        "content": f"Objective: {objective}",
    }
    messages = [assistant_message, user_message]

    loop_count = 0

    session_id = None

    while True:
        if config.debug:
            print("[loop] messages before next action:\n\n\n", messages[1:])
        try:
            response = asyncio.run(
                get_next_action(model, messages, objective, session_id)
            )

            action = parse_response(response)
            action_type = action.get("type")
            action_detail = action.get("data")

        except ModelNotRecognizedException as e:
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] -> {e} {ANSI_RESET}"
            )
            break
        except Exception as e:
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] -> {e} {ANSI_RESET}"
            )
            break

        if action_type == "DONE":
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BLUE} Objective complete {ANSI_RESET}"
            )
            summary = summarize(model, messages, objective)
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BLUE} Summary\n{ANSI_RESET}{summary}"
            )
            break

        if action_type != "UNKNOWN":
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA} [Act] {action_type} {ANSI_RESET}{action_detail}"
            )

        function_response = ""
        if action_type == "SEARCH":
            function_response = search(action_detail)
        elif action_type == "TYPE":
            function_response = keyboard_type(action_detail)
        elif action_type == "CLICK":
            function_response = click(action_detail)
        else:
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] something went wrong :({ANSI_RESET}"
            )
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] AI response\n{ANSI_RESET}{response}"
            )
            break

        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA} [Act] {action_type} COMPLETE {ANSI_RESET}{function_response}"
        )

        message = {
            "role": "assistant",
            "content": function_response,
        }
        messages.append(message)

        loop_count += 1
        if loop_count > 15:
            break


def validation(model, voice_mode):
    """
    Validate the input parameters for the dialog operation.

    Args:
        model (str): The model to be used for the dialog operation.
        voice_mode (bool): Flag indicating whether to use voice mode.

    Raises:
        SystemExit: If the input parameters are invalid.

    """

    if voice_mode and not config.openai_api_key:
        print("To use voice mode, please add an OpenAI API key")
        sys.exit(1)

    if model == "gpt-4-vision-preview" and not config.openai_api_key:
        print("To use `gpt-4-vision-preview` add an OpenAI API key")
        sys.exit(1)

    if model == "gemini-pro-vision" and not config.google_api_key:
        print("To use `gemini-pro-vision` add a Google API key")
        sys.exit(1)
