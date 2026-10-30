# Self-Operating Computer v1 (clean rebuild)

A minimal Windows-friendly rewrite that runs a decide-and-act loop with a local Ollama model (no API keys required). Phase B wiring for OpenRouter is also in place.

## Features
- Tkinter GUI with Tasks, Settings, and Logs tabs
- Dry Run safety (on by default) and STOP hotkey/button
- Loop: screenshot → LLM JSON action → validate → (optionally) execute via `pyautogui`
- Config persisted to `rebuild_v1/config.json`

## Requirements
- Python 3.11 on Windows
- [Ollama](https://ollama.com) running locally (default host `http://localhost:11434`)
- Optional: OpenRouter API key for Phase B

Install Python packages:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r rebuild_v1/requirements.txt
```

## Running the app
```bash
python -m rebuild_v1.main
```
If Tkinter fails to start in a headless environment, run on a local desktop session.

## Using Ollama (Phase A)
1. Start Ollama: `ollama serve`
2. Pull the default model once: `ollama pull llama3.2:3b`
3. Ensure the host and model fields in **Settings** match your setup.

The app checks connectivity to Ollama and shows a friendly message if the server or model is unavailable.

## Safety controls
- **Dry Run**: enabled by default; shows actions without executing.
- **STOP hotkey**: `Ctrl+Alt+S` (configurable) registered via the `keyboard` library.
- **STOP button**: halts the current loop.
- **Max steps** and **delay** configurable in Settings.

## OpenRouter (Phase B)
A provider dropdown exists; if "OpenRouter (API)" is chosen, set your API key, model, and base URL in Settings. Requests use the OpenAI-compatible SDK.

## Notes
- Screenshots use Pillow's `ImageGrab`; ensure a visible desktop session.
- Avoid sharing `config.json`—it is gitignored and may contain sensitive keys.
