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

def read_file(path: str) -> str:
    """
    Reads the content of a file.
    :param path: Path to the file.
    :return: The content of the file.
    """
    with open(path, 'r') as f:
        return f.read()

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
    return f"{label}: {" <- ".join(blocks_to_show)} ({len(chain)} blocks)"
