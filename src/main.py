import time
from node import Node

def main():
    n_nodes = 5
    nodes = []
    base_port = 8000
    host = "localhost"

    addresses = [(host, base_port + i) for i in range(n_nodes)]

    for i, address in enumerate(addresses):
        peers = addresses[:i] + addresses[i+1:] # skips address of the current node (removes self)
        node = Node(i, address, peers)
        node.start()
        nodes.append(node)

    # keep the main thread alive to let the simulation run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping nodes...")
        for node in nodes:
            node.stop()

if __name__ == '__main__':
    main()
