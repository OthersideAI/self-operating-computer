import tkinter as tk
from typing import Callable, List

from automation import ActionLooper, AutomationEngine
from config import load_config
from engine_llm import LLMEngine, LLMError, parse_action_text
from gui import AppGUI


class AppController:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.logger: Callable[[str], None] = lambda msg: None
        self.config = load_config()
        self.automation = AutomationEngine(
            dry_run=bool(self.config.get("dry_run", True)),
            stop_hotkey=str(self.config.get("stop_hotkey", "ctrl+alt+s")),
        )
        self.gui = AppGUI(root, self.run_tasks, self.stop, self.export_logger)

    def export_logger(self, logger: Callable[[str], None]) -> None:
        self.logger = logger

    def log(self, message: str) -> None:
        self.logger(message)

    def stop(self) -> None:
        self.automation.stop()
        self.log("Stop signal sent.")

    def run_tasks(self, tasks: List[str]) -> None:
        for index, objective in enumerate(tasks, start=1):
            self.config = load_config()
            self.automation.dry_run = bool(self.config.get("dry_run", True))
            self.automation.stop_hotkey = str(self.config.get("stop_hotkey", "ctrl+alt+s"))
            llm = LLMEngine(self.config)
            looper = ActionLooper(
                automation=self.automation,
                request_action=llm.request_action,
                parse_action=parse_action_text,
                max_steps=int(self.config.get("max_steps", 10)),
                delay_seconds=float(self.config.get("delay_seconds", 0.6)),
                log_callback=self.log,
            )
            self.log(f"Running task {index}/{len(tasks)}: {objective}")
            try:
                outcome = looper.run(objective)
            except LLMError as exc:
                self.log(f"LLM error: {exc}")
                break
            except Exception as exc:  # pylint: disable=broad-except
                self.log(f"Unexpected error: {exc}")
                break
            self.log(f"Task result: {outcome}")
            if self.automation.should_stop():
                self.log("Stopped before finishing all tasks.")
                break


def main() -> None:
    root = tk.Tk()
    AppController(root)
    root.mainloop()


if __name__ == "__main__":
    main()
