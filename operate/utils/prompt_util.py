from prompt_toolkit.styles import Style as PromptStyle
from operate.prompts.prompt import (
    VISION_PROMPT,
    ACCURATE_PIXEL_COUNT,
    ACCURATE_MODE_VISION_PROMPT,
    SUMMARY_PROMPT,
)
from operate.config.settings import Config

# Load settings
config = Config()
monitor_size = config.monitor_size

# Define style
style = PromptStyle.from_dict(
    {
        "dialog": "bg:#88ff88",
        "button": "bg:#ffffff #000000",
        "dialog.body": "bg:#44cc44 #ffffff",
        "dialog shadow": "bg:#003800",
    }
)


def format_summary_prompt(objective):
    """
    Format the summary prompt
    """
    prompt = SUMMARY_PROMPT.format(objective=objective)
    return prompt


def format_vision_prompt(objective, previous_action):
    """
    Format the vision prompt
    """
    if previous_action:
        previous_action = f"Here was the previous action you took: {previous_action}"
    else:
        previous_action = ""
    prompt = VISION_PROMPT.format(objective=objective, previous_action=previous_action)
    return prompt


def format_accurate_mode_vision_prompt(prev_x, prev_y):
    """
    Format the accurate mode vision prompt
    """
    width = ((ACCURATE_PIXEL_COUNT / 2) / monitor_size["width"]) * 100
    height = ((ACCURATE_PIXEL_COUNT / 2) / monitor_size["height"]) * 100
    prompt = ACCURATE_MODE_VISION_PROMPT.format(
        prev_x=prev_x, prev_y=prev_y, width=width, height=height
    )
    return prompt
