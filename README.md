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

### Key Features
- **Compatibility**: Designed for various multimodal models.
- **Integration**: Currently integrated with **GPT-4v** as the default model.
- **Future Plans**: Support for additional models.

### Current Challenges
> **Note:** GPT-4V's error rate in estimating XY mouse click locations is currently quite high. This framework aims to track the progress of multimodal models over time, aspiring to achieve human-level performance in computer operation.

### Ongoing Development
At [HyperwriteAI](https://www.hyperwriteai.com/), we are developing Agent-1-Vision a multimodal model with more accurate click location predictions.

### Agent-1-Vision Model API Access
We will soon be offering API access to our Agent-1-Vision model.

If you're interested in gaining access to this API, sign up [here](https://othersideai.typeform.com/to/FszaJ1k8?typeform-source=www.hyperwriteai.com).

### Additional Thoughts
We recognize that some operating system functions may be more efficiently executed with hotkeys such as entering the Browser Address bar using `command + L` rather than by simulating a mouse click at the correct XY location. We plan to make these improvements over time. However, it's important to note that many actions require the accurate selection of visual elements on the screen, necessitating precise XY mouse click locations. A primary focus of this project is to refine the accuracy of determining these click locations. We believe this is essential for achieving a fully self-operating computer in the current technological landscape.
## Demo

https://github.com/OthersideAI/self-operating-computer/assets/42594239/9e8abc96-c76a-46fb-9b13-03678b3c67e0

## Quick Start Instructions
Below are instructions to set up the Self-Operating Computer Framework locally on your computer.

1. **Clone the repo** to a directory on your computer:
```
git clone https://github.com/OthersideAI/self-operating-computer.git
```
2. **Cd into directory**:

```
cd self-operating-computer
```

3. **Create a Python virtual environment**. [Learn more about Python virtual environment](https://docs.python.org/3/library/venv.html).

```
python3 -m venv venv
```

4. **Activate the virtual environment**:
```
source venv/bin/activate
```
5. **Install the project requirements**:
```
pip install -r requirements.txt
```
6. **Install Project and Command-Line Interface**:
```
pip install .
```
7. **Then rename the `.example.env` file to `.env` so that you can save your OpenAI key in it.**
```
mv .example.env .env
``` 
8. **Add your Open AI key to your new `.env` file. If you don't have one, you can obtain an OpenAI key [here](https://platform.openai.com/account/api-keys)**:
```
OPENAI_API_KEY='your-key-here'
```
9. **Run it**!
```
operate
```
10. **Final Step**: As a last step, the Terminal app will ask for permission for "Screen Recording" and "Accessibility" in the "Security & Privacy" page of Mac's "System Preferences".

<div align="center">
  <img src="https://github.com/OthersideAI/self-operating-computer/blob/main/readme/terminal-access-1.png" width="300"  style="margin: 10px;"/>
  <img src="https://github.com/OthersideAI/self-operating-computer/blob/main/readme/terminal-access-2.png" width="300"  style="margin: 10px;"/>
</div>

### Accurate mouse clicks
When running operate, you can optionally add an -accurate tag when running operate to improve the model's mouse clicking accuracy. However, by turning on -accurate, additional GPT requests will be sent. 
**Example run**:
```
operate -accurate
```

### Contributions are Welcomed!:

If you want to contribute yourself, see [CONTRIBUTING.md](https://github.com/OthersideAI/self-operating-computer/blob/main/CONTRIBUTING.md).

### Feedback

For any input on improving this project, feel free to reach out to [Josh](https://twitter.com/josh_bickett) on Twitter. 

### Follow HyperWriteAI for More Updates

Stay updated with the latest developments:
- Follow HyperWriteAI on [Twitter](https://twitter.com/HyperWriteAI).
- Follow HyperWriteAI on [LinkedIn](https://www.linkedin.com/company/othersideai/).

### Compatibility
- This project is compatible with Mac OS, Windows, and Linux (with X server installed).

### Star History

[![Star History Chart](https://api.star-history.com/svg?repos=OthersideAI/self-operating-computer&type=Timeline)](https://star-history.com/#OthersideAI/self-operating-computer&Timeline)
