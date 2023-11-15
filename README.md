# Self-Operating Computer Framework

**This framework enables multimodal models to operate a computer, replicating the inputs and outputs of a human operator.** Models receive an objective and proceed by analyzing a screenshot at each step, subsequently generating the next mouse or keyboard action.

### Key Features
- **Compatibility**: Designed for various multimodal models.
- **Integration**: Currently integrated with **GPT-4v** as the default model.
- **Future Plans**: Support for additional models.

### Current Challenges
> **Note:** The GPT-4v's error rate in estimating XY mouse click locations is currently quite high. This framework aims to track the progress of multimodal models over time, aspiring to achieve human-level performance in computer operation.

### Ongoing Development
At [HyperwriteAI](https://www.hyperwriteai.com/), we are developing a multimodal model with more accurate click location predictions.

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
6. **Run it**!
```
operate
```
7. **Final Step**: As a last step, the Terminal app will ask for permission for "Screen Recording" and "Accessibility" in the "Security & Privacy" page of Mac's "System Preferences".




### Other important notes
- This project is only compatible with MacOS as this time. 