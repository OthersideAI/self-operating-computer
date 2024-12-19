import sys
import os
import subprocess
import platform
import base64
import json
import openai
import argparse

from dotenv import load_dotenv

# "Objective for `operate`" : "Guideline for passing this test case given to GPT-4v"
TEST_CASES = {
    "Go to Github.com": "A Github page is visible.",
    "Go to Youtube.com and play a video": "The YouTube video player is visible.",
}

EVALUATION_PROMPT = """
Your job is to look at the given screenshot and determine if the following guideline is met in the image.
You must respond in the following format ONLY. Do not add anything else:
{{ "guideline_met": (true|false), "reason": "Explanation for why guideline was or wasn't met" }}
guideline_met must be set to a JSON boolean. True if the image meets the given guideline.
reason must be a string containing a justification for your decision.

Guideline: {guideline}
"""

SCREENSHOT_PATH = os.path.join("screenshots", "screenshot.png")


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
    try:
        res = json.loads(content)

        print(res["reason"])

        return res["guideline_met"]
    except:
        print(
            "The model gave a bad evaluation response and it couldn't be parsed. Exiting..."
        )
        exit(1)


def evaluate_final_screenshot(guideline):
    """Load the final screenshot and return True or False if it meets the given guideline."""
    with open(SCREENSHOT_PATH, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        eval_message = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": format_evaluation_prompt(guideline)},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                    },
                ],
            }
        ]

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=eval_message,
            presence_penalty=1,
            frequency_penalty=1,
            temperature=0.7,
        )

        eval_content = response.choices[0].message.content

        return parse_eval_content(eval_content)


def run_test_case(objective, guideline, model):
    """Returns True if the result of the test with the given prompt meets the given guideline for the given model."""
    # Run `operate` with the model to evaluate and the test case prompt
    subprocess.run(
        ["operate", "-m", model, "--prompt", f'"{objective}"'],
        stdout=subprocess.DEVNULL,
    )

    try:
        result = evaluate_final_screenshot(guideline)
    except OSError:
        print("[Error] Couldn't open the screenshot for evaluation")
        return False

    return result


def get_test_model():
    parser = argparse.ArgumentParser(
        description="Run the self-operating-computer with a specified model."
    )

    parser.add_argument(
        "-m",
        "--model",
        help="Specify the model to evaluate.",
        required=False,
        default="gpt-4-with-ocr",
    )

    return parser.parse_args().model


def main():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    model = get_test_model()

    print(f"{ANSI_BLUE}[EVALUATING MODEL `{model}`]{ANSI_RESET}")
    print(f"{ANSI_BRIGHT_MAGENTA}[STARTING EVALUATION]{ANSI_RESET}")

    passed = 0
    failed = 0
    for objective, guideline in TEST_CASES.items():
        print(f"{ANSI_BLUE}[EVALUATING]{ANSI_RESET} '{objective}'")

        result = run_test_case(objective, guideline, model)
        if result:
            print(f"{ANSI_GREEN}[PASSED]{ANSI_RESET} '{objective}'")
            passed += 1
        else:
            print(f"{ANSI_RED}[FAILED]{ANSI_RESET} '{objective}'")
            failed += 1

    print(
        f"{ANSI_BRIGHT_MAGENTA}[EVALUATION COMPLETE]{ANSI_RESET} {passed} test{'' if passed == 1 else 's'} passed, {failed} test{'' if failed == 1 else 's'} failed"
    )


if __name__ == "__main__":
    main()
