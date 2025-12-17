import json
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path(__file__).parent / "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "provider": "Ollama (Local)",
    "ollama_host": "http://localhost:11434",
    "ollama_model": "llama3.2:3b",
    "openrouter_api_key": "",
    "openrouter_model": "openrouter/auto",
    "openrouter_base_url": "https://openrouter.ai/api/v1",
    "max_steps": 10,
    "delay_seconds": 0.6,
    "stop_hotkey": "ctrl+alt+s",
    "dry_run": True,
}


def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
            merged = {**DEFAULT_CONFIG, **data}
            return merged
        except (json.JSONDecodeError, OSError):
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    try:
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except OSError:
        # Prefer silent failure over crashing the UI when filesystem is read-only
        pass
