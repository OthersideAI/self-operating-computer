from setuptools import setup, find_packages

setup(
    name="self-operating-computer",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "operate=operate.main:main",
        ],
    },
    # include any other necessary setup options here
)
