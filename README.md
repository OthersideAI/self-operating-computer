## Self-Operating Computer Framework

This framework enables multimodal models to operate a computer, replicating the inputs and outputs of a human operator. Models receive an objective and proceed by analyzing a screenshot at each step, subsequently generating the next mouse or keyboard action.

Designed for compatibility with various multimodal models, the project currently integrates with GPT-4v as its default model. We plan to add support for additional models in the future.


It's worth noting that the GPT-4v's error rate in estimating XY mouse click locations is currently quite high. By establishing this framework, our aim is to track the progress of multimodal models over time, with the ultimate goal of achieving human-level performance in computer operation.

At [HyperwriteAI](https://www.hyperwriteai.com/), we are developing a multimodal model that promises more accurate click location predictions.

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