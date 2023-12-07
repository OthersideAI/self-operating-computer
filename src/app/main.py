"""
Self-Operating Computer
"""
import sys
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.styles import Style as PromptStyle
from app.config import settings
from app.lib import prompts
from app.lib import terminal
from app.lib.openai import OpenAIWrapper
from app.lib.terminal import Terminal

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
    """Main function for the Self-Operating Computer"""
    oai: OpenAIWrapper = OpenAIWrapper()
    mic = None

    # Initialize WhisperMic if voice mode enabled
    if settings.voice_mode:
        try:
            from whisper_mic import WhisperMic

            # Initialize WhisperMic if import is successful
            mic = WhisperMic()
        except ImportError:
            Terminal.print_error('Missing Dependency', "Voice mode requires the 'whisper_mic' module. "
                                 + "Please install it using 'pip install -r requirements-audio.txt'")
            sys.exit(1)

    # Display an intro prompt
    message_dialog(
        title="Self-Operating Computer",
        text="Ask a computer to do anything.",
        style=style,
    ).run()

    # Clear the console
    terminal.clear_console()

    if settings.voice_mode:
        Terminal.print_message(None, 'Listening for your command... (speak now)')
        try:
            objective = mic.listen()
        except Exception as e:
            Terminal.print_error('Error in capturing voice input', str(e))
            return  # Exit if voice input fails
    else:
        Terminal.print_message(None, prompts.USER_QUESTION)
        Terminal.print('[User]', None, terminal.ANSI_YELLOW, False)
        objective = prompt(style=style)

    oai.execute_objective(objective)
