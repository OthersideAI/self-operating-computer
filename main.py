import os
import time
import sys
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import message_dialog, button_dialog
from prompt_toolkit.styles import Style as PromptStyle
from prompt_toolkit.shortcuts import button_dialog
from colorama import Fore, Style as ColoramaStyle


# Define style
style = PromptStyle.from_dict({
    'dialog': 'bg:#88ff88',
    'button': 'bg:#ffffff #000000',
    'dialog.body': 'bg:#44cc44 #ffffff',
    'dialog shadow': 'bg:#003800',
})

def main():
    message_dialog(
        title='Self Driving Computer',
        text='Ask a computer to do anything.',
        style=style
    ).run()

    os.system('clear')  # Clears the terminal screen

    bot_1_name = prompt('What would you like the computer to do? ')

    bot_1_system_prompt = { "role": "system", "content": f"You are a self driving computer that can do anything."}

    os.system('clear')  # Clears the terminal screen


if __name__ == "__main__":
    main()