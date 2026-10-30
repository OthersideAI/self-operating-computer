import json
from typing import Dict, List, Optional

import requests
from openai import OpenAI


class LLMError(Exception):
    """Raised when the language model call fails."""


class LLMEngine:
    def __init__(self, config: Dict[str, object]):
        self.config = config

    def _ollama_chat(self, messages: List[Dict[str, str]]) -> str:
        host = str(self.config.get("ollama_host") or "http://localhost:11434")
        model = str(self.config.get("ollama_model") or "llama3.2:3b")
        try:
            health = requests.get(f"{host}/api/tags", timeout=3)
        except requests.RequestException as exc:
            raise LLMError(
                "Could not reach Ollama. Please ensure it is running on this machine."
            ) from exc

        if health.status_code != 200:
            raise LLMError(
                "Ollama responded unexpectedly. Please restart Ollama and try again."
            )

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        try:
            response = requests.post(
                f"{host}/api/chat", json=payload, timeout=30, stream=False
            )
        except requests.RequestException as exc:
            raise LLMError(
                "Failed to call Ollama. Is the service running on the configured host?"
            ) from exc

        if response.status_code == 404:
            raise LLMError(
                "Model not found. Please install it with: ollama pull llama3.2:3b"
            )
        if response.status_code >= 500:
            raise LLMError("Ollama server error. Please try again after a moment.")
        if response.status_code >= 400:
            raise LLMError(
                "Ollama rejected the request. If the model is missing, run: ollama pull llama3.2:3b"
            )

        data = response.json()
        message = data.get("message", {})
        content = message.get("content")
        if not content:
            raise LLMError("Ollama returned an empty response.")
        return content

    def _openrouter_chat(self, messages: List[Dict[str, str]]) -> str:
        api_key = str(self.config.get("openrouter_api_key") or "")
        model = str(self.config.get("openrouter_model") or "openrouter/auto")
        base_url = str(self.config.get("openrouter_base_url") or "https://openrouter.ai/api/v1")

        if not api_key:
            raise LLMError("OpenRouter API key is missing in settings.")

        client = OpenAI(api_key=api_key, base_url=base_url)
        try:
            chat = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False,
            )
        except Exception as exc:  # pylint: disable=broad-except
            raise LLMError("OpenRouter call failed. Check network and API key.") from exc

        try:
            content = chat.choices[0].message.content
        except (AttributeError, IndexError):
            content = None
        if not content:
            raise LLMError("OpenRouter returned an empty response.")
        return content

    def chat(self, messages: List[Dict[str, str]]) -> str:
        provider = self.config.get("provider", "Ollama (Local)")
        if provider == "Ollama (Local)":
            return self._ollama_chat(messages)
        if provider == "OpenRouter (API)":
            return self._openrouter_chat(messages)
        raise LLMError("Unsupported provider selected.")

    def request_action(self, objective: str, screenshot_note: str) -> str:
        prompt = (
            "You are controlling a computer. Decide the SINGLE next action as strict JSON only. "
            "Use one of: click, type, hotkey, wait, done. Respond with JSON only."
        )
        instructions = (
            "Schema: {\"type\":\"click\",\"x\":int,\"y\":int} | "
            "{\"type\":\"type\",\"text\":str} | "
            "{\"type\":\"hotkey\",\"keys\":[str,...]} | "
            "{\"type\":\"wait\",\"seconds\":float} | "
            "{\"type\":\"done\",\"reason\":str}. "
            "Only one action. No explanation."
        )
        user_message = (
            f"Objective: {objective}\n"
            f"Latest screenshot: {screenshot_note}\n"
            "Output JSON only."
        )
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": instructions},
            {"role": "user", "content": user_message},
        ]
        return self.chat(messages)


def parse_action_text(text: str) -> Optional[Dict[str, object]]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    action_type = data.get("type")
    if action_type not in {"click", "type", "hotkey", "wait", "done"}:
        return None
    if action_type == "click":
        if isinstance(data.get("x"), int) and isinstance(data.get("y"), int):
            return {"type": "click", "x": data["x"], "y": data["y"]}
    elif action_type == "type":
        if isinstance(data.get("text"), str):
            return {"type": "type", "text": data["text"]}
    elif action_type == "hotkey":
        keys = data.get("keys")
        if isinstance(keys, list) and all(isinstance(k, str) for k in keys):
            return {"type": "hotkey", "keys": keys}
    elif action_type == "wait":
        seconds = data.get("seconds")
        if isinstance(seconds, (int, float)):
            return {"type": "wait", "seconds": float(seconds)}
    elif action_type == "done":
        reason = data.get("reason")
        if isinstance(reason, str):
            return {"type": "done", "reason": reason}
    return None
