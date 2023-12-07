<h1 align="center">Self-Operating Computer Framework</h1>

<p align="center">
  <strong>A framework to enable multimodal models to operate a computer.</strong>
</p>
<p align="center">
  Using the same inputs and outputs of a human operator, the model views the screen and decides on a series of mouse and keyboard actions to reach an objective. 
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
- **Integration**: Currently integrated with **GPT-4v** as the default model.
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

**You must have `git` installed in order to execute the following commands.**

**These instructions are partially specific to Linux machines.**

### 1. **Setup the execution environment:**
```
git clone https://github.com/OthersideAI/self-operating-computer.git
cd self-operating-computer
./deploy/bare-metal/linux/debian.sh
source venv/bin/activate
```

### 2. **Edit the default settings in your choice of text editor:**
```
vim .env
```

**Notice!** Make sure you at lest set the SOC_OPENAI_API_KEY setting to your OpenAI API key or the app will not work.

**Notice!** Make sure to adjust the `screen_width` and `screen_height` settings to match your screen resolution.

**Notice!** All settings can be set via environment variables just as they are in the `.env` file.

### 3. **Run it!**

**Mac Users:** When you run this app, the Terminal app will ask for permission for "Screen Recording" and "Accessibility" in the "Security & Privacy" page of Mac's "System Preferences".

```
soc run
```

<div align="center">
  <img src="https://github.com/OthersideAI/self-operating-computer/blob/main/readme/terminal-access-1.png" width="300"  style="margin: 10px;"/>
  <img src="https://github.com/OthersideAI/self-operating-computer/blob/main/readme/terminal-access-2.png" width="300"  style="margin: 10px;"/>
</div>

## Using `soc` Modes

### Voice Mode

Additional dependencies for voice mode need to be installed with the following commands:

**All Users:**
```
pip install -r requirements-audio.txt
```

**For Mac Users**
```
brew install portaudio
```

Now you should be ready to run in voice mode with the `-v` flag:
```
soc run -v
```

### High Accuracy Mode

To run in high-accuracy mode where additional screenshots are taken for verification, run with the `-a` flag:
```
soc run -a
```

### Debug Mode

To run with additional debugging output, run with the `-d` flag:
```
soc run -d
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