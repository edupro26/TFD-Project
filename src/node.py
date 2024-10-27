from socket import socket

from src.block import Block
from src.message import Message, MessageType
from src.transaction import Transaction


class Node:
    def __init__(self, id: int, port: int):
        self.id = id
        self.blockchain = []
        self.unconfirmed_tx = []
        self.current_epoch = 0
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        self.socket.bind(('localhost', self.port))
        print(f'Node {self.id} started on port {self.port}')

    def listen(self):
        # TODO
        pass

    def propose_block(self):
        # TODO
        pass

    def vote_block(self, block: Block):
        # TODO
        pass

    def broadcast_message(self, message: Message):
        # TODO
        pass

    def receive_message(self, message: Message):
        # TODO
        pass

    def add_transaction(self, transaction: Transaction):
        self.unconfirmed_tx.append(transaction)