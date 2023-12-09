import sys
import os
import subprocess
import platform
import base64
import openai

from dotenv import load_dotenv

SUMMARY_SCREENSHOT_PATH = os.path.join('screenshots', 'summary_screenshot.png')

EVALUATION_PROMPT = """
Your job is to look at the given screenshot and determine if the following guideline is met in the image.
You can only respond in one of two possible ways: 'TRUE' or 'FALSE' with those exact spellings.
Respond TRUE or FALSE based on whether or not the given guideline is met.

Guideline: {guideline}
"""

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
    
    
def format_evaluation_prompt(guideline):
    prompt = EVALUATION_PROMPT.format(guideline=guideline)
    return prompt


def parse_eval_content(content):
    if content == "TRUE":
        return True
    elif content == "FALSE":
        return False
    else:
        print("The model gave a bad evaluation response and it couldn't be parsed. Exiting...")
        exit(1)


def evaluate_summary_screenshot(guideline):
    '''Load the summary screenshot and return True or False if it meets the given guideline.'''
    with open(SUMMARY_SCREENSHOT_PATH, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        eval_message = [{
            "role": "user",
            "content": [
                {"type": "text", "text": format_evaluation_prompt(guideline)},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                },
            ],
        }]
        
        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=eval_message,
            presence_penalty=1,
            frequency_penalty=1,
            temperature=0.7,
            max_tokens=300,
        )

        eval_content = response.choices[0].message.content
        
        return parse_eval_content(eval_content)


def run_test_case(objective, guideline):
    '''Returns True if the result of the test with the given prompt meets the given guideline.'''
    # Run `operate` with the test case prompt
    subprocess.run(['operate', '--prompt', f'"{objective}"'], stdout=subprocess.DEVNULL)
    
    try:
        result = evaluate_summary_screenshot(guideline)
    except(OSError):
        print("Couldn't open the summary screenshot")
        return False
    
    return result


def main():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Define the test cases and the guidelines
    test_cases = {
        "Go to Google.com": "The Google home page is visible with the search bar.",
        "Open YouTube and play holiday music": "The YouTube video player is loaded and actively playing holiday music.",
        "Open Google Docs and write a poem": "A Google Doc file is opened in the browser with a poem typed into it.",
    }
    
    print(f"{ANSI_BRIGHT_MAGENTA}[STARTING EVALUATION]{ANSI_RESET} NOTE: `operate` output is silenced.")

    for objective, guideline in test_cases.items():
        print(f"{ANSI_BLUE}[EVALUATING]{ANSI_RESET} '{objective}'")
        
        result = run_test_case(objective, guideline)
        if result:
            print(f"{ANSI_GREEN}[PASSED]{ANSI_RESET} '{objective}'")
        else:
            print(f"{ANSI_RED}[FAILED]{ANSI_RESET} '{objective}'")


if __name__ == "__main__":
    main()
