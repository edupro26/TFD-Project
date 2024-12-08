import random
import socket
import threading
import time
import hashlib

from collections import deque
from domain.blockchain import BlockChain
from domain.transaction import Transaction
from domain.block import Block
from domain.message import Message, MessageType
from domain.state import State
from utils.utils import *

class Node:
    def __init__(
        self,
        id: int,
        host: str,
        port: int,
        peers: list[tuple[str, int]],
        epoch_duration: int,
        seed: int,
        start_time: str,
        confusion_start: int,
        confusion_duration: int
    ):
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
        self.seed = seed
        self.start_time = start_time
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.peer_sockets = {}
        self.pending_tx = []
        self.current_leader = 0
        self.current_epoch = 1
        self.blockchain = BlockChain(self.id, len(self.peers) + 1) # initialize the blockchain
        self.received_messages = deque(maxlen=200) # avoid processing the same message multiple times
        self.state = State.WAITING
        self.confusion_start = confusion_start
        self.confusion_duration = confusion_duration
        self.queue = deque()
        self.running = True

    def start(self):
        """
        Starts the node
        """
        self.wait_start_time()
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(len(self.peers))
        for peer in self.peers:
            self.connect_to_peer(peer)
        print(f"Node {self.id} started on {self.host}:{self.port}")
        threading.Thread(target=self.start_server, daemon=True).start()
        
    def stop(self):
        """
        Stops the node
        """
        self.server_socket.close()
        for socket in self.peer_sockets.values():
            if socket is not None:
                socket.close()

    def start_server(self):
        """
        Starts the server socket and listens for incoming connections
        """
        if self.state == State.RECOVERED:
            print("Initiated node recovery")
            self.current_epoch = self.deduce_current_epoch()

        threading.Thread(target=self.generate_tx).start()
        threading.Thread(target=self.run_protocol).start()
        threading.Thread(target=self.process_messages).start()
        threading.Thread(target=self.reconnect_peers).start()
        while True:
            try:
                client_socket, address = self.server_socket.accept()
                threading.Thread(target=self.handle_connection, args=(client_socket,)).start()
            except socket.error:
                break

    def process_messages(self):
        """
        Processes messages from the queue
        During the confusion period, buffer messages without processing them
        After the confusion period, process buffered messages in sequence
        """
        while self.running:
            if len(self.queue) > 0:
                if self.in_confusion_period():
                    # buffer messages during the confusion period 
                    time.sleep(0.1)
                else:
                    # process buffered messages after the confusion period
                    while self.queue:
                        msg = self.queue.popleft()
                        self.handle_message(msg)


    def connect_to_peer(self, peer: tuple[str, int]):
        """
        Establishes a connection to a single peer and adds it to the connection pool
        """
        peer_socket = None
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            peer_socket.connect(peer)
            self.peer_sockets[peer] = peer_socket
        except socket.error:
            peer_socket.close()
            self.peer_sockets[peer] = None

    def reconnect_peers(self):
        """
        Tries to reconnect to all peers
        """
        while self.running:
            for peer in self.peers:
                if self.peer_sockets[peer] is None:
                    self.connect_to_peer(peer)
                    if self.peer_sockets[peer] is not None:
                        print(f"Reconnected to peer {peer}")
            time.sleep(self.epoch_duration / 2)

    def generate_tx(self):
        """
        Simulates clients submitting transactions to this node
        """
        while True:
            sender = random.randint(1, 1000)
            receiver = random.randint(1, 1000)
            amount = random.uniform(0.01, 1000)
            # ensure sender and receiver are different
            while receiver == sender:
                receiver = random.randint(1, 1000)

            # generate a unique tx id
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
            while True:
                bytes = client_socket.recv(4)
                length = int.from_bytes(bytes, byteorder='big')
        
                data = client_socket.recv(length)
                if message := Message.deserialize(data):
                    self.queue.append(message)
        except EOFError:
            pass
        except socket.error as e:
            print(f"Error receiving data from {client_socket.getpeername()}")
        finally:
            client_socket.close()

    def urb_broadcast(self, message: Message):
        """
        URB-broadcasts a message to all peers
        """
        if self.state != State.RUNNING:
            return

        for peer, peer_socket in self.peer_sockets.items():
            try:
                if peer_socket is not None:
                    serialized = message.serialize()
                    length = len(serialized).to_bytes(4, byteorder='big')
                    peer_socket.sendall(length + serialized)
            except socket.error:
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
            vote_message = Message(MessageType.VOTE, block, self.id) # vote for the block
            self.urb_broadcast(vote_message)

    def handle_block_vote(self, message: Message):
        """
        Logic for handling a vote message
        @param message: the message containing the vote
        """
        block = message.content
        self.blockchain.add_vote(block, message.sender)

    def run_protocol(self):
        """
        Main logic of the node containing the protocol
        """
        print(f"Node {self.id} running protocol")
        while True:
            start_time = time.time()
            self.syncronize_epoch()

            print(f"------------------- Epoch {self.current_epoch} -------------------")
            
            if self.in_confusion_period():
                print("############# IN CONFUSION PERIOD #############")
            
            self.current_leader = self.elect_leader() # elect the new leader of the epoch
            if self.current_leader == self.id: # if this node is the leader
                self.run_leader_phase()

            # wait for the epoch duration
            elapsed_time = time.time() - start_time
            time.sleep(max(0, self.epoch_duration - elapsed_time))
            self.blockchain.update_finalization()
            self.state = self.next_state()
            
            self.current_epoch += 1

            print(f"Leader: Node {self.current_leader}")
            print(self.blockchain)

    def run_leader_phase(self):
        """
        Runs the leader phase by proposing a new block and broadcasting it
        During confusion periods, blocks are proposed independently of notarization
        """
       
        # find the head of the longest notarized chain
        parent_block = max(
            self.blockchain.not_finalized_blocks.values(),
            key=lambda block: block.length if self.blockchain.check_notarization(block) else 0,
            default=None
        )
        if parent_block is None:
            print("No notarized chain found.")
            return

        # propose new block
        previous_hash = parent_block.hash()
        new_block = Block(
            previous_hash=previous_hash,
            epoch=self.current_epoch,
            length=parent_block.length + 1,
            transactions=self.pending_tx.copy()
        )
        # clear the pending transactions
        self.pending_tx.clear()

        # broadcast the proposed block
        print(f"Node {self.id} proposing block: {new_block}")
        propose_message = Message(MessageType.PROPOSE, new_block, self.id)
        self.urb_broadcast(propose_message)

    def elect_leader(self) -> int:
        """
        Elects the leader of the current epoch
        """
        if self.in_confusion_period():
            return self.current_epoch % (len(self.peers) + 1)
        else:
            random.seed(self.seed + self.current_epoch)
            return random.randint(0, len(self.peers))

    def wait_start_time(self):
        """
        Waits for time to start
        """
        start_time_obj = get_time(self.start_time)
        start_time = start_time_obj.timestamp()
        current_time = time.time()

        # detect if it is a recovery after a crash
        if current_time > start_time:
            self.state = State.RECOVERED
            return

        print("Starting at", start_time_obj)
        time_to_wait = max(0, int(start_time - current_time)) # ensure time is not negative
        time.sleep(time_to_wait)
        self.state = State.RUNNING

    def in_confusion_period(self) -> bool:
        if self.confusion_duration == 0:
            return False
        return self.confusion_start <= self.current_epoch < self.confusion_start + self.confusion_duration

    def deduce_current_epoch(self):
        """
        Deduces the current epoch based on the current time and the start time
        """
        current_time = time.time()
        start_time = get_time(self.start_time).timestamp()
        return int((current_time - start_time) / self.epoch_duration) + 1
    
    def syncronize_epoch(self):
        next_epoch = self.deduce_current_epoch()
        # calculate the time to wait until the next epoch
        current_time = time.time()
        start_time = get_time(self.start_time).timestamp()
        time_to_wait = max(0, int(start_time + next_epoch * self.epoch_duration - current_time))
        time.sleep(time_to_wait)

    def next_state(self) -> State:
        """
        Determines the next state of the node
        """
        if self.state == State.RECOVERED:
            # check if has seen 3 consecutive notarized blocks
            notarized = len(self.blockchain.get_notarized_blocks())
            if notarized >= 3:
                print("Recovered node has seen 3 notarized blocks, starting protocol normally...")
                return State.RUNNING

        return self.state

if __name__ == "__main__":
    args = parse_program_args()
    id = args.id
    config = load_config("../config.yaml")
    nodes = config['nodes']
    host, port = next((p['ip'], p['port']) for p in nodes if p['id'] == id)
    peers = [(n['ip'], n['port']) for n in nodes if n['id'] != id]
    epoch_duration = config['epoch_duration']
    seed = config['seed']
    confusion_start = int(config['confusion_start'])
    confusion_duration = int(config['confusion_duration'])
    start_time = read_file('../start_time.txt')
    node = Node(id, host, port, peers, epoch_duration, seed, start_time, confusion_start, confusion_duration)
    node.start()

    # keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down node...")
        node.stop()
