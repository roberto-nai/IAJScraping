# config_reader.py

import yaml
from pathlib import Path

def read_config_yaml(file_path=None) -> dict:
    """
    Reads a YAML configuration file and returns its contents as a dictionary.
    
    Parameters
    --------------
    file_path: str,
        optional path to the YAML file. If not provided, defaults to 'config.yml' in the script's directory.

    Returns
    --------------
    Dictionary containing the configuration data.
    """

    if file_path is None:
        # Defaults to config.yml in the same directory as this script
        file_path = Path(__file__).parent / "config.yml"
    
    try:
        with file_path.open('r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
        return None
    except yaml.YAMLError as exc:
        print(f"Error in parsing YAML file: {exc}")
        return None