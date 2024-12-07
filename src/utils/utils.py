import argparse
import yaml
from datetime import datetime

def load_config(path: str) -> dict:
    """
    Loads the configuration from the given YAML file.
    :return: Parsed configuration as a dictionary.
    """
    with open(path, 'r') as file:
        return yaml.safe_load(file)

def parse_program_args():
    parser = argparse.ArgumentParser(
        description="node.py --id <id>"
    )
    parser.add_argument("--id", type=int, required=True, help="ID number for this node")
    return parser.parse_args()


def get_time(time: str) -> datetime:
    now = datetime.now()
    return datetime.strptime(time, '%H:%M:%S').replace(
        year=now.year, month=now.month, day=now.day
    )