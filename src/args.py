import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="node.py --id <id> --epoch-duration <epoch-duration> --port <port> --peers <peerss>"
    )
    parser.add_argument("--id", type=int, required=True, help="ID number for this node")
    parser.add_argument('--epoch-duration', type=int, default=2, help='Epoch duration in seconds')
    parser.add_argument("--port", type=int, required=True, help="Port number for this node")
    parser.add_argument("--peers", nargs="*", default=[], help="List of peer ports")
    return parser.parse_args()