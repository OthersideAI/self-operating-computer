import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from prompt_toolkit.shortcuts import input_dialog
import google.generativeai as genai


class Config:
    """
    Configuration class for managing settings.

    Attributes:
        verbose (bool): Flag indicating whether verbose mode is enabled.
        openai_api_key (str): API key for OpenAI.
        google_api_key (str): API key for Google.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            # Put any initialization here
        return cls._instance

    def __init__(self):
        load_dotenv()
        self.verbose = False
        self.openai_api_key = (
            None  # instance variables are backups in case saving to a `.env` fails
        )
        self.google_api_key = (
            None  # instance variables are backups in case saving to a `.env` fails
        )

    def initialize_openai(self):
        if self.verbose:
            print("[Config][initialize_openai]")

        if self.openai_api_key:
            if self.verbose:
                print("[Config][initialize_openai] using cached openai_api_key")
            api_key = self.openai_api_key
        else:
            if self.verbose:
                print(
                    "[Config][initialize_openai] no cached openai_api_key, try to get from env."
                )
            api_key = os.getenv("OPENAI_API_KEY")

        client = OpenAI(
            api_key=api_key,
        )
        client.api_key = api_key
        client.base_url = os.getenv("OPENAI_API_BASE_URL", client.base_url)
        return client

    def initialize_google(self):
        if self.google_api_key:
            if self.verbose:
                print("[Config][initialize_google] using cached google_api_key")
            api_key = self.google_api_key
        else:
            if self.verbose:
                print(
                    "[Config][initialize_google] no cached google_api_key, try to get from env."
                )
            api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key, transport="rest")
        model = genai.GenerativeModel("gemini-pro-vision")

        return model

    def validation(self, model, voice_mode):
        """
        Validate the input parameters for the dialog operation.
        """
        self.require_api_key(
            "OPENAI_API_KEY",
            "OpenAI API key",
            model == "gpt-4"
            or voice_mode
            or model == "gpt-4-with-som"
            or model == "gpt-4-with-ocr",
        )
        self.require_api_key(
            "GOOGLE_API_KEY", "Google API key", model == "gemini-pro-vision"
        )

    def require_api_key(self, key_name, key_description, is_required):
        key_exists = bool(os.environ.get(key_name))
        if self.verbose:
            print("[Config] require_api_key")
            print("[Config] key_name", key_name)
            print("[Config] key_description", key_description)
            print("[Config] key_exists", key_exists)
        if is_required and not key_exists:
            self.prompt_and_save_api_key(key_name, key_description)

    def prompt_and_save_api_key(self, key_name, key_description):
        key_value = input_dialog(
            title="API Key Required", text=f"Please enter your {key_description}:"
        ).run()

        if key_value is None:  # User pressed cancel or closed the dialog
            sys.exit("Operation cancelled by user.")

        if key_value:
            if key_name == "OPENAI_API_KEY":
                self.openai_api_key = key_value
            elif key_name == "GOOGLE_API_KEY":
                self.google_api_key = key_value
            self.save_api_key_to_env(key_name, key_value)
            load_dotenv()  # Reload environment variables
            # Update the instance attribute with the new key

    @staticmethod
    def save_api_key_to_env(key_name, key_value):
        with open(".env", "a") as file:
            file.write(f"\n{key_name}='{key_value}'")
