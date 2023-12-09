import sys
import os
import subprocess
import platform
import openai

from dotenv import load_dotenv

# Check if on a windows terminal that supports ANSI escape codes
def supports_ansi():
    """
    Check if the terminal supports ANSI escape codes
    """
    plat = platform.system()
    supported_platform = plat != "Windows" or "ANSICON" in os.environ
    is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    return supported_platform and is_a_tty

if supports_ansi():
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


def run_test_case(prompt, guideline):
    '''Returns True if the result of the test with the given prompt meets the given guideline.'''
    # Run main.py with the test case prompt
    subprocess.run(['operate', '--prompt', f'"{prompt}"'])
    
    return True


def main():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Define the test cases and the guidelines
    test_cases = {
        "Open YouTube and play holiday music": "The YouTube video player is loaded and actively playing holiday music.",
        "Open Google Docs and write a poem": "A Google Doc file is opened in the browser with a poem typed into it.",
    }

    for prompt, guideline in test_cases.items():
        print(f"{ANSI_BLUE}[EVALUATING]{ANSI_RESET} Test case '{prompt}'")
        
        result = run_test_case(prompt, guideline)
        if result:
            print(f"{ANSI_GREEN}[PASSED]{ANSI_RESET} Test case '{prompt}'")
        else:
            print(f"{ANSI_RED}[FAILED]{ANSI_RESET} Test case '{prompt}'")


if __name__ == "__main__":
    main()
