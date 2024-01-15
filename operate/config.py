import os
from dotenv import load_dotenv
from openai import OpenAI
import sys


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

    def initialize_apis(self):
        """
            Initializes and returns an OpenAI client with the configured API key.

        Returns:
                OpenAI or None: An instance of the OpenAI client if the API key is provided, else None.
        """
        try:
            if self.openai_api_key:
                client = OpenAI()
                print("setting openai key")
                client.api_key = self.openai_api_key
                client.base_url = os.getenv("OPENAI_API_BASE_URL", client.base_url)
                return client
            return "Failed to initialize OpenAI"
        except Exception as e:
            print("[Config] Failed to initialize OpenAI", e)
            return "Failed to initialize OpenAI"

    def validation(self, model, voice_mode):
        """
        Validate the input parameters for the dialog operation.

        Args:
            model (str): The model to be used for the dialog operation.
            voice_mode (bool): Flag indicating whether to use voice mode.

        Raises:
            SystemExit: If the input parameters are invalid.

        """
        print("[validation]")
        print("[validation] self.openai_api_key", self.openai_api_key)

        if voice_mode and not self.openai_api_key:
            print("To use voice mode, please add an OpenAI API key")
            sys.exit(1)

        if model == "gpt-4" and not self.openai_api_key:
            print("To use `gpt-4-vision-preview` add an OpenAI API key")
            sys.exit(1)

        if model == "gemini-pro-vision" and not self.google_api_key:
            print("To use `gemini-pro-vision` add a Google API key")
            sys.exit(1)
