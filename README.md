ome
<h1 align="center">Self-Operating Computer Framework</h1>

<p align="center">
  <strong>A framework to enable multimodal models to operate a computer.</strong>
</p>

### Version v2.0.5 (Latest) Release Summary

**New Features:**

*   **Interactive Model Selection:** When running `operate` without specifying a model, a welcome screen is displayed, followed by an interactive menu to select your desired model.
*   **Dynamic API Key Prompting:** The application now intelligently prompts for required API keys (e.g., OpenAI, Google, Anthropic) only when a model requiring that key is selected and the key is not found in your environment variables or `.env` file.
*   **Custom System Prompt:** Users can now provide a custom system prompt from a file or an environment variable (`CUSTOM_SYSTEM_PROMPT`). If the environment variable is set, the option to load from it will be hidden.

**Improvements:**

*   **Expanded Google Gemini Support:** Added full support for `gemini-2.5-pro` and `gemini-2.5-flash` models.
*   **Enhanced Ollama Integration:** Improved handling for Ollama models, including setting `http://localhost:11434` as the default host and providing more informative error messages when Ollama models are not found.
*   **Gemma 3n Model Support:** Integrated support for `gemma3n`, `gemma3n:e2b`, and `gemma3n:e4b` models via Ollama.
*   **Robust Error Handling:** Improved error handling for API calls to prevent unexpected fallbacks and provide clearer error messages.

**Bug Fixes:**

*   Resolved an issue where the application would incorrectly prompt for an OpenAI API key when a Google Gemini model was selected.
*   Fixed an issue where the application would attempt to use an incorrect model name for `gemini-2.5-flash-lite` (which is not a valid model name).
*   Addressed the "Extra data" JSON parsing error when receiving responses from Gemini models.

<p align="center">
  Using the same inputs and outputs as a human operator, the model views the screen and decides on a series of mouse and keyboard actions to reach an objective. Released Nov 2023, the Self-Operating Computer Framework was one of the first examples of usiself-ai-operating-computerng a multimodal model to view the screen and operate a computer.
</p>

<div align="center">
  <img src="/readme/choose-model.png" width="750"  style="max-width: 100%;"/>
</div>


<!--
:rotating_light: **OUTAGE NOTIFICATION: gpt-4o**
**This model is currently experiencing an outage so the self-operating computer may not work as expected.**
-->


## Key Features
- **Compatibility**: Designed for various multimodal models.
- **Expanded Model Support**: Now integrated with the latest **OpenAI o3, o4-mini, GPT-4.1, GPT-4.1 mini, GPT-4.1 nano**, **Gemini 2.5 Pro, Gemini 2.5 Flash**, and **Gemma 3n** models (including `e2b` and `e4b` variants), alongside existing support for GPT-4o, Claude 3, Qwen-VL, and LLaVa.
- **Enhanced Ollama Integration**: Improved handling for Ollama models, including default host configuration and more informative error messages.
- **Future Plans**: Support for additional models.

## Demo
https://github.com/malah-code/self-ai-operating-computer/assets/42594239/9e8abc96-c76a-46fb-9b13-03678b3c67e0


## Run `Self-Operating Computer`

### Run from PyPI

To run the application by installing it from PyPI, follow these steps:

1.  **Install the project:**
    ```bash
    pip install self-ai-operating-computer
    ```
2.  **Run the project:**
    ```bash
    operate
    ```

### Run from Source Code

To run the application from your local copy (after making changes), follow these steps:

1.  **Uninstall previous installations (if any):**
    ```bash
    pip uninstall self-ai-operating-computer
    ```
    Confirm uninstallation when prompted.

2.  **Install in editable mode:**
    Navigate to the project's root directory (where `setup.py` is located) and run:
    ```bash
    pip install -e .
    ```
    This links your local source code to your Python environment, so changes are immediately reflected.

