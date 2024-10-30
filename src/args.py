import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="main.py --node-id <node-id> --epoch-delay <epoch-delay> --total-nodes <total-nodes>")
    parser.add_argument('--epoch-delay', type=int, default=1, help='Delay between epochs')
    parser.add_argument('--node-id', type=int, help='Node id')
    parser.add_argument('--total-nodes', type=int, help='Total number of nodes')
    return parser.parse_args()