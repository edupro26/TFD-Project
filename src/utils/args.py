import argparse

def workloads_args():
    parser = argparse.ArgumentParser(description="workload.py --base-port <base-port> --num-nodes <num-nodes>")
    parser.add_argument("--base-port", type=int, required=True, help="Base port number for the nodes")
    parser.add_argument("--num-nodes", type=int, required=True, help="Number of nodes")
    return parser.parse_args()

def parse_program_args():
    parser = argparse.ArgumentParser(
        description="node.py --id <id> --epoch-duration <epoch-duration> --port <port> --peers <peerss>"
    )
    parser.add_argument("--id", type=int, required=True, help="ID number for this node")
    parser.add_argument('--epoch-duration', type=int, default=2, help='Epoch duration in seconds')
    parser.add_argument("--port", type=int, required=True, help="Port number for this node")
    parser.add_argument("--peers", nargs="*", default=[], help="List of peer ports")
    return parser.parse_args()

def get_command_line_args() -> tuple[int, int]:
    num_nodes = int(input("Enter the number of nodes: "))
    if num_nodes < 3:
        raise ValueError("Invalid number of nodes. Must be at least 3.")

    epoch_duration = int(input("Enter the epoch duration: "))
    if epoch_duration < 1:
        raise ValueError("Invalid epoch duration. Must be at least 1.")
    
    return num_nodes, epoch_duration