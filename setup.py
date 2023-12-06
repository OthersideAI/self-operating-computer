from setuptools import setup, find_packages

# Read the contents of your requirements.txt file
with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="self-operating-computer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=required,  # Add dependencies here
    entry_points={
        "console_scripts": [
            "operate=operate.main:main_entry",
        ],
    },
    # include any other necessary setup options here
)
