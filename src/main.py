import time
import multiprocessing
import subprocess
import os
import sys
from node import Node

def run_node(node_id, address, peers):  # Now outside main()
    """Function to run a single node process."""
    node = Node(node_id, address, peers)
    node.start()


def main():
    n_nodes = 5
    nodes = []
    base_port = 8000
    host = "localhost"

    addresses = [(host, base_port + i) for i in range(n_nodes)]
    processes = []

    #TODO not sure se isto funciona no linux
    for i, address in enumerate(addresses):
        peers = addresses[:i] + addresses[i+1:] # skips address of the current node (removes self)
        command = [sys.executable, "-c", f"import sys; from node import Node; node = Node({i}, ('{host}', {address[1]}), {peers}); node.start()", ]
        process = subprocess.Popen(command,creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0, cwd=os.path.dirname(os.path.abspath(__file__)))
        processes.append(process)

    # keep the main thread alive to let the simulation run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping nodes...")
        for process in processes:
            process.terminate()  # send a termination signal
            process.wait()       # wait for the process to complete


if __name__ == '__main__':
    main()
