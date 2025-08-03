#utils.config_loader.py

# Import libraries
import csv
from datetime import datetime
import os
import yaml

def load_config(filepath):
    """
    Load configuration from a YAML file.
    """
    abs_path = os.path.abspath(filepath)

    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"YAML config file not found at: {filepath}")

    try:
        with open(filepath, "r") as f:
            config = yaml.safe_load(f)
        return config
    except yaml.YAMLError as e:
        raise RuntimeError(f"Error parsing YAML file: {e}")
    

def log_model_params(yaml_dict, section_key, filename=None):
    """
    Log the model parameters (config.yaml) to the database.

    Args:
        yaml_dict (dict): The loaded YAML config.
        section_key (str): The keyword in the YAML dict.
    """
    params = yaml_dict.get(section_key, {}).copy()  # copy so original not modified
    params["run_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if filename is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{section_key}_parameters_{timestamp}.csv"

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["parameter", "value"])
        for key, value in params.items():
            writer.writerow([key, value])