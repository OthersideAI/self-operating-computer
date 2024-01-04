from prompt_toolkit.styles import Style as PromptStyle
from operate.prompts.prompts import (
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
