import os
from openai import OpenAI
from dotenv import load_dotenv

def setup_client():
    load_dotenv()
    # OpenAI API Key
    client = OpenAI()
    client.api_key = os.getenv("OPENAI_API_KEY")
    client.base_url = os.getenv("OPENAI_API_BASE_URL", client.base_url)
    return client