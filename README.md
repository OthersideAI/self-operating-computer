# Self-Operating Computer Framework

**This framework enables multimodal models to operate a computer, replicating the inputs and outputs of a human operator.** Models receive an objective and proceed by analyzing a screenshot at each step, subsequently generating the next mouse or keyboard action.

<div align="center">
  <img src="https://github.com/OthersideAI/self-operating-computer/blob/main/readme/self-operating-computer.png" width="500"  style="margin: 10px;"/>
</div>

### Key Features
- **Compatibility**: Designed for various multimodal models.
- **Integration**: Currently integrated with **GPT-4v** as the default model.
- **Future Plans**: Support for additional models.

### Current Challenges
> **Note:** The GPT-4v's error rate in estimating XY mouse click locations is currently quite high. This framework aims to track the progress of multimodal models over time, aspiring to achieve human-level performance in computer operation.

### Ongoing Development
At [HyperwriteAI](https://www.hyperwriteai.com/), we are developing a multimodal model with more accurate click location predictions.

### Additional Thoughts
We recognize that some operating system functions may be more efficiently executed with hotkeys such as entering the Browser Address bar using `command + L` rather than by simulating a mouse click at the correct XY location. We plan to make these improvements over time. However, it's important to note that many actions require the accurate selection of visual elements on the screen, necessitating precise XY mouse click locations. A primary focus of this project is to refine the accuracy of determining these click locations. We believe this is essential for achieving a fully self-operating computer in the current technological landscape.

## Instructions
Below are instructions to set up the Self-Operating Computer Framework locally on your computer.

1. **Clone the repo** to a directory on your computer:
```
git clone https://github.com/OthersideAI/self-operating-computer.git
```
2. **Create a Python virtual environment**. [Learn more about Python virtual environment](https://docs.python.org/3/library/venv.html).

```
python3 -m venv venv
```
3. **Activate the virtual environment**:
```
source venv/bin/activate
```
4. **Install the project requirements**:
```
pip install -r requirements.txt
```
5. **Install Project and Command-Line Interface**:
```
pip install .
```
6. **Then rename the `.example.env` file to `.env` so that you can save your OpenAI key in it.**
```
mv .env.example .env
``` 
7. **Add your Open AI key to your new `.env` file. If you don't have one, you can obtain an OpenAI key [here](https://platform.openai.com/account/api-keys)**:
```
OPENAI_API_KEY='your-key-here'
```
6. **Run it**!
```
operate
```
7. **Final Step**: As a last step, the Terminal app will ask for permission for "Screen Recording" and "Accessibility" in the "Security & Privacy" page of Mac's "System Preferences".

<div align="center">
  <img src="https://github.com/OthersideAI/self-operating-computer/blob/main/readme/terminal-access-1.png" width="300"  style="margin: 10px;"/>
  <img src="https://github.com/OthersideAI/self-operating-computer/blob/main/readme/terminal-access-2.png" width="300"  style="margin: 10px;"/>
</div>

### Contributions are Welcomed! Some Ideas: 
- **Prompt Improvements**: Noticed any areas for prompt improvements? Feel free to make suggestions or submit a pull request (PR). 
- **Framework Architecture Improvements**: Think you can enhance the framework architecture described in the intro? We welcome suggestions and PRs.
- **Innovative Ideas**: Have an idea to improve this project in ways we haven't considered? Whether it's transforming this into an evaluation system for multimodal models or something else, we're open to your ideas!

For any input on improving this project, feel free to reach out to me on [Twitter](https://twitter.com/josh_bickett).

### Follow HyperWriteAI for More Updates

Stay updated with the latest developments:
- Follow HyperWriteAI on [Twitter](https://twitter.com/HyperWriteAI).
- Follow HyperWriteAI on [LinkedIn](https://www.linkedin.com/company/othersideai/).

### Other important notes
- This project is only compatible with MacOS as this time. 