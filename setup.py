from setuptools import setup, find_packages

# Read the contents of your requirements.txt file
with open("requirements.txt") as f:
    required = f.read().splitlines()

# Read the contents of your README.md file for the project description
with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="self-operating-computer",
    version="1.0.8",
    packages=find_packages(),
    install_requires=required,  # Add dependencies here
    entry_points={
        "console_scripts": [
            "operate=operate.main:main_entry",
        ],
    },
    long_description=long_description,  # Add project description here
    long_description_content_type="text/markdown",  # Specify Markdown format
    # include any other necessary setup options here
)
