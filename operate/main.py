"""
Self-Operating Computer
"""
import argparse
from operate.dialogs import main

def main_entry():
    parser = argparse.ArgumentParser(
        description="Run the self-operating-computer with a specified model."
    )
    parser.add_argument(
        "-m",
        "--model",
        help="Specify the model to use",
        required=False,
        default="gpt-4-vision-preview",
    )

    args = parser.parse_args()
    main(args.model)


if __name__ == "__main__":
    main_entry()
    
