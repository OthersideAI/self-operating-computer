import os
import sys

import google.generativeai as genai
from dotenv import load_dotenv
from ollama import Client
from openai import OpenAI
import anthropic
from prompt_toolkit.shortcuts import input_dialog


class Config:
    """
    Configuration class for managing settings.

    Attributes:
        verbose (bool): Flag indicating whether verbose mode is enabled.
        openai_api_key (str): API key for OpenAI.
        google_api_key (str): API key for Google.
        ollama_host (str): url to ollama running remotely.
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
        self.ollama_host = (
            None  # instance variables are backups in case saving to a `.env` fails
        )
        self.ollama_api_key = (
            None  # instance variables are backups for Ollama Cloud API
        )
        self.anthropic_api_key = (
            None  # instance variables are backups in case saving to a `.env` fails
        )
        self.qwen_api_key = (
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

    def initialize_qwen(self):
        if self.verbose:
            print("[Config][initialize_qwen]")

        if self.qwen_api_key:
            if self.verbose:
                print("[Config][initialize_qwen] using cached qwen_api_key")
            api_key = self.qwen_api_key
        else:
            if self.verbose:
                print(
                    "[Config][initialize_qwen] no cached qwen_api_key, try to get from env."
                )
            api_key = os.getenv("QWEN_API_KEY")

        client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        client.api_key = api_key
        client.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
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

    def initialize_ollama(self):
        if self.ollama_host:
            if self.verbose:
                print("[Config][initialize_ollama] using cached ollama host")
        else:
            if self.verbose:
                print(
                    "[Config][initialize_ollama] no cached ollama host. Assuming ollama running locally."
                )
            self.ollama_host = os.getenv("OLLAMA_HOST", None)

        client_kwargs = {}
        ollama_api_key = self.ollama_api_key or os.getenv("OLLAMA_API_KEY")
        if ollama_api_key and self.ollama_host and "ollama.com" in str(self.ollama_host):
            client_kwargs["headers"] = {
                "Authorization": f"Bearer {ollama_api_key}"
            }

        model = Client(host=self.ollama_host, **client_kwargs)
        return model

    def initialize_ollama_cloud(self):
        if self.verbose:
            print("[Config][initialize_ollama_cloud]")

        if self.ollama_api_key:
            if self.verbose:
                print("[Config][initialize_ollama_cloud] using cached ollama_api_key")
            api_key = self.ollama_api_key
        else:
            if self.verbose:
                print(
                    "[Config][initialize_ollama_cloud] no cached key, try to get from env."
                )
            api_key = os.getenv("OLLAMA_API_KEY")

        host = os.getenv("OLLAMA_HOST", "https://ollama.com")
        if not host or "127.0.0.1" in host or "localhost" in host:
            host = "https://ollama.com"

        client = Client(
            host=host,
            headers={"Authorization": f"Bearer {api_key}"},
        )
        return client
    def initialize_anthropic(self):
        if self.anthropic_api_key:
            api_key = self.anthropic_api_key
        else:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        return anthropic.Anthropic(api_key=api_key)

    def is_ollama_cloud_model(self, model):
        if not model:
            return False
        model = str(model)
        aliases = {
            "ollama-cloud",
            "ollama-cloud-api",
            "ollama-cloud-llava",
            "ollama-cloud-gemma",
            "ollama-cloud-gemma4",
        }
        if model in aliases:
            return True
        if model.startswith("ollama-cloud") or model.startswith("ollama:"):
            return True
        # Direct Ollama Cloud model names such as "gemma4:31b" are cloud
        # models when an explicit cloud marker is present, or when the value
        # contains an Ollama-style "name:tag" reference and is not a known
        # local-only alias.
        if ":" in model and not model.lower().startswith(("gpt", "claude", "gemini")):
            return True
        return False

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
            or model == "gpt-4-with-ocr"
            or model == "gpt-4.1-with-ocr"
            or model == "o1-with-ocr",
        )
        self.require_api_key(
            "GOOGLE_API_KEY", "Google API key", model == "gemini-pro-vision"
        )
        self.require_api_key(
            "ANTHROPIC_API_KEY", "Anthropic API key", model == "claude-3"
        )
        self.require_api_key("QWEN_API_KEY", "Qwen API key", model == "qwen-vl")
        self.require_api_key(
            "OLLAMA_API_KEY", "Ollama API key", self.is_ollama_cloud_model(model)
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
            elif key_name == "ANTHROPIC_API_KEY":
                self.anthropic_api_key = key_value
            elif key_name == "QWEN_API_KEY":
                self.qwen_api_key = key_value
            elif key_name == "OLLAMA_API_KEY":
                self.ollama_api_key = key_value
            self.save_api_key_to_env(key_name, key_value)
            load_dotenv()  # Reload environment variables
            # Update the instance attribute with the new key

    @staticmethod
    def save_api_key_to_env(key_name, key_value):
        with open(".env", "a") as file:
            file.write(f"\n{key_name}='{key_value}'")
