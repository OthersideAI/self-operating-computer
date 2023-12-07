import os
from app.lib import checks

if checks.ansi_support():
    # Standard green text
    ANSI_GREEN = "\033[32m"
    # Bright/bold green text
    ANSI_BRIGHT_GREEN = "\033[92m"
    # Reset to default text color
    ANSI_RESET = "\033[0m"
    # ANSI escape code for blue text
    ANSI_BLUE = "\033[94m"  # This is for bright blue

    # Standard yellow text
    ANSI_YELLOW = "\033[33m"

    ANSI_RED = "\033[31m"

    # Bright magenta text
    ANSI_BRIGHT_MAGENTA = "\033[95m"
else:
    ANSI_GREEN = ""
    ANSI_BRIGHT_GREEN = ""
    ANSI_RESET = ""
    ANSI_BLUE = ""
    ANSI_YELLOW = ""
    ANSI_RED = ""
    ANSI_BRIGHT_MAGENTA = ""


class Terminal:
    """Terminal class for handling console output"""

    @staticmethod
    def print(title: str or None, content: str or None = None, color: str = ANSI_BLUE, prefix: bool = True):
        """Print a formatted message"""
        message: str = ''

        if prefix:
            message += f'{ANSI_GREEN}[Self-Operating Computer]'

        message += color

        if title is not None:
            if prefix:
                message += ' '
            message += title

        if content is not None:
            message += f'\n{ANSI_RESET}{content}'
        else:
            message += ANSI_RESET

        print(message)

    @staticmethod
    def print_action(title: str or None, content: str or None = None):
        """Print a formatted error message"""
        Terminal.print(f'[Act] {title}', content, ANSI_BRIGHT_MAGENTA)

    @staticmethod
    def print_error(title: str or None, content: str or None = None):
        """Print a formatted error message"""
        Terminal.print(f'[Error] {title}', content, ANSI_RED)

    @staticmethod
    def print_message(title: str or None, content: str or None = None):
        """Print a formatted message"""
        Terminal.print(title, content)

    @staticmethod
    def clear_console():
        # Clear the console
        if checks.PLATFORM_WINDOWS:
            os.system('cls')
        else:
            print("\033c", end="")


def clear_console():
    # Clear the console
    if checks.PLATFORM_WINDOWS:
        os.system('cls')
    else:
        print("\033c", end="")
