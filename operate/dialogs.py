import platform
import os 

from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import message_dialog
from operate.styling import style, ANSI_GREEN, ANSI_BRIGHT_GREEN, ANSI_RESET, ANSI_BLUE, ANSI_YELLOW, ANSI_RED, ANSI_BRIGHT_MAGENTA
from operate.utils import get_next_action, get_last_assistant_message, parse_oai_response,summarize
from operate.exceptions import ModelNotRecognizedException
from operate.actions import search, keyboard_type, mouse_click
from operate.prompt_template import USER_QUESTION

DEBUG = False

def main(model):
    """
    Main function for the Self-Operating Computer
    """

    message_dialog(
        title="Self-Operating Computer",
        text="Ask a computer to do anything.",
        style=style,
    ).run()

    print("SYSTEM", platform.system())

    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


    print(f"{ANSI_GREEN}[Self-Operating Computer]\n{ANSI_RESET}{USER_QUESTION}")
    print(f"{ANSI_YELLOW}[User]{ANSI_RESET}")

    objective = prompt(
        style=style,
    )

    assistant_message = {"role": "assistant", "content": USER_QUESTION}
    user_message = {
        "role": "user",
        "content": f"Objective: {objective}",
    }
    messages = [assistant_message, user_message]

    loop_count = 0

    while True:
        if DEBUG:
            print("[loop] messages before next action:\n\n\n", messages[1:])
        try:
            response = get_next_action(model, messages, objective)
            action = parse_oai_response(response)
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
            summary = summarize(messages, objective)
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
            function_response = mouse_click(action_detail)
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
        if loop_count > 10:
            break