3.  **Run the project:**
    ```bash
    operate
    ```
    If you run `operate` without any arguments, a welcome screen will be displayed, followed by an interactive model selection menu. If a model requires an API key that is not found in your environment variables or `.env` file, you will be prompted to enter it.

<div align="center">
  <img src="/readme/choose-model.png" width="300"  style="margin: 10px;"/>
</div>

Once you select a model, you will be prompted to provide a custom system prompt. This can be loaded from a file or an environment variable.

<div align="center">
  <img src="/readme/system-parameter-1.png" width="300"  style="margin: 10px;"/>
  <img src="/readme/system-parameter-2.png" width="300"  style="margin: 10px;"/>
</div>

4.  **Enter your OpenAI Key**: If you don't have one, you can obtain an OpenAI key [here](https://platform.openai.com/account/api-keys). If you need you change your key at a later point, run `vim .env` to open the `.env` and replace the old key. 

<div align="center">
  <img src="/readme/key.png" width="300"  style="margin: 10px;"/>
</div>

5.  **Give Terminal app the required permissions**: As a last step, the Terminal app will ask for permission for "Screen Recording" and "Accessibility" in the "Security & Privacy" page of Mac's "System Preferences".

<div align="center">
  <img src="/readme/terminal-access-1.png" width="300"  style="margin: 10px;"/>
  <img src="/readme/terminal-access-2.png" width="300"  style="margin: 10px;"/>
</div>

## Using `operate` Modes

#### OpenAI models

The default model for the project is gpt-4o which you can use by simply typing `operate`. To try running OpenAI's new `o1` model, use the command below.

```
operate -m o1-with-ocr
```

To experiment with OpenAI's latest `gpt-4.1` model, run:

```
operate -m gpt-4.1
```

To experiment with OpenAI's latest `gpt-4.1 mini` model, run:

```
operate -m gpt-4.1-mini
```

To experiment with OpenAI's latest `gpt-4.1 nano` model, run:

```
operate -m gpt-4.1-nano
```

To experiment with OpenAI's latest `o3` model, run:

```
operate -m o3
```

To experiment with OpenAI's latest `o4-mini` model, run:

```
operate -m o4-mini
```


### Multimodal Models  `-m`
Try Google's `gemini-1.5-pro-latest`, `gemini-2.5-pro`, or `gemini-2.5-flash` by following the instructions below. Start `operate` with the Gemini model
```
operate -m gemini-2.5-pro
```

**Enter your Google AI Studio API key when terminal prompts you for it** If you don't have one, you can obtain a key [here](https://makersuite.google.com/app/apikey) after setting up your Google AI Studio account. You may also need [authorize credentials for a desktop application](https://ai.google.dev/palm_docs/oauth_quickstart). It took me a bit of time to get it working, if anyone knows a simpler way, please make a PR.

