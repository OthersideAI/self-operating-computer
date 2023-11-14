## Self-Operating Computer
A framework for a multimodal model to output key and mouse commands to control a computer to accomplish objectives.

This is an experimental project which currently lets GPT-4v decide on XY mouse click locations. The error rate is still quite high but we expect this to change rapidly. HyperwriteAI [https://www.hyperwriteai.com/] is working on a multimodal model with more accurate click locations. 

We think multimodal models will achieve beyond human performance at operating computers in the next 5 years and we'd like to setup a framework project to track this progress. 

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