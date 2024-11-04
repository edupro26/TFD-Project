import time
from node import Node
from args import parse_args

def main():
    base_port = 8000
    host = "localhost"
    args = parse_args()
    epoch_duration = args.epoch_duration
    node_id = args.node_id
    total_nodes = args.total_nodes

    addresses = [(host, base_port + i) for i in range(total_nodes)]
    peers = addresses[:node_id] + addresses[node_id+1:] # skips address of the current node (removes self)
    node = Node(node_id, addresses[node_id], peers, epoch_duration)
    node.start()

    # keep the main thread alive to let the simulation run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping node...")
        node.stop()


if __name__ == '__main__':
    main()
