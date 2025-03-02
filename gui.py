import sys
import os
import time
import threading
import asyncio
import platform
import json
import base64
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QComboBox, QCheckBox,
    QLabel, QScrollArea, QFrame, QSplitter, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon, QTextCursor, QColor, QPalette, QPixmap

# Import directly from local modules
from operate.models.prompts import USER_QUESTION, get_system_prompt
from operate.config import Config
from operate.models.apis import get_next_action
from operate.utils.screenshot import capture_screen_with_cursor
from operate.exceptions import ModelNotRecognizedException
from operate.operate import operate, get_scaling_factor

# Setup config
config = Config()

# Define available models - match the models in apis.py
AVAILABLE_MODELS = [
    "gpt-4-vision",
    "gpt-4-with-som",
    "gpt-4-with-ocr",
    "claude-3",
    "claude-3.7",
    "qwen-vl",
    "o1-with-ocr",
    "gemini-pro-vision",
    "llava"
]


class LogRedirector:
    """Redirects print output to the GUI log window"""

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

    def write(self, text):
        self.original_stdout.write(text)
        self.text_widget.append(text)
        # Auto-scroll to bottom
        self.text_widget.moveCursor(QTextCursor.End)

    def flush(self):
        self.original_stdout.flush()
        QApplication.processEvents()


class RecordButton(QPushButton):
    """Custom button for voice recording that changes appearance when pressed"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Hold to Record")
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 2px solid #c0c0c0;
                border-radius: 15px;
                padding: 8px;
                color: #404040;
            }
            QPushButton:checked {
                background-color: #ff4444;
                color: white;
                border: 2px solid #dd2222;
            }
        """)
        self.mic = None


class ScreenshotDisplay(QLabel):
    """Widget to display the current screenshot"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(200)
        self.setStyleSheet("background-color: #121212; border: 1px solid #333;")
        self.setText("No screenshot available")

    def update_screenshot(self, filename):
        if os.path.exists(filename):
            pixmap = QPixmap(filename)
            # Scale pixmap to fit widget while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.width(), self.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
        else:
            self.setText("Screenshot not found")

    def resizeEvent(self, event):
        # If we have a pixmap, rescale it when the widget is resized
        if hasattr(self, 'pixmap') and self.pixmap():
            scaled_pixmap = self.pixmap().scaled(
                self.width(), self.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
        super().resizeEvent(event)


class OperateThread(QThread):
    update_signal = pyqtSignal(str)
    completed_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    screenshot_signal = pyqtSignal(str)

    def __init__(self, model, objective, voice_mode=False, verbose_mode=False):
        super().__init__()
        self.model = model
        self.objective = objective
        self.voice_mode = voice_mode
        self.verbose_mode = verbose_mode
        self.running = True

    def run(self):
        try:
            config.verbose = self.verbose_mode
            config.validation(self.model, self.voice_mode)

            mic = None
            if self.voice_mode:
                try:
                    from whisper_mic import WhisperMic
                    mic = WhisperMic()
                    self.update_signal.emit("Voice recognition initialized.")
                except ImportError:
                    self.error_signal.emit(
                        "Voice mode requires 'whisper_mic' module. Install with 'pip install -r requirements-audio.txt'")
                    return

            system_prompt = get_system_prompt(self.model, self.objective)
            system_message = {"role": "system", "content": system_prompt}
            messages = [system_message]
            loop_count = 0
            session_id = None

            self.update_signal.emit(f"Starting task: {self.objective}")

            task_completed = False
            while not task_completed and self.running:
                if config.verbose:
                    self.update_signal.emit(f"[Self Operating Computer] loop_count {loop_count}")

                # Capture screenshot for UI
                screenshots_dir = "screenshots"
                if not os.path.exists(screenshots_dir):
                    os.makedirs(screenshots_dir)
                screenshot_filename = os.path.join(screenshots_dir, "screenshot.png")
                capture_screen_with_cursor(screenshot_filename)
                self.screenshot_signal.emit(screenshot_filename)

                # Get next action from the model
                operations, session_id = self.run_async(
                    get_next_action(self.model, messages, self.objective, session_id)
                )

                # Process the operations and update task_completed accordingly
                task_completed = operate(operations, session_id, self.model)

                loop_count += 1
                if loop_count > 10:
                    task_completed = True
                    self.update_signal.emit("[Self-Operating Computer] Max loop count reached. Task considered complete.")

            # If the thread was stopped by the user, we can check the running flag:
            if not self.running:
                self.update_signal.emit("Task stopped by the user.")
            else:
                self.update_signal.emit("Task completed.")
            self.completed_signal.emit()

        except Exception as e:
            self.error_signal.emit(f"Thread error: {str(e)}")

    def stop(self):
        self.running = False

    def run_async(self, coroutine):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coroutine)
        finally:
            loop.close()



class VoiceRecordingThread(QThread):
    finished_signal = pyqtSignal(str)

    def __init__(self, mic):
        super().__init__()
        self.mic = mic

    def run(self):
        try:
            # Call listen() without a stop_flag since it's not supported
            result = self.mic.listen()
            self.finished_signal.emit(result)
        except Exception as e:
            self.finished_signal.emit(f"Error: {str(e)}")

class MessageWidget(QFrame):
    """Widget to display a single message in the chat view"""

    def __init__(self, text, is_user=False, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(
            "background-color: #c8c8c8; border-radius: 10px; margin: 5px;" if is_user else
            "background-color: #d0d0d0; border-radius: 10px; margin: 5px;"
        )

        layout = QVBoxLayout(self)

        # Add a label for the sender
        sender = QLabel("You:" if is_user else "System:")
        sender.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(sender)

        # Add the message text
        message = QLabel(text)
        message.setWordWrap(True)
        message.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(message)

        self.setLayout(layout)



class SOCChatWindow(QMainWindow):
    """Main chat window for the Self-Operating Computer interface"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Self-Operating Computer")
        self.setMinimumSize(1000, 700)

        # Initialize mic to None
        self.mic = None
        self.operate_thread = None

        self.init_ui()

        # Try to initialize whisper_mic if available
        try:
            from whisper_mic import WhisperMic
            self.mic = WhisperMic()
            self.record_button.setEnabled(True)
        except ImportError:
            self.record_button.setEnabled(False)
            self.record_button.setToolTip("Install whisper_mic module to use voice")

    def init_ui(self):
        """Initialize the user interface"""
        # Create the central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Settings bar at the top
        settings_layout = QHBoxLayout()

        # Model selection dropdown
        model_label = QLabel("Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(AVAILABLE_MODELS)
        self.model_combo.setCurrentIndex(
            AVAILABLE_MODELS.index("gpt-4-with-ocr") if "gpt-4-with-ocr" in AVAILABLE_MODELS else 0)

        # Verbose mode checkbox
        self.verbose_checkbox = QCheckBox("Verbose Logs")

        # Add widgets to settings layout
        settings_layout.addWidget(model_label)
        settings_layout.addWidget(self.model_combo)
        settings_layout.addWidget(self.verbose_checkbox)
        settings_layout.addStretch(1)

        # Add settings to main layout
        main_layout.addLayout(settings_layout)

        # Create a horizontal splitter for screenshot and chat views
        h_splitter = QSplitter(Qt.Horizontal)

        # Left panel - Screenshot view
        screenshot_container = QWidget()
        screenshot_layout = QVBoxLayout(screenshot_container)

        # Screenshot label
        screenshot_label = QLabel("Screen Preview:")
        screenshot_layout.addWidget(screenshot_label)

        # Screenshot display
        self.screenshot_display = ScreenshotDisplay()
        screenshot_layout.addWidget(self.screenshot_display)

        h_splitter.addWidget(screenshot_container)

        # Right panel - Chat view and log
        chat_log_splitter = QSplitter(Qt.Vertical)

        # Chat view area (top part of right panel)
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)

        # Create the scrollable chat view
        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_content = QWidget()
        self.chat_content_layout = QVBoxLayout(self.chat_content)
        self.chat_content_layout.addStretch(1)  # Push messages to the top

        self.chat_scroll_area.setWidget(self.chat_content)
        chat_layout.addWidget(self.chat_scroll_area)

        # Input area
        input_layout = QHBoxLayout()

        # Text input field
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type your request here...")
        self.text_input.returnPressed.connect(self.send_message)

        # Record button
        self.record_button = RecordButton()
        self.record_button.pressed.connect(self.start_recording)
        self.record_button.released.connect(self.stop_recording)

        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        # **New Stop button**
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_task)

        # Add widgets to input layout
        input_layout.addWidget(self.text_input)
        input_layout.addWidget(self.record_button)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.stop_button)  # Add the Stop button

        # Add input area to chat layout
        chat_layout.addLayout(input_layout)

        # Log view (bottom part of right panel)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("font-family: Consolas, monospace; background-color: #222; color: #ddd;")

        # Add chat view and log view to the chat_log_splitter
        chat_log_splitter.addWidget(chat_container)
        chat_log_splitter.addWidget(self.log_view)
        chat_log_splitter.setStretchFactor(0, 3)  # Give chat view more space
        chat_log_splitter.setStretchFactor(1, 2)

        # Add chat_log_splitter to the right side of h_splitter
        h_splitter.addWidget(chat_log_splitter)
        h_splitter.setStretchFactor(0, 1)  # Screenshot area
        h_splitter.setStretchFactor(1, 2)  # Chat + log area

        # Add h_splitter to main layout
        main_layout.addWidget(h_splitter)

        # Add progress indicator at the bottom (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Set the central widget
        self.setCentralWidget(central_widget)

        # Redirect stdout to the log view
        self.log_redirector = LogRedirector(self.log_view)
        sys.stdout = self.log_redirector
        sys.stderr = self.log_redirector

        # Add a welcome message to the chat
        self.add_message("Welcome to Self-Operating Computer! What would you like done?", is_user=False)

        # Set focus to the text input
        self.text_input.setFocus()

        # Check for screenshots directory and display the latest screenshot if available
        screenshots_dir = "screenshots"
        if os.path.exists(screenshots_dir):
            screenshot_files = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
            if screenshot_files:
                latest_screenshot = os.path.join(screenshots_dir, sorted(screenshot_files)[-1])
                self.screenshot_display.update_screenshot(latest_screenshot)

    def add_message(self, text, is_user=True):
        """Add a message to the chat view"""
        message_widget = MessageWidget(text, is_user)
        self.chat_content_layout.insertWidget(self.chat_content_layout.count() - 1, message_widget)

        # Scroll to the bottom to show the new message
        self.chat_scroll_area.verticalScrollBar().setValue(
            self.chat_scroll_area.verticalScrollBar().maximum()
        )

    def send_message(self):
        """Send a message and start processing the task"""
        text = self.text_input.text().strip()
        if not text:
            return

        # Add the message to the chat view
        self.add_message(text, is_user=True)
        self.text_input.clear()

        # Start processing in a separate thread
        self.process_task(text)

    def process_task(self, objective):
        """Process a task in a separate thread"""
        # Disable input while processing
        self.text_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.record_button.setEnabled(False)
        self.model_combo.setEnabled(False)
        self.verbose_checkbox.setEnabled(False)

        # Show progress indicator
        self.progress_bar.setVisible(True)

        # Get selected model and verbose setting
        model = self.model_combo.currentText()
        verbose = self.verbose_checkbox.isChecked()

        # Create and start the thread
        self.operate_thread = OperateThread(model, objective, False, verbose)
        self.operate_thread.update_signal.connect(self.update_log)
        self.operate_thread.completed_signal.connect(self.task_completed)
        self.operate_thread.error_signal.connect(self.handle_error)
        self.operate_thread.screenshot_signal.connect(self.update_screenshot)
        self.operate_thread.start()

    @pyqtSlot()
    def stop_task(self):
        if self.operate_thread is not None and self.operate_thread.isRunning():
            self.operate_thread.stop()  # Signal the thread to stop
            self.operate_thread.wait()  # Wait for it to finish
            self.add_message("Task stopped by the user.", is_user=False)

            # Re-enable input and hide progress indicator
            self.text_input.setEnabled(True)
            self.send_button.setEnabled(True)
            self.record_button.setEnabled(True)
            self.model_combo.setEnabled(True)
            self.verbose_checkbox.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.text_input.setFocus()

    @pyqtSlot(str)
    def update_log(self, text):
        """Update the log view with new text"""
        print(text)

    @pyqtSlot(str)
    def update_screenshot(self, filename):
        """Update the screenshot display with the latest screenshot"""
        self.screenshot_display.update_screenshot(filename)

    @pyqtSlot()
    def task_completed(self):
        """Handle task completion"""
        # Add completion message to chat
        self.add_message("Task completed! What would you like to do next?", is_user=False)

        # Re-enable input
        self.text_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.verbose_checkbox.setEnabled(True)
        if self.mic:
            self.record_button.setEnabled(True)

        # Hide progress indicator
        self.progress_bar.setVisible(False)

        # Set focus back to text input
        self.text_input.setFocus()

    @pyqtSlot(str)
    def handle_error(self, error_text):
        """Handle errors from the operate thread"""
        print(f"ERROR: {error_text}")
        self.add_message(f"An error occurred: {error_text}", is_user=False)

        # Re-enable input
        self.text_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.verbose_checkbox.setEnabled(True)
        if self.mic:
            self.record_button.setEnabled(True)

        # Hide progress indicator
        self.progress_bar.setVisible(False)

        # Set focus back to text input
        self.text_input.setFocus()

    def start_recording(self):
        """Start voice recording"""
        if not self.mic:
            return

        self.record_thread = VoiceRecordingThread(self.mic)
        self.record_thread.finished_signal.connect(self.process_voice_result)
        self.record_thread.start()

    def stop_recording(self):
        """Stop voice recording gracefully."""
        if hasattr(self, 'record_thread') and self.record_thread.isRunning():
            self.record_thread.stop()  # signal the thread to stop
            self.record_thread.wait(2000)  # wait up to 2 seconds for the thread to finish

    @pyqtSlot(str)
    def process_voice_result(self, result):
        """Process the result from voice recognition"""
        if result.startswith("Error:"):
            QMessageBox.warning(self, "Voice Recognition Error", result)
            return

        # Set the recognized text to the input field and send it
        self.text_input.setText(result)
        self.send_message()

    def closeEvent(self, event):
        """Handle window close event"""
        # Stop any running thread
        if self.operate_thread and self.operate_thread.isRunning():
            self.operate_thread.stop()
            self.operate_thread.wait()

        # Restore stdout and stderr
        sys.stdout = self.log_redirector.original_stdout
        sys.stderr = self.log_redirector.original_stderr

        event.accept()