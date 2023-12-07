import os
import yaml
from pathlib import Path
from pydantic_settings import BaseSettings

ROOT_PATH: Path = Path(__file__).parent.parent.parent
""" The root path of the application which is typically the project repository root path. """

SRC_PATH: Path = ROOT_PATH / 'src'
""" The source path of the application which is typically the src directory within the ROOT_PATH. """

DEFAULT_ENV_PATH: Path = Path('./.env')
""" The default path to the environment file to load settings from. """

DEFAULT_SECRETS_PATH: Path | None = None
""" The default path to the secrets directory to load environment variable values from. """


class AppSettings(BaseSettings):
    """ The application settings class that loads setting values from the application environment. """

    accurate_mode: bool = False
    env_file: str = './.env'
    env_file_encoding: str = 'UTF-8'
    env_secrets_dir: str | None = None
    debug: bool = False
    openai_api_key: str | None = None
    openai_api_url: str = 'https://api.openai.com/v1'
    openai_model: str = 'gpt-4-vision-preview'
    root_path: str = str(ROOT_PATH)
    screen_height: int = 1080
    screen_width: int = 1920
    screenshot_directory: str = './screenshots'
    voice_mode: bool = False
    
    version: str = '0.1.0'
    """ The application version number """

    """ The following settings are automatically loaded at application startup. """

    config: dict | None = None
    """ Additional configuration settings loaded automatically from the given YAML configuration file (if any) """

    class Config:
        env_prefix = 'soc_'
        env_nested_delimiter = '__'


def load_settings(env_file_path: str | None = None, env_file_encoding: str | None = None,
                  secrets_path: str | None = None) -> AppSettings:
    """ Loads an AppSettings instance based on the given environment file and secrets directory. """

    # Extract the default environment file path from the environment if defined, otherwise use the default path
    if env_file_path is None:
        env_file_path = os.getenv('SOC_ENV_FILE', DEFAULT_ENV_PATH)

    # Extract the default environment file encoding from the environment if defined, otherwise use the default value
    if env_file_encoding is None:
        env_file_encoding = os.getenv('SOC_ENV_FILE_ENCODING', 'UTF-8')

    # Extract the default secrets directory path from the environment if defined, otherwise use the default path
    if secrets_path is None:
        secrets_path = os.getenv('SOC_ENV_SECRETS_DIR', DEFAULT_SECRETS_PATH)

    params: dict = {
        '_env_file': env_file_path,
        '_env_file_encoding': env_file_encoding,
    }

    os.putenv('SOC_ENV_FILE', str(env_file_path))
    os.putenv('SOC_ENV_FILE_ENCODING', env_file_encoding)

    if secrets_path is not None:
        valid: bool = True

        if not os.path.exists(secrets_path):
            valid = False
            print(f'The given path for the "--secrets-dir" option does not exist: {secrets_path}')
        elif not os.path.isdir(secrets_path):
            valid = False
            print(f'The given path for the "--secrets-dir" option is not a directory: {secrets_path}')

        if valid:
            params['_secrets_dir'] = secrets_path
            os.putenv('SOC_ENV_SECRETS_DIR', str(secrets_path))

    # Load base app configuration settings from the given environment file and the local environment
    app_settings = AppSettings(**params)

    return app_settings


# Load application settings from the environment and environment configuration files
settings: AppSettings = load_settings()
