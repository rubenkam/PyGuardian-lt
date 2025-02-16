import yaml
import os
import shutil


def load_config(config_path=None):
    if config_path is None:
        # First check if the file exists in the current working directory
        config_path = 'pipeguardian.yaml'
        if not os.path.isfile(config_path):
            # If not, fall back to the package's default configuration
            config_path = os.path.join(os.path.dirname(__file__), 'config', 'pipeguardian.yaml')
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file not found at {config_path}. Using default config.")
        return {"YAML": "Not found!"}  # Default config


def add_policy(custom_yaml_path):
    # Validate that the custom YAML file exists
    if not os.path.exists(custom_yaml_path):
        print(f"Error: The file '{custom_yaml_path}' does not exist.")
        return

    # Validate if the file is a YAML file
    if not custom_yaml_path.endswith(('.yaml', '.yml')):
        print(f"Error: The file '{custom_yaml_path}' is not a valid YAML file.")
        return

    # Target directory and file
    config_directory = os.path.join(os.path.dirname(__file__), 'config')
    os.makedirs(config_directory, exist_ok=True)  # Ensure the config directory exists
    destination_path = os.path.join(config_directory, 'pipeguardian.yaml')

    try:
        # Overwrite the existing pipeguardian.yaml with the custom YAML
        shutil.copy(custom_yaml_path, destination_path)
        print(f"Successfully added custom policy. The policy has been updated at '{destination_path}'")
    except Exception as e:
        print(f"Error: Could not overwrite the policy file. {e}")
