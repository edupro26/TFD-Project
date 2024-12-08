import random
import socket
import threading
import time
import hashlib
from collections import deque
from queue import Queue
from domain.blockchain import BlockChain
from domain.transaction import Transaction
from domain.block import Block
from domain.message import Message, MessageType
from domain.state import State
from utils.utils import *


class Node:
    def __init__(self, id: int, host: str, port: int, peers: list[tuple[str, int]], epoch_duration: int, seed: int, start_time: str):
        """
        Initializes a new node
        @param id: the id of the node
        @param host: the host of the node
        @param port: the port of the node
        @param peers: the list of neighboring nodes
        @param epoch_duration: the duration of an epoch in seconds
        @param seed: the seed for the leader election
        """
        self.id = id
        self.host = host
        self.port = port
        self.peers = peers
        self.epoch_duration = epoch_duration
        self.random = random.Random(seed)
        self.start_time = start_time
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peer_sockets = {}
        self.pending_tx = []
        self.running = False
        self.current_leader = 0
        self.current_epoch = 1
        self.blockchain = BlockChain(self.id, len(self.peers) + 1) # initialize the blockchain
        self.received_messages = deque(maxlen=200) # avoid processing the same message multiple times
        self.state = State.WAITING
        # self.msg_queue = Queue()

    def start(self):
        """
        Starts the node
        """
        self.wait_start_time()
        self.running = True
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(len(self.peers))
        for peer in self.peers:
            self.connect_to_peer(peer)
        threading.Thread(target=self.start_server, daemon=True).start()

    def stop(self):
        """
        Stops the node
        """
        self.running = False
        self.server_socket.close()
        for socket in self.peer_sockets.values():
            if socket is not None:
                socket.close()

    def start_server(self):
        """
        Starts the server socket and listens for incoming connections
        """
        print(f"Node {self.id} started on {self.host}:{self.port}")
        threading.Thread(target=self.generate_tx).start()
        threading.Thread(target=self.run_protocol).start()
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                threading.Thread(target=self.handle_connection, args=(client_socket,)).start()
            except socket.error:
                break

    def connect_to_peer(self, peer: tuple[str, int]):
        """
        Establishes a connection to a single peer and adds it to the connection pool.
        """
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            peer_socket.connect(peer)
            self.peer_sockets[peer] = peer_socket
        except socket.error:
            self.peer_sockets[peer] = None

    def generate_tx(self):
        """
        Simulates clients submitting transactions to this node.
        """
        while self.running:
            sender = random.randint(1, 1000)
            receiver = random.randint(1, 1000)
            amount = random.uniform(0.01, 1000)
            # Ensure sender and receiver are different
            while receiver == sender:
                receiver = random.randint(1, 1000)

            # Generate a unique tx ID
            nonce = random.randint(0, 1000000)
            id = hashlib.sha1(f"{sender}{nonce}".encode()).hexdigest()

            self.pending_tx.append(Transaction(sender, receiver, int(id, 16), amount))
            time.sleep(self.epoch_duration / 2)

    def handle_connection(self, client_socket: socket.socket):
        """
        Handles a connection established with this node
        :param client_socket: the socket connected to the client
        """
        try:
            while self.running:
                bytes = client_socket.recv(4)
                length = int.from_bytes(bytes, byteorder='big')
        
                data = client_socket.recv(length)
                if message := Message.deserialize(data):
                    self.handle_message(message)
                    # TODO check if in confusion epoch
        except EOFError:
            pass
        except socket.error as e:
            print(f"Node {self.id}: error listening to peers: {e} - while running? {self.running}")
        finally:
            client_socket.close()

    def urb_broadcast(self, message: Message):
        """
        URB-broadcasts a message to all peers
        """
        for peer, peer_socket in self.peer_sockets.items():
            try:
                if peer_socket is not None:
                    serialized = message.serialize()
                    length = len(serialized).to_bytes(4, byteorder='big')
                    peer_socket.sendall(length + serialized)
            except socket.error:
                self.peer_sockets[peer].close()
                self.peer_sockets[peer] = None

    def handle_message(self, message: Message):
        """
        Logic for handling a message
        @param message: the message to handle
        """
        if message.type == MessageType.ECHO:
            echo = message.content
            if echo.hash() not in self.received_messages:
                self.received_messages.append(echo.hash())
                if echo.type == MessageType.PROPOSE:
                    self.handle_block_proposal(echo)
                elif echo.type == MessageType.VOTE:
                    self.handle_block_vote(echo)
        else:
            if message.hash() not in self.received_messages:
                self.received_messages.append(message.hash())
                self.urb_broadcast(Message(MessageType.ECHO, message, self.id))
                if message.type == MessageType.PROPOSE:
                    self.handle_block_proposal(message)
                elif message.type == MessageType.VOTE:
                    self.handle_block_vote(message)

    def handle_block_proposal(self, message: Message):
        """
        Logic for handling a block proposal message
        @param message: the message containing the block proposal
        """
        block = message.content
        # check if block extends the longest notarized chain, otherwise ignore it
        if block.length > self.blockchain.length():
            self.blockchain.add_block(block)
            # vote for the block
            vote_message = Message(MessageType.VOTE, block, self.id)
            self.urb_broadcast(vote_message)

    def handle_block_vote(self, message: Message):
        """
        Logic for handling a vote message
        @param message: the message containing the vote
        """
        self.blockchain.add_vote(message.content, message.sender)

    def run_protocol(self):
        """
        Main logic of the node containing the protocol
        """
        print(f"Node {self.id} running protocol")
        while self.running:
            start_time = time.time()

            print(f"------------------- Epoch {self.current_epoch} -------------------")
            
            self.elect_leader() # elect the new leader of the epoch
            if self.current_leader == self.id: # if this node is the leader
                self.run_leader_phase()

            # wait for the epoch duration
            elapsed_time = time.time() - start_time
            time.sleep(self.epoch_duration - elapsed_time)
            self.current_epoch += 1
            self.blockchain.update_finalization()

            print(f"Leader: Node {self.current_leader}")
            print(self.blockchain)

    def run_leader_phase(self):
        """
        Runs the leader phase by proposing a new block and broadcasting it
        """
        # propose new block
        previous_block = self.blockchain[-1]
        previous_hash = previous_block.hash()
        new_block = Block(
            previous_hash=previous_hash,
            epoch=self.current_epoch,
            length=self.blockchain.length() + 1,
            transactions=self.pending_tx.copy()
        )
        # clear the pending transactions
        self.pending_tx.clear()

        # broadcast the proposed block
        propose_message = Message(MessageType.PROPOSE, new_block, self.id)
        self.urb_broadcast(propose_message)

    def elect_leader(self):
        """
        Elects the leader of the current epoch
        """
        self.current_leader = self.random.randint(0, len(self.peers))

    def wait_start_time(self):
        """
        Waits for time to start
        """
        start_time_obj = get_time(self.start_time)
        start_time = start_time_obj.timestamp()
        current_time = time.time()

        if current_time > start_time: # if time has passed, start immediately because we are late
            self.state = State.RECOVERED # recovered after crash
            print("Recovered after crash, starting immediately...")
            # TODO: recover state
            return

        print("Starting at", start_time_obj)
        time_to_wait = max(0, int(start_time - current_time)) # ensure time is not negative
        time.sleep(time_to_wait)
        print("Starting node...")
        self.state = State.RUNNING

if __name__ == "__main__":
    args = parse_program_args()
    id = args.id
    config = load_config("../config.yaml")
    nodes = config['nodes']
    host, port = next((p['ip'], p['port']) for p in nodes if p['id'] == id)
    peers = [(n['ip'], n['port']) for n in nodes if n['id'] != id]
    epoch_duration = config['epoch_duration']
    seed = config['seed']
    start_time = config['start_time']
    node = Node(id, host, port, peers, epoch_duration, seed, start_time)
    node.start()

    # keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down node...")
        node.stop()
