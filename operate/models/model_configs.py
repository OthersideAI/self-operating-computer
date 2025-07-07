# operate/models/model_configs.py

# A centralized registry for all supported models.
# This file simplifies adding, removing, and managing models across the application.
#
# Each model is defined with the following properties:
# - 'api_key': The environment variable for the required API key.
# - 'provider': The service provider (e.g., 'openai', 'google', 'ollama').
# - 'display_name': The name shown in the interactive model selection menu.
#
# This centralized approach avoids hardcoding model names and their configurations
# in multiple places, making the codebase cleaner and more maintainable.

MODELS = {
    # OpenAI Models
    "gpt-4o": {"api_key": "OPENAI_API_KEY", "provider": "openai", "display_name": "OpenAI GPT-4o (Default)"},
    "gpt-4-with-ocr": {"api_key": "OPENAI_API_KEY", "provider": "openai", "display_name": "OpenAI GPT-4 with OCR"},
    "gpt-4.1": {"api_key": "OPENAI_API_KEY", "provider": "openai", "display_name": "OpenAI GPT-4.1"},
    "gpt-4.1-mini": {"api_key": "OPENAI_API_KEY", "provider": "openai", "display_name": "OpenAI GPT-4.1 mini"},
    "gpt-4.1-nano": {"api_key": "OPENAI_API_KEY", "provider": "openai", "display_name": "OpenAI GPT-4.1 nano"},
    "o1-with-ocr": {"api_key": "OPENAI_API_KEY", "provider": "openai", "display_name": "OpenAI o1 with OCR"},
    "o3": {"api_key": "OPENAI_API_KEY", "provider": "openai", "display_name": "OpenAI o3"},
    "o4-mini": {"api_key": "OPENAI_API_KEY", "provider": "openai", "display_name": "OpenAI o4-mini"},
    "gpt-4-with-som": {"api_key": "OPENAI_API_KEY", "provider": "openai", "display_name": "OpenAI GPT-4 with Set-of-Mark Prompting"},

    # Google Models
    "gemini-1.5-pro-latest": {"api_key": "GOOGLE_API_KEY", "provider": "google", "display_name": "Google Gemini 1.5 Pro (latest)"},
    "gemini-2.5-pro": {"api_key": "GOOGLE_API_KEY", "provider": "google", "display_name": "Google Gemini 2.5 Pro"},
    "gemini-2.5-flash": {"api_key": "GOOGLE_API_KEY", "provider": "google", "display_name": "Google Gemini 2.5 Flash"},

    # Anthropic Models
    "claude-3": {"api_key": "ANTHROPIC_API_KEY", "provider": "anthropic", "display_name": "Anthropic Claude 3"},

    # Qwen Models
    "qwen-vl": {"api_key": "QWEN_API_KEY", "provider": "qwen", "display_name": "Qwen-VL"},

    # Ollama Models
    "llava": {"api_key": "OLLAMA_HOST", "provider": "ollama", "display_name": "LLaVa (via Ollama)"},
    "gemma3n": {"api_key": "OLLAMA_HOST", "provider": "ollama", "display_name": "Gemma 3n (via Ollama)"},
    "gemma3n:e2b": {"api_key": "OLLAMA_HOST", "provider": "ollama", "display_name": "Gemma 3n:e2b (via Ollama)"},
    "gemma3n:e4b": {"api_key": "OLLAMA_HOST", "provider": "ollama", "display_name": "Gemma 3n:e4b (via Ollama)"},
    "gemma3:12b": {"api_key": "OLLAMA_HOST", "provider": "ollama", "display_name": "Gemma 3:12b (via Ollama)"},
    "gemma3:4b": {"api_key": "OLLAMA_HOST", "provider": "ollama", "display_name": "Gemma 3:4b (via Ollama)"},
    "qwen2.5vl:3b": {"api_key": "OLLAMA_HOST", "provider": "ollama", "display_name": "Qwen 2.5 VL 3B (via Ollama)"}
}