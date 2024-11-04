import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="main.py --node-id <node-id> --epoch-duration <epoch-duration> --total-nodes <total-nodes>")
    parser.add_argument('--epoch-duration', type=int, default=2, help='Epoch duration in seconds')
    parser.add_argument('--node-id', type=int, help='Node id')
    parser.add_argument('--total-nodes', type=int, help='Total number of nodes')
    return parser.parse_args()