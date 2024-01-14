<h1 align="center">Self-Operating Computer Framework</h1>

<p align="center">
  <strong>A framework to enable multimodal models to operate a computer.</strong>
</p>
<p align="center">
  Using the same inputs and outputs as a human operator, the model views the screen and decides on a series of mouse and keyboard actions to reach an objective. 
</p>

<div align="center">
  <img src="https://github.com/OthersideAI/self-operating-computer/blob/main/readme/self-operating-computer.png" width="750"  style="margin: 10px;"/>
</div>

<!--
:rotating_light: **OUTAGE NOTIFICATION: gpt-4-vision-preview**
**This model is currently experiencing an outage so the self-operating computer may not work as expected.**
-->


## Key Features
- **Compatibility**: Designed for various multimodal models.
- **Integration**: Currently integrated with **GPT-4v** as the default model, with extended support for Gemini Pro Vision.
- **Future Plans**: Support for additional models.

## Current Challenges
> **Note:** GPT-4V's error rate in estimating XY mouse click locations is currently quite high. This framework aims to track the progress of multimodal models over time, aspiring to achieve human-level performance in computer operation.

## Ongoing Development
At [HyperwriteAI](https://www.hyperwriteai.com/), we are developing Agent-1-Vision a multimodal model with more accurate click location predictions.

## Agent-1-Vision Model API Access
We will soon be offering API access to our Agent-1-Vision model.

If you're interested in gaining access to this API, sign up [here](https://othersideai.typeform.com/to/FszaJ1k8?typeform-source=www.hyperwriteai.com).

### Additional Thoughts
We recognize that some operating system functions may be more efficiently executed with hotkeys such as entering the Browser Address bar using `command + L` rather than by simulating a mouse click at the correct XY location. We plan to make these improvements over time. However, it's important to note that many actions require the accurate selection of visual elements on the screen, necessitating precise XY mouse click locations. A primary focus of this project is to refine the accuracy of determining these click locations. We believe this is essential for achieving a fully self-operating computer in the current technological landscape.
## Demo

https://github.com/OthersideAI/self-operating-computer/assets/42594239/9e8abc96-c76a-46fb-9b13-03678b3c67e0


## Quick Start Instructions
Below are instructions to set up the Self-Operating Computer Framework locally on your computer.

### Option 1: Quick Start
1. **Install the project locally**:
```
pip install self-operating-computer
```
2. **Add your Open AI key. If you don't have one, you can obtain an OpenAI key [here](https://platform.openai.com/account/api-keys)**:

For Mac:
```
export OPENAI_API_KEY='your-key-here'
``` 
For Windows:
```
set GOOGLE_API_KEY='your_api_key'
```
3. **Run it**!
```
operate
```
5. **Final Step**: As a last step, the Terminal app will ask for permission for "Screen Recording" and "Accessibility" in the "Security & Privacy" page of Mac's "System Preferences".

<div align="center">
  <img src="https://github.com/OthersideAI/self-operating-computer/blob/main/readme/terminal-access-1.png" width="300"  style="margin: 10px;"/>
  <img src="https://github.com/OthersideAI/self-operating-computer/blob/main/readme/terminal-access-2.png" width="300"  style="margin: 10px;"/>
</div>


### Option 2: Installation using .sh script

1. **Clone the repo** to a directory on your computer:
```
git clone https://github.com/OthersideAI/self-operating-computer.git
```
2. **Cd into directory**:

```
cd self-operating-computer
```

3. **Run the installation script**: 

```
./run.sh
```


## Using `operate` Modes

### Multimodal Models  `-m`
An additional model is now compatible with the Self Operating Computer Framework. Try Google's `gemini-pro-vision` by following the instructions below. 

**Add your Google AI Studio API key to your .env file.** If you don't have one, you can obtain a key [here](https://makersuite.google.com/app/apikey) after setting up your Google AI Studio account. You may also need [authorize credentials for a desktop application](https://ai.google.dev/palm_docs/oauth_quickstart). It took me a bit of time to get it working, if anyone knows a simpler way, please make a PR:
```
GOOGLE_API_KEY='your-key-here'
```

Start `operate` with the Gemini model
```
operate -m gemini-pro-vision
```

### Set-of-Mark Prompting `-m gpt-4-with-som`
The Self-Operating Computer Framework now supports Set-of-Mark (SoM) Prompting with the `gpt-4-with-som` command. This new visual prompting method enhances the visual grounding capabilities of large multimodal models.

Learn more about SoM Prompting in the detailed arXiv paper: [here](https://arxiv.org/abs/2310.11441).

For this initial version, a simple YOLOv8 model is trained for button detection, and the `best.pt` file is included under `model/weights/`. Users are encouraged to swap in their `best.pt` file to evaluate performance improvements. If your model outperforms the existing one, please contribute by creating a pull request (PR).

Start `operate` with the SoM model

```
operate -m gpt-4-with-som
```

### Voice Mode `--voice`
The framework supports voice inputs for the objective. Try voice by following the instructions below. 

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

## Contributions are Welcomed!:

If you want to contribute yourself, see [CONTRIBUTING.md](https://github.com/OthersideAI/self-operating-computer/blob/main/CONTRIBUTING.md).

## Feedback

For any input on improving this project, feel free to reach out to [Josh](https://twitter.com/josh_bickett) on Twitter. 

## Join Our Discord Community

For real-time discussions and community support, join our Discord server. 
- If you're already a member, join the discussion in [#self-operating-computer](https://discord.com/channels/877638638001877052/1181241785834541157).
- If you're new, first [join our Discord Server](https://discord.gg/YqaKtyBEzM) and then navigate to the [#self-operating-computer](https://discord.com/channels/877638638001877052/1181241785834541157).

## Follow HyperWriteAI for More Updates

Stay updated with the latest developments:
- Follow HyperWriteAI on [Twitter](https://twitter.com/HyperWriteAI).
- Follow HyperWriteAI on [LinkedIn](https://www.linkedin.com/company/othersideai/).

## Compatibility
- This project is compatible with Mac OS, Windows, and Linux (with X server installed).

## OpenAI Rate Limiting Note
The ```gpt-4-vision-preview``` model is required. To unlock access to this model, your account needs to spend at least \$5 in API credits. Pre-paying for these credits will unlock access if you haven't already spent the minimum \$5.   
Learn more **[here](https://platform.openai.com/docs/guides/rate-limits?context=tier-one)**
