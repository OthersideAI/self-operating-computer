# Self-Operating Computer GUI

A graphical user interface for the Self-Operating Computer, allowing easy interaction with AI models to automate computer tasks.

## Features

- **Intuitive Chat Interface**: Communicate with the Self-Operating Computer through a familiar chat interface
- **Live Screenshot Preview**: See what the AI sees in real-time
- **Model Selection**: Choose from multiple AI models including GPT-4, Claude, Qwen, and more
- **Voice Control**: Speak your commands using the built-in voice recognition (requires whisper_mic)
- **Real-time Logs**: Monitor detailed logs of operations in real-time
- **Multi-platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites

- Python 3.8 or higher
- Self-Operating Computer installed and configured
- pip (Python package manager)

### Required Packages

```bash
pip install PyQt5
pip install whisper_mic  # Optional, for voice commands
```

## Usage

### Running the GUI

From the Self-Operating Computer directory:

```bash
python gui_main.py
```

### Command Line Options

```
usage: gui_main.py [-h] [-m MODEL] [--verbose] [--light]

Run the Self-Operating Computer GUI with a specified model.

optional arguments:
  -h, --help            show this help message and exit
  -m MODEL, --model MODEL
                        Specify the default model to use
  --verbose             Run with verbose logging
  --light               Use light mode instead of dark mode
```

### Examples

```bash
# Run with GPT-4 model and verbose logging
python gui_main.py -m gpt-4-vision --verbose

# Run with Claude 3 model in light mode
python gui_main.py -m claude-3 --light
```

## Interface Guide

The GUI is divided into several sections:

1. **Top Bar**: Contains model selection dropdown and verbose mode toggle
2. **Left Panel**: Displays the current screenshot that the AI sees
3. **Right Panel - Top**: Chat history showing your requests and system messages
4. **Right Panel - Bottom**: Detailed logs of operations in real-time
5. **Bottom Input**: Text field for typing tasks, Send button, and voice recording button

## Model Support

The GUI supports all models that the Self-Operating Computer supports:

- GPT-4 Vision
- GPT-4 with SOM (Spatial Object Memory)
- GPT-4 with OCR
- Claude 3
- Claude 3.7
- Qwen-VL
- O1 with OCR
- Gemini Pro Vision
- LLaVA

## API Keys

The GUI uses the same API key configuration as the main Self-Operating Computer. If a required API key is missing, a prompt will appear asking you to enter it.

## Troubleshooting

### Voice Recognition Not Working

Make sure you have installed whisper_mic:
```bash
pip install whisper_mic
```

### GUI Not Launching

Check that PyQt5 is properly installed:
```bash
pip install PyQt5
```

### Model Not Responding

Ensure your API keys are properly configured in the Self-Operating Computer settings.

## Integration with Existing Codebase

The GUI integrates seamlessly with the existing Self-Operating Computer codebase:

- It uses the same `operate.py` functions for executing tasks
- It leverages the same model APIs from `apis.py`
- It inherits configuration from `config.py`
- It preserves the same prompt formats from `prompts.py`

The UI simply provides a graphical wrapper around these core components, making them more accessible to users who prefer not to use the comman