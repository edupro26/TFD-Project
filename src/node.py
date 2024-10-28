import socket
import threading
import hashlib
from block import Block
from message import Message, MessageType
from transaction import Transaction

class Node:
    def __init__(self, id: int, address: tuple[str, int], peers: list[tuple[str, int]]):
        """
        @param id: node id
        @param address: address of the node (host, port)
        @param peers: list of addresses of the peers [(host, port)]
        """
        self.id = id
        self.host, self.port = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.current_epoch = 0
        self.current_leader = 0
        self.blockchain = []
        self.pending_tx = []
        self.peers = peers
        self.running = False
        self.socket.bind((self.host, self.port)) # bind the socket to the address

    def start(self):
        """
        Starts the node thread
        """
        self.running = True
        threading.Thread(target=self.listen_to_peers).start() # start the listening thread
        threading.Thread(target=self.run_protocol).start() # start the main protocol thread
        print(f"Node {self.id} started on port {self.port}")

    def stop(self):
        """
        Stops the node's threads
        """
        self.running = False
        self.socket.close()

    def listen_to_peers(self):
        """
        Listens to the peers for incoming messages
        """
        while self.running:
            data, addr = self.socket.recvfrom(4096) # receive data from the socket
            threading.Thread(target=self.handle_connection, args=(data, addr), daemon=True).start() # handle connection in a new thread

    def handle_connection(self, data: bytes, addr: tuple[str, int]):
        """
        Handles incoming connections
        @param data: incoming data
        @param addr: address of the sender (host, port)
        """
        try:
            message = Message.deserialize(data)
            self.handle_message(message)
        except Exception as e:
            print(f"Node {self.id}: error handling connection from {addr}: {e}")

    def send_message(self, message: Message, recipient: tuple[str, int]):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(recipient)
            sock.sendall(message.serialize())
        except Exception as e:
            print(f"Node {self.id}: error sending message to {recipient}: {e}")
        finally:
            sock.close()

    def broadcast_message(self, message: Message):
        for peer in self.peers:
            self.send_message(message, peer)

    def handle_message(self, message):
        if message.type != Message.ECHO:
            echo_message = Message(MessageType.ECHO, message, self.id)
            self.broadcast_message(echo_message) # urb broadcast

        if message.type == Message.PROPOSE:
            self.propose_block(message)
        elif message.type == Message.VOTE:
            self.vote_block(message)
        elif message.type == Message.ECHO:
            self.handle_message(message.content)

    def receive_message(self, message: Message):
        # TODO
        pass

    def propose_block(self):
        # TODO
        pass

    def vote_block(self, block: Block):
        # TODO
        pass

    def check_finalization(self):
        # TODO
        pass

    def run_protocol(self):
        while self.running:
            # TODO
            # determine if this node is the leader of the currect epoch using get_leader
            # if so, run leader phase
            # then, wait for epoch duration to finish
            pass

    def leader_phase(self):
        # TODO
        # propose a block
        pass
        
    def add_transaction(self, transaction: Transaction):
        self.pending_tx.append(transaction)

    def compute_hash(self, epoch: int) -> str:
        """
        @param epoch: epoch number
        Determine the leader of the epoch based on a VRF (Verifiable Random Function) - it is "random" but verifiable
        Concatenate the current leader with the epoch and hash it
        """
        input_str = f"{self.current_leader}-{epoch}"  # Concatenate node ID and epoch as the input
        hash_value = hashlib.sha1(input_str.encode()).hexdigest()  # Compute the SHA-1 hash
        return hash_value

    # TODO saber se é preciso precaver contra o caso do leader ter crashado
    def get_leader(self, epoch: int, nodes: list['Node']) -> 'Node':
        """
        @param epoch: epoch number
        @param nodes: list of nodes
        Obtain the leader of the epoch based on the hash of the epoch
        """
        hash = self.compute_hash(epoch)
        leader_id = int(hash, 16) % len(nodes)
        return nodes[leader_id]