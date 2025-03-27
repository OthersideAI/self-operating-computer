"""
Self-Operating Computer
"""
import argparse
from operate.utils.style import ANSI_BRIGHT_MAGENTA
from operate.operate import main


def main_entry():
    parser = argparse.ArgumentParser(
        description="Run the self-operating-computer with a specified model."
    )
    parser.add_argument(
        "-m",
        "--model",
        help="Specify the model to use",
        required=False,
        default="gpt-4-with-ocr",
    )

    # Add a voice flag
    parser.add_argument(
        "--voice",
        help="Use voice input mode",
        action="store_true",
    )
    
    # Add a flag for verbose mode
    parser.add_argument(
        "--verbose",
        help="Run operate in verbose mode",
        action="store_true",
    )
    
    # Allow for direct input of prompt
    parser.add_argument(
        "--prompt",
        help="Directly input the objective prompt",
        type=str,
        required=False,
    )
    
    # Add OCR flag for Ollama models
    parser.add_argument(
        "--ocr",
        help="Enable OCR for Ollama models",
        action="store_true",
    )
    
    # Add browser preference flag
    parser.add_argument(
        "-b",
        "--browser",
        help="Specify preferred browser (default: Google Chrome)",
        type=str,
        default="Google Chrome",
    )

    try:
        args = parser.parse_args()
        
        # No need to prompt for model name if it's directly specified
        # The Ollama model name can now be passed directly

        main(
            args.model,
            terminal_prompt=args.prompt,
            voice_mode=args.voice,
            verbose_mode=args.verbose,
            ocr_mode=args.ocr,
            browser=args.browser
        )
    except KeyboardInterrupt:
        print(f"\n{ANSI_BRIGHT_MAGENTA}Exiting...")


if __name__ == "__main__":
    main_entry()
