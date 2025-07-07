import os
from setuptools import setup, find_packages

# Read the contents of your requirements.txt file
with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as f:
    required = f.read().splitlines()

# Read the contents of your README.md file for the project description
with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="self-ai-operating-computer",
    version="2.0.14",
    packages=find_packages(),
    install_requires=[
        "annotated-types==0.6.0",
        "anyio==3.7.1",
        "certifi==2025.6.15",
        "charset-normalizer==3.3.2",
        "colorama==0.4.6",
        "contourpy==1.2.0",
        "cycler==0.12.1",
        "distro==1.8.0",
        "EasyProcess==1.1",
        "entrypoint2==1.1",
        "exceptiongroup==1.1.3",
        "fonttools==4.44.0",
        "h11==0.14.0",
        "httpcore==1.0.2",
        "httpx>=0.25.2",
        "idna==3.4",
        "importlib-resources==6.1.1",
        "kiwisolver==1.4.5",
        "matplotlib==3.8.1",
        "MouseInfo==0.1.3",
        "mss==9.0.1",
        "numpy==1.26.1",
        "openai==1.2.3",
        "packaging==23.2",
        "Pillow==10.1.0",
        "prompt-toolkit==3.0.39",
        "PyAutoGUI==0.9.54",
        "pydantic==2.4.2",
        "pydantic_core==2.10.1",
        "PyGetWindow==0.0.9",
        "PyMsgBox==1.0.9",
        "pyparsing==3.1.1",
        "pyperclip==1.8.2",
        "PyRect==0.2.0",
        "pyscreenshot==3.1",
        "PyScreeze==0.1.29",
        "python3-xlib==0.15",
        "python-dateutil==2.8.2",
        "python-dotenv==1.0.0",
        "pytweening==1.0.7",
        "requests==2.31.0",
        "rubicon-objc==0.4.7",
        "six==1.16.0",
        "sniffio==1.3.0",
        "tqdm==4.66.1",
        "typing_extensions==4.8.0",
        "urllib3==2.0.7",
        "wcwidth==0.2.9",
        "zipp==3.17.0",
        "google-generativeai==0.3.0",
        "aiohttp==3.9.1",
        "ultralytics==8.0.227",
        "easyocr==1.7.1",
        "ollama==0.1.6",
        "anthropic",
    ],
    entry_points={
        "console_scripts": [
            "operate=operate.main:main_entry",
        ],
    },
    package_data={
        # Include the file in the operate.models.weights package
        "operate.models.weights": ["best.pt"],
    },
    long_description=long_description,  # Add project description here
    long_description_content_type="text/markdown",  # Specify Markdown format
    # include any other necessary setup options here
)
