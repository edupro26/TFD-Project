import argparse
import yaml
from datetime import datetime, timedelta

def load_config(path: str) -> dict:
    """
    Loads the configuration from the given YAML file.
    :return: Parsed configuration as a dictionary.
    """
    with open(path, 'r') as file:
        return yaml.safe_load(file)
    
def set_config(path: str, config: dict, to_add: dict):
    """
    Updates the configuration file with the given properties
    @param path: the path to the configuration file
    @param config: the configuration to be updated
    @param to_add: the properties to be added to the configuration
    """
    config.update(to_add)
    with open(path, 'w') as file:
        yaml.dump(config, file)

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

def get_time_plus(time: datetime, seconds: int) -> datetime:
    return time + timedelta(seconds=seconds)

def parse_chain(chain, label):
    max_blocks = 5
    few_blocks = len(chain) < max_blocks
    blocks = [str(b) for b in chain]
    blocks_to_show = blocks if few_blocks else ["...", *blocks[-max_blocks+1:]]
    return f"{label}: {" <- ".join(blocks_to_show)}"