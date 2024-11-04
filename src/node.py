import socket
import threading
import hashlib
import time
from block import Block
from message import Message, MessageType
from transaction import Transaction

class Node:
    def __init__(self, id: int, address: tuple[str, int], peers: list[tuple[str, int]], epoch_duration: int):
        """
        @param id: node id
        @param address: address of the node (host, port)
        @param peers: list of addresses of the peers [(host, port)]
        """
        self.id = id
        self.host, self.port = address
        self.epoch_duration = epoch_duration
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.current_epoch = 0
        self.current_leader = 0
        self.blockchain = []
        self.pending_tx = []
        self.votes = {}
        self.notarized_blocks = set()
        self.peers = peers
        self.running = False
        self.socket.bind((self.host, self.port)) # bind the socket to the address

    def start(self):
        """
        Starts the node thread
        """
        self.running = True
        self.listen_thread = threading.Thread(target=self.listen_to_peers, daemon=True)
        self.listen_thread.start() # start the listening thread
        print(f"Node {self.id} started on port {self.port}")        
        try: # in case we stop a node using keyboard interrupt
            self.run_protocol() 
        except KeyboardInterrupt:
            self.stop()

        # threading.Thread(target=self.listen_to_peers).start() # start the listening thread
        # threading.Thread(target=self.run_protocol).start() # start the main protocol thread

    def stop(self):
        """
        Stops the node
        """
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except OSError: # if the socket is already closed
            pass
        self.socket.close()
        self.running = False

    def listen_to_peers(self):
        """
        Listens to the peers for incoming messages
        """
        while self.running:
            try:
                data, addr = self.socket.recvfrom(4096) # receive data from the socket
                threading.Thread(target=self.handle_connection, args=(data, addr), daemon=True).start() # handle connection in a new thread
            except OSError as e:
                print(f"Node {self.id}: error listening to peers: {e} - while running? {self.running}")
                break

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
        """
        Sends a message to a recipient
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(recipient)
            sock.sendall(message.serialize())
        except Exception as e:
            print(f"Node {self.id}: error sending message to {recipient}: {e}")
        finally:
            sock.close()

    def broadcast_message(self, message: Message):
        """
        Broadcasts a message to all peers
        """
        for peer in self.peers:
            self.send_message(message, peer)

    def handle_message(self, message: Message):
        """
        Logic for handling a message
        """
        if message.type != Message.ECHO:
            echo_message = Message(MessageType.ECHO, message, self.id)
            self.broadcast_message(echo_message) # urb broadcast

        if message.type == Message.PROPOSE:
            self.handle_block_proposal(message)
        elif message.type == Message.VOTE:
            self.handle_vote(message)
        elif message.type == Message.ECHO:
            self.handle_message(message.content)

   
    def handle_block_proposal(self, message: Message):
        """
        Logic for handling a block proposal message
        """
        block = message.content
        # check if block extends the longest notarized chain, otherwise ignore it
        if block.length > len(self.blockchain):
            self.blockchain.append(block)
            # vote for the block
            vote_message = Message(MessageType.VOTE, block, self.id)
            self.broadcast_message(vote_message)
            

    def handle_vote(self, message: Message):
        """
        Logic for handling a vote message
        """
        block = message.content
        block_hash = block.compute_hash()
        if block_hash not in self.votes:
            self.votes[block_hash] = set()
        self.votes[block_hash].add(message.sender)

        # check notarization
        if len(self.votes[block_hash]) > len(self.peers) / 2:
            if block_hash not in self.notarized_blocks:
                self.notarized_blocks.add(block_hash)
                # check for finalization
                self.check_finalization()
            

    def check_finalization(self):
        # TODO
        pass

    def run_protocol(self):
        """
        Main logic of the node containing the protocol
        """
        while self.running:
            print(f"Node {self.id} running protocol")
            start_time = time.time()
            self.elect_leader() # elect the new leader of the epoch
            if self.current_leader == self.id: # if this node is the leader
                self.run_leader_phase()

            # wait for the epoch duration
            elapsed_time = time.time() - start_time
            time.sleep(self.epoch_duration - elapsed_time)
            self.current_epoch += 1            

    def leader_phase(self):
        """
        Runs the leader phase by proposing a new block and broadcasting it
        """
        # propose new block
        previous_block = self.blockchain[-1]
        previous_hash = previous_block.compute_hash()
        new_block = Block(
            previous_hash = previous_hash,
            epoch = self.current_epoch,
            length = len(self.blockchain),
            transactions = self.pending_tx.copy()
        )
        # clear the pending transactions
        self.pending_tx.clear()

        # broadcast the proposed block
        propose_message = Message(MessageType.PROPOSE, new_block, self.id)
        self.broadcast_message(propose_message)
        
    def add_transaction(self, transaction: Transaction):
        """
        Adds a transaction to the pending transactions list
        """
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
    def elect_leader(self, epoch: int, nodes: list['Node']):
        """
        @param epoch: epoch number
        @param nodes: list of nodes
        Elects the new leader of the epoch based on the hash of the epoch
        """
        hash = self.compute_hash(epoch)
        self.current_leader = int(hash, 16) % len(nodes)
        