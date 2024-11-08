import socket
import time

from domain.message import Message, MessageType
from domain.transaction import Transaction

BASE_PORT = 8000

def run_workload():
    print("Running workload...")

    # Wait for the nodes to start
    time.sleep(2)

    # TODO
    #  Create a loop that generates random transactions
    #  Send the transactions to the nodes randomly

    # This is a test transaction
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(("localhost", BASE_PORT))
    tx1 = Transaction(sender=3, receiver=5, tx_id=1111, amount=100)
    sock1.sendall(b"TXN" + tx1.serialize())
    sock1.close()

    # This is another test transaction
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.connect(("localhost", BASE_PORT + 1))
    tx2 = Transaction(sender=2, receiver=6, tx_id=2222, amount=200)
    sock2.sendall(b"TXN" + tx2.serialize())
    sock2.close()
