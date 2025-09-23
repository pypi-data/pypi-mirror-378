import os
from typing import Any, Dict

from dotenv import load_dotenv
from ms_agent.config.env import Env
from ms_agent.tools.exa import ExaSearch
from ms_agent.tools.search.arxiv import ArxivSearch
from ms_agent.tools.search.search_base import SearchEngineType
from ms_agent.tools.search.serpapi import SerpApiSearch
from ms_agent.utils.logger import get_logger

logger = get_logger()


def get_search_config(config_file: str):
    config_file = os.path.abspath(os.path.expanduser(config_file))
    config = load_base_config(config_file)
    search_config = config.get('SEARCH_ENGINE', {})
    return search_config


def load_base_config(file_path: str) -> Dict[str, Any]:
    """
    Load the base configuration from a YAML file.

    Args:
        file_path (str): Path to the YAML configuration file.

    Returns:
        Dict[str, Any]: The loaded configuration as a dictionary.
    """
    if not os.path.exists(file_path):
        logger.warning(
            f'Config file {file_path} does not exist. Using default config (ArxivSearch).'
        )
        return {}

    import yaml
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)

    # Load environment variables from .env file if it exists
    if not load_dotenv(os.path.join(os.getcwd(), '.env')):
        Env.load_env()

    return process_dict(config)


def process_dict(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively process dictionary to replace environment variables.

    Args:
        config (Dict[str, Any]): The configuration dictionary to process.

    Returns:
        Dict[str, Any]: The processed configuration dictionary with environment variables replaced.
    """
    if not config:
        return {}

    result = {}
    for key, value in config.items():
        if isinstance(value, dict):
            result[key] = process_dict(value)
        elif isinstance(value, str):
            result[key] = replace_env_vars(value)
        else:
            result[key] = value
    return result


def replace_env_vars(value: str) -> str:
    """
    Replace environment variables in string values.

    Args:
        value (str): The string potentially containing environment variables.
    Returns:
        str: The string with environment variables replaced.
    """
    if not isinstance(value, str):
        return value

    if value.startswith('$'):
        env_var = value[1:]
        return os.getenv(env_var, None)

    return value


def get_web_search_tool(config_file: str):
    """
    Get the web search tool based on the configuration.

    Returns:
        SearchEngine: An instance of the SearchEngine class configured with the API key.
    """
    search_config = get_search_config(config_file=config_file)

    if search_config.get('engine', '') == SearchEngineType.EXA.value:
        return ExaSearch(
            api_key=search_config.get('exa_api_key',
                                      os.getenv('EXA_API_KEY', None)))
    elif search_config.get('engine', '') == SearchEngineType.SERPAPI.value:
        return SerpApiSearch(
            api_key=search_config.get('serpapi_api_key',
                                      os.getenv('SERPAPI_API_KEY', None)),
            provider=search_config.get('provider', 'google').lower())
    elif search_config.get('engine', '') == SearchEngineType.ARXIV.value:
        return ArxivSearch()
    else:
        return ArxivSearch()