#### Try Claude `-m claude-3`
Use Claude 3 with Vision to see how it stacks up to GPT-4-Vision at operating a computer. Navigate to the [Claude dashboard](https://console.anthropic.com/dashboard) to get an API key and run the command below to try it. 

```
operate -m claude-3
```

#### Try qwen `-m qwen-vl`
Use Qwen-vl with Vision to see how it stacks up to GPT-4-Vision at operating a computer. Navigate to the [Qwen dashboard](https://bailian.console.aliyun.com/) to get an API key and run the command below to try it. 

```
operate -m qwen-vl
```

#### Try LLaVa Hosted Through Ollama `-m llava`
If you wish to experiment with the Self-Operating Computer Framework using LLaVA on your own machine, you can with Ollama!   

First, install Ollama on your machine from https://ollama.ai/download.   

Once Ollama is installed, pull the LLaVA model:
```
ollama pull llava
```
This will download the model on your machine which takes approximately 5 GB of storage.   

When Ollama has finished pulling LLaVA, start the server:
```
ollama serve
```

That's it! Now start `operate` and select the LLaVA model:
```
operate -m llava
```   
**Important:** Error rates when using LLaVA are very high. This is simply intended to be a base to build off of as local multimodal models improve over time.

#### Try Gemma 3n Hosted Through Ollama `-m gemma3n`
If you wish to experiment with the Self-Operating Computer Framework using Gemma 3n on your own machine, you can with Ollama!   
*Note: Ollama currently only supports MacOS and Linux. Windows now in Preview*   

First, install Ollama on your machine from https://ollama.ai/download.   

Once Ollama is installed, pull the Gemma 3n model:
```
ollama pull gemma3n
```
This will download the model on your machine. You can also pull specific versions like `ollama pull gemma3n:e2b` or `ollama pull gemma3n:e4b`.

When Ollama has finished pulling Gemma 3n, start the server:
```
ollama serve
```

That's it! Now start `operate` and select the Gemma 3n model. You can specify `gemma3n`, `gemma3n:e2b`, or `gemma3n:e4b`:
```
operate -m gemma3n:e2b
```   

Learn more about Ollama at its [GitHub Repository](https://www.github.com/ollama/ollama)

### Voice Mode `--voice`
The framework supports voice inputs for the objective. Try voice by following the instructions below. 
**Clone the repo** to a directory on your computer:
```
git clone https://github.com/malah-code/self-ai-operating-computer.git
```
**Cd into directory**:
```
cd self-ai-operating-computer
```
Install the additional `requirements-audio.txt`
```
pip install -r requirements-audio.txt
```
**Install device requirements**
For mac users:
```
brew install portaudio
```
For Linux users:
```
sudo apt install portaudio19-dev python3-pyaudio
```
Run with voice mode
```
operate --voice
```

### Optical Character Recognition Mode `-m gpt-4-with-ocr`
The Self-Operating Computer Framework now integrates Optical Character Recognition (OCR) capabilities with the `gpt-4-with-ocr` mode. This mode gives GPT-4 a hash map of clickable elements by coordinates. GPT-4 can decide to `click` elements by text and then the code references the hash map to get the coordinates for that element GPT-4 wanted to click. 

Based on recent tests, OCR performs better than `som` and vanilla GPT-4 so we made it the default for the project. To use the OCR mode you can simply write: 

 `operate` or `operate -m gpt-4-with-ocr` will also work. 

### Set-of-Mark Prompting `-m gpt-4-with-som`
The Self-Operating Computer Framework now supports Set-of-Mark (SoM) Prompting with the `gpt-4-with-som` command. This new visual prompting method enhances the visual grounding capabilities of large multimodal models.

Learn more about SoM Prompting in the detailed arXiv paper: [here](https://arxiv.org/abs/2310.11441).

For this initial version, a simple YOLOv8 model is trained for button detection, and the `best.pt` file is included under `model/weights/`. Users are encouraged to swap in their `best.pt` file to evaluate performance improvements. If your model outperforms the existing one, please contribute by creating a pull request (PR).

Start `operate` with the SoM model

```
operate -m gpt-4-with-som
```



## Contributions are Welcomed!:

If you want to contribute yourself, see [CONTRIBUTING.md](/CONTRIBUTING.md).

## Feedback

For any input on improving this project, feel free to reach out to [Josh](https://twitter.com/josh_bickett) on Twitter. 

## Join Our Discord Community

For real-time discussions and community support, join our Discord server. 
- If you're already a member, join the discussion in [#self-ai-operating-computer](https://discord.com/channels/877638638001877052/1181241785834541157).
- If you're new, first [join our Discord Server](https://discord.com/channels/877638638001877052/1181241785834541157).

## Follow HyperWriteAI for More Updates

Stay updated with the latest developments:
- Follow HyperWriteAI on [Twitter](https://twitter.com/HyperWriteAI).
- Follow HyperWriteAI on [LinkedIn](https://www.linkedin.com/company/malah-code/).

## Compatibility
- This project is compatible with Mac OS, Windows, and Linux (with X server installed).

## OpenAI Rate Limiting Note
The ```gpt-4o``` model is required. To unlock access to this model, your account needs to spend at least $5 in API credits. Pre-paying for these credits will unlock access if you haven't already spent the minimum $5.   
Learn more **[here](https://platform.openai.com/docs/guides/rate-limits?context=tier-one)**

## Supported Models Summary

Here's a summary of all currently supported models and how to run them:

*   **OpenAI GPT-4o (Default):**
    ```
    operate
    ```
*   **OpenAI o1-with-ocr:**
    ```
    operate -m o1-with-ocr
    ```
*   **OpenAI o3:**
    ```
    operate -m o3
    ```
*   **OpenAI o4-mini:**
    ```
    operate -m o4-mini
    ```
*   **OpenAI gpt-4.1:**
    ```
    operate -m gpt-4.1
    ```
*   **OpenAI gpt-4.1 mini:**
    ```
    operate -m gpt-4.1-mini
    ```
*   **OpenAI gpt-4.1 nano:**
    ```
    operate -m gpt-4.1-nano
    ```
*   **OpenAI gpt-4-with-ocr:**
    ```
    operate -m gpt-4-with-ocr
    ```
*   **OpenAI gpt-4-with-som:**
    ```
    operate -m gpt-4-with-som
    ```
*   **Google Gemini 1.5 Pro (latest):**
    ```
    operate -m gemini-1.5-pro-latest
    ```
*   **Google Gemini 2.5 Pro:**
    ```
    operate -m gemini-2.5-pro
    ```
*   **Google Gemini 2.5 Flash:**
    ```
    operate -m gemini-2.5-flash
    ```
*   **Anthropic Claude 3:**
    ```
    operate -m claude-3
    ```
*   **Qwen-VL:**
    ```
    operate -m qwen-vl
    ```
*   **LLaVa (via Ollama):**
    ```
    operate -m llava
    ```
*   **Gemma 3n (via Ollama):**
    ```
    operate -m gemma3n
    ```
*   **Gemma 3n:e2b (via Ollama):**
    ```
    operate -m gemma3n:e2b
    ```
*   **Gemma 3n:e4b (via Ollama):**
    ```
    operate -m gemma3n:e4b
    ```

## Release Notes

### Version 0.0.X (Latest)

**New Features:**

*   **Interactive Model Selection:** When running `operate` without specifying a model, a welcome screen is displayed, followed by an interactive menu to select your desired model.
*   **Dynamic API Key Prompting:** The application now intelligently prompts for required API keys (e.g., OpenAI, Google, Anthropic) only when a model requiring that key is selected and the key is not found in your environment variables or `.env` file.
*   **Custom System Prompt:** Users can now provide a custom system prompt from a file or an environment variable (`CUSTOM_SYSTEM_PROMPT`). If the environment variable is set, the option to load from it will be hidden.

**Improvements:**

*   **Expanded Google Gemini Support:** Added full support for `gemini-2.5-pro` and `gemini-2.5-flash` models.
*   **Enhanced Ollama Integration:** Improved handling for Ollama models, including setting `http://localhost:11434` as the default host and providing more informative error messages when Ollama models are not found.
*   **Gemma 3n Model Support:** Integrated support for `gemma3n`, `gemma3n:e2b`, and `gemma3n:e4b` models via Ollama.
*   **Robust Error Handling:** Improved error handling for API calls to prevent unexpected fallbacks and provide clearer error messages.

**Bug Fixes:**

*   Resolved an issue where the application would incorrectly prompt for an OpenAI API key when a Google Gemini model was selected.
*   Fixed an issue where the application would attempt to use an incorrect model name for `gemini-2.5-flash-lite` (which is not a valid model name).
*   Addressed the "Extra data" JSON parsing error when receiving responses from Gemini models.
