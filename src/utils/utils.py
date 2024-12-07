import argparse
import yaml

def load_config(path: str) -> dict:
    """
    Loads the configuration from the given YAML file.
    :return: Parsed configuration as a dictionary.
    """
    with open(path, 'r') as file:
        config = yaml.safe_load(file)
        return config

def parse_program_args():
    parser = argparse.ArgumentParser(
        description="node.py --id <id> --host <host> --port <port> --epoch-duration <epoch-duration> --peers <peerss>"
    )
    parser.add_argument("--id", type=int, required=True, help="ID number for this node")
    parser.add_argument("--host", type=str, required=True, help="IP address for this node")
    parser.add_argument("--port", type=int, required=True, help="Port number for this node")
    parser.add_argument('--epoch-duration', type=int, required=True, help='Epoch duration in seconds')
    parser.add_argument("--seed", type=int, required=True, help="Seed for the leader election")
    parser.add_argument("--peers", nargs="*", required=True, help="List of peer ports")
    parser.add_argument("--start-time", type=str, required=False, help="Time for the node to start running")
    return parser.parse_args()
