## Self-Operating Computer Framework

**This framework enables multimodal models to operate a computer, replicating the inputs and outputs of a human operator.** Models receive an objective and proceed by analyzing a screenshot at each step, subsequently generating the next mouse or keyboard action.

### Key Features
- **Compatibility**: Designed for various multimodal models.
- **Integration**: Currently integrated with **GPT-4v** as the default model.
- **Future Plans**: Support for additional models.

### Current Challenges
> **Note:** The GPT-4v's error rate in estimating XY mouse click locations is currently quite high. This framework aims to track the progress of multimodal models over time, aspiring to achieve human-level performance in computer operation.

### Ongoing Development
At [HyperwriteAI](https://www.hyperwriteai.com/), we are developing a multimodal model with more accurate click location predictions.

### Instructions
Create virtual environment. 
```
python3 -m venv venv
```
Activate it
```
source venv/bin/activate
```
Install requirements. 
```
pip install -r requirements.txt
```
Install Project and Command-Line Interface.
```
pip install .
```
Run it!
```
operate
```
Lastly
- Make sure to give permissions to the Terminal app in for both "Screen Recording" and "Accessibility" in the "Security & Privacy" page of "System Preferences". 


### Other important notes
- This project is only compatible with MacOS as this time. 