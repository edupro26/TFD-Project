import random
import socket
import time
from collections import deque

from domain.transaction import Transaction


# Dictionary to keep track of recent tx_ids
recent_tx_ids = {}

def generate_tx_id(sender: int) -> int:
    """
    Generate a unique, random tx_id for the given sender.
    """
    if sender not in recent_tx_ids:
        recent_tx_ids[sender] = deque(maxlen=1000)

    tx_id = random.randint(100000, 999999)
    while tx_id in recent_tx_ids[sender]:
        tx_id = random.randint(100000, 999999)

    recent_tx_ids[sender].append(tx_id)
    return tx_id

def run_workload(base_port: int, num_nodes: int):
    """
    Simulates the workload imposed by clients submitting
    transactions to the server nodes.
    :param base_port: the base port number
    :param num_nodes: the number of nodes
    """
    print("Starting workload...")
    # TODO Create workload threads in the future
    try:
        while True:
            sender = random.randint(1, 20)
            receiver = random.randint(1, 20)
            # Ensure sender and receiver are different
            while receiver == sender:
                receiver = random.randint(1, 20)
            tx_id = generate_tx_id(sender)
            amount = round(random.uniform(1, 1000), 2)

            transaction = Transaction(sender=sender, receiver=receiver, tx_id=tx_id, amount=amount)
            node_port = base_port + random.randint(0, num_nodes - 1)
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect(("localhost", node_port))
                    sock.sendall(b"TXN" + transaction.serialize())
            except Exception as e:
                print(f"Lost connection to node {node_port}: {e}")

            time.sleep(random.uniform(1, 5))
    except KeyboardInterrupt:
        print("\nWorkload interrupted. Exiting...")