import time

from operate.config import Config
from operate.utils.operating_system import OperatingSystem
from operate.utils.style import (
    ANSI_BLUE,
    ANSI_BRIGHT_MAGENTA,
    ANSI_GREEN,
    ANSI_RED,
    ANSI_RESET,
)

# Load configuration
config = Config()
operating_system = OperatingSystem()

VERBOSE = config.verbose


def operate(operations):
    if VERBOSE:
        print("[Self Operating Computer][operate]")
    for operation in operations:
        if VERBOSE:
            print("[Self Operating Computer][operate] operation", operation)
        # wait one second
        time.sleep(1)
        operate_type = operation.get("operation").lower()
        operate_thought = operation.get("thought")
        operate_detail = ""
        if VERBOSE:
            print("[Self Operating Computer][operate] operate_type", operate_type)

        if operate_type == "press" or operate_type == "hotkey":
            keys = operation.get("keys")
            operate_detail = keys
            operating_system.press(keys)
        elif operate_type == "write":
            content = operation.get("content")
            operate_detail = content
            operating_system.write(content)
        elif operate_type == "click":
            x = operation.get("x")
            y = operation.get("y")
            click_detail = {"x": x, "y": y}
            operate_detail = click_detail

            operating_system.mouse(click_detail)
        elif operate_type == "done":
            summary = operation.get("summary")

            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BLUE} Objective Completed {ANSI_RESET}"
            )
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BLUE} Summary {ANSI_RESET}{summary}"
            )
            return True

        else:
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] unknown operation response :({ANSI_RESET}"
            )
            print(
                f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_RED}[Error] AI response {ANSI_RESET}{operation}"
            )
            return True

        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA}[Operate] Thought {ANSI_RESET} {operate_thought}"
        )
        print(
            f"{ANSI_GREEN}[Self-Operating Computer]{ANSI_BRIGHT_MAGENTA}[Operate] {operate_type} {ANSI_RESET} {operate_detail}"
        )

    return False
