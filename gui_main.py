#!/usr/bin/env python
"""
Self-Operating Computer GUI
"""
import sys
import os
import argparse
from PyQt5.QtWidgets import QApplication

# Add the root directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after setting path
from operate.config import Config
from operate.utils.style import ANSI_BRIGHT_MAGENTA
from gui import SOCChatWindow


def main_entry():
    """
    Main entry point for the Self-Operating Computer GUI
    """
    parser = argparse.ArgumentParser(
        description="Run the Self-Operating Computer GUI with a specified model."
    )
    parser.add_argument(
        "-m",
        "--model",
        help="Specify the default model to use",
        required=False,
        default="gpt-4-with-ocr",
    )

    # Add a flag for verbose mode
    parser.add_argument(
        "--verbose",
        help="Run with verbose logging",
        action="store_true",
    )

    # Allow for dark or light mode
    parser.add_argument(
        "--light",
        help="Use light mode instead of dark mode",
        action="store_true",
    )

    try:
        args = parser.parse_args()

        # Create Qt application
        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        # Apply dark mode palette unless light mode is requested
        if not args.light:
            from PyQt5.QtGui import QPalette, QColor
            from PyQt5.QtCore import Qt

            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)

        # Initialize configuration
        config = Config()
        config.verbose = args.verbose

        # Create and show the main window
        window = SOCChatWindow()

        # Set the default model based on command-line argument
        model_index = window.model_combo.findText(args.model)
        if model_index >= 0:
            window.model_combo.setCurrentIndex(model_index)

        # Set verbose checkbox based on command-line argument
        window.verbose_checkbox.setChecked(args.verbose)

        # Show the window
        window.show()

        # Run the application
        sys.exit(app.exec_())

    except KeyboardInterrupt:
        print(f"\n{ANSI_BRIGHT_MAGENTA}Exiting...")
    except Exception as e:
        print(f"Error starting GUI: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main_entry()