import hashlib
from socket import socket

from typing import List
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
        self.current_Leader = 0

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
        
        
    def compute_hash(self, epoch: int) -> str:
        """
        @param epoch: epoch number
        Descobrir o lider da epoch baseado numa VRF (Verifiable Random Function) - ou seja é "random" mas é verificável
        Junta o lider atual com o epoch e faz hash disso
        """
        input_str = f"{self.current_Leader}-{epoch}"  # Concatenate node ID and epoch as the input
        hash_value = hashlib.sha256(input_str.encode()).hexdigest()  # Compute the SHA-256 hash
        return hash_value
    
    
    # TODO saber se é preciso precaver contra o caso do leader ter crashado
    def get_leader(self, epoch: int, nodes: List['Node']) -> 'Node':
        """
        @param epoch: epoch number
        @param nodes: list of nodes
        Obter o lider da epoch
        """
        hash = self.compute_hash(epoch)
        leader_id = int(hash, 16) % len(nodes)
        return nodes[leader_id]