import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from prompt_toolkit.shortcuts import input_dialog


class Config:
    """
    Configuration class for managing settings.

    Attributes:
        debug (bool): Flag indicating whether debug mode is enabled.
        openai_api_key (str): API key for OpenAI.
        google_api_key (str): API key for Google.
    """

    def __init__(self):
        load_dotenv()
        self.verbose = True
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")

    def initialize_openai(self):
        print("[initialize_openai]")
        print("[initialize_openai] self.openai_api_key", self.openai_api_key)
        if self.openai_api_key:
            client = OpenAI()
            print("[initialize_openai] client = OpenAI()")
            client.api_key = self.openai_api_key
            print("[initialize_openai] client.api_key", client.api_key)
            client.base_url = os.getenv("OPENAI_API_BASE_URL", client.base_url)
            return client
        return None

    def validation(self, model, voice_mode):
        """
        Validate the input parameters for the dialog operation.
        """
        self.require_api_key(
            "OPENAI_API_KEY", "OpenAI API key", model == "gpt-4" or voice_mode
        )
        self.require_api_key(
            "GOOGLE_API_KEY", "Google API key", model == "gemini-pro-vision"
        )

    def require_api_key(self, key_name, key_description, is_required):
        if is_required and not getattr(self, key_name.lower()):
            self.prompt_and_save_api_key(key_name, key_description)

    def prompt_and_save_api_key(self, key_name, key_description):
        key_value = input_dialog(
            title="API Key Required", text=f"Please enter your {key_description}:"
        ).run()
        print("[prompt_and_save_api_key]")
        print("[prompt_and_save_api_key] key_value", key_value)

        if key_value is None:  # User pressed cancel or closed the dialog
            sys.exit("Operation cancelled by user.")

        if key_value:
            self.save_api_key_to_env(key_name, key_value)
            load_dotenv()  # Reload environment variables
            # Update the instance attribute with the new key
            print("[prompt_and_save_api_key] key_name", key_name)
            print("[prompt_and_save_api_key] key_value", key_value)

            if key_value:
                self.save_api_key_to_env(key_name, key_value)
                load_dotenv()  # Reload environment variables
                setattr(self, key_name.lower(), key_value)
            print("[prompt_and_save_api_key] self.openai_api_key ", self.openai_api_key)
            print("[prompt_and_save_api_key] self.google_api_key ", self.google_api_key)

    @staticmethod
    def save_api_key_to_env(key_name, key_value):
        print("[save_api_key_to_env]")
        print("[save_api_key_to_env] key_name", key_name)
        print("[save_api_key_to_env] key_value", key_value)
        with open(".env", "a") as file:
            file.write(f"\n{key_name}='{key_value}'")
