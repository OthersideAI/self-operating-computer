import os
from dotenv import load_dotenv
from openai import OpenAI

class Config:
    """
    Configuration class for managing settings.

    Attributes:
        debug (bool): Flag indicating whether debug mode is enabled.
        openai_api_key (str): API key for OpenAI.
        google_api_key (str): API key for Google.
        monitor_size (dict): Dictionary containing the width and height of the monitor.
    """

    def __init__(self):
        load_dotenv()
        self.debug = True
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.monitor_size = {
            "width": 1920,
            "height": 1080,
        }

    def initialize_openai_client(self):
        """
        Initializes and returns an OpenAI client with the configured API key.

        Returns:
            OpenAI or None: An instance of the OpenAI client if the API key is provided, else None.
        """
        if self.openai_api_key:
            client = OpenAI()
            client.api_key = self.openai_api_key
            client.base_url = os.getenv("OPENAI_API_BASE_URL", client.base_url)
            return client
        return None
