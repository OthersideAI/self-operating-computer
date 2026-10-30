import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict, Optional

import keyboard
import pyautogui
from PIL import ImageGrab

pyautogui.FAILSAFE = False


@dataclass
class ActionResult:
    action: Dict[str, object]
    executed: bool
    error: Optional[str] = None


class AutomationEngine:
    def __init__(self, dry_run: bool = True, stop_hotkey: str = "ctrl+alt+s"):
        self.dry_run = dry_run
        self.stop_hotkey = stop_hotkey
        self._stop_flag = threading.Event()
        self._hotkey_registered = False

    def register_stop_hotkey(self) -> None:
        if self._hotkey_registered:
            return
        try:
            keyboard.add_hotkey(self.stop_hotkey, self.stop)
            self._hotkey_registered = True
        except keyboard.KeyboardException:
            # Keyboard may need elevated privileges; ignore if unavailable
            pass

    def stop(self) -> None:
        self._stop_flag.set()

    def reset_stop(self) -> None:
        self._stop_flag.clear()

    def should_stop(self) -> bool:
        return self._stop_flag.is_set()

    def capture_screenshot(self, save_path: Optional[str] = None):
        image = ImageGrab.grab()
        if save_path:
            image.save(save_path)
        return image

    def execute_action(self, action: Dict[str, object]) -> ActionResult:
        if self.dry_run:
            return ActionResult(action=action, executed=False, error=None)

        try:
            action_type = action.get("type")
            if action_type == "click":
                pyautogui.click(x=int(action["x"]), y=int(action["y"]))
            elif action_type == "type":
                pyautogui.typewrite(str(action["text"]))
            elif action_type == "hotkey":
                keys = [str(k) for k in action.get("keys", [])]
                pyautogui.hotkey(*keys)
            elif action_type == "wait":
                time.sleep(float(action.get("seconds", 0)))
            elif action_type == "done":
                # No-op
                pass
            else:
                return ActionResult(action=action, executed=False, error="Unknown action type")
            return ActionResult(action=action, executed=True, error=None)
        except Exception as exc:  # pylint: disable=broad-except
            return ActionResult(action=action, executed=False, error=str(exc))


class ActionLooper:
    def __init__(
        self,
        automation: AutomationEngine,
        request_action: Callable[[str, str], str],
        parse_action: Callable[[str], Optional[Dict[str, object]]],
        max_steps: int,
        delay_seconds: float,
        log_callback: Callable[[str], None],
    ):
        self.automation = automation
        self.request_action = request_action
        self.parse_action = parse_action
        self.max_steps = max_steps
        self.delay_seconds = delay_seconds
        self.log_callback = log_callback

    def run(self, objective: str) -> str:
        self.automation.reset_stop()
        self.automation.register_stop_hotkey()
        last_note = "Screenshot captured"
        for step in range(1, self.max_steps + 1):
            if self.automation.should_stop():
                return "Stopped by user"
            try:
                self.automation.capture_screenshot()
            except Exception as exc:  # pylint: disable=broad-except
                self.log_callback(f"Screenshot failed: {exc}")
                last_note = "screenshot failed"
            else:
                last_note = "screenshot taken"

            retries = 0
            action_data = None
            raw = ""
            while retries < 3 and action_data is None:
                raw = self.request_action(objective, last_note)
                self.log_callback(f"Raw model response: {raw}")
                action_data = self.parse_action(raw)
                if action_data is None:
                    retries += 1
                    self.log_callback("Model returned invalid JSON. Retrying...")
            if action_data is None:
                return "Failed to parse action after retries"

            result = self.automation.execute_action(action_data)
            executed_text = "executed" if result.executed else "dry-run"
            self.log_callback(f"Action step {step}: {action_data} ({executed_text})")
            if result.error:
                self.log_callback(f"Action error: {result.error}")
            if action_data.get("type") == "done":
                return str(action_data.get("reason", "Done"))

            if self.automation.should_stop():
                return "Stopped by user"
            time.sleep(self.delay_seconds)
        return "Reached max steps"
