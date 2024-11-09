import socket
import threading
import time
import hashlib
from collections import deque

from domain.blockchain import BlockChain
from domain.transaction import Transaction
from utils.args import parse_program_args
from domain.block import Block
from domain.message import Message, MessageType


class Node:
    def __init__(self, host: str, port: int, id: int, peers: list[int], epoch_duration: int):
        """
        Initializes a new node
        @param host: the host of the node
        @param port: the port of the node
        @param id: the id of the node
        @param peers: the list of neighboring nodes
        @param epoch_duration: the duration of an epoch in seconds
        """
        self.host = host
        self.port = port
        self.id = id
        self.peers = [(self.host, int(p)) for p in peers]
        self.running = False
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pending_tx = []
        self.current_leader = 0
        self.current_epoch = 0

        self.epoch_duration = epoch_duration
        self.blockchain = BlockChain(self.id, len(self.peers) + 1) # initialize the blockchain
        self.received_messages = deque(maxlen=200) # avoid processing the same message multiple times

    def start(self):
        """
        Starts the node
        """
        self.running = True
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        server_thread.start()

    def stop(self):
        """
        Stops the node
        """
        self.running = False
        self.server_socket.close()

    def start_server(self):
        """
        Starts the server socket and listens for incoming connections
        """
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(len(self.peers))
        print(f"Node {self.id} started on {self.host}:{self.port}")
        threading.Thread(target=self.run_protocol).start()
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                threading.Thread(target=self.listen_to_peers, args=(client_socket,)).start()
            except socket.error:
                break

    def listen_to_peers(self, client_socket: socket.socket):
        """
        Listens to incoming messages from peers
        @param client_socket: the socket to listen to
        """
        try:
            header = client_socket.recv(3).decode('utf-8') # read the first 3 bytes as the header
            data = client_socket.recv(1024)
            match header:
                case "MSG":
                    if message := Message.deserialize(data):
                        self.handle_message(message)
                case "TXN":
                    if transaction := Transaction.deserialize(data):
                        self.add_transaction(transaction)
        except OSError as e:
            print(f"Node {self.id}: error listening to peers: {e} - while running? {self.running}")
        finally:
            client_socket.close()

    def urb_broadcast(self, message: Message):
        """
        URB-broadcasts a message to all peers
        """
        for peer in self.peers:
            try:
                peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_socket.connect(peer)
                peer_socket.sendall(b"MSG" + message.serialize())
                peer_socket.close()
            except Exception as e:
                print(f"Failed to send to {peer}: {e}")

    def add_transaction(self, transaction: Transaction):
        """
        Adds a transaction to the pending transactions
        @param transaction: the transaction to add
        """
        self.pending_tx.append(transaction)

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
        self.blockchain.update_finalization() # check notarization and finalization

    def run_protocol(self):
        """
        Main logic of the node containing the protocol
        """
        print(f"Node {self.id} running protocol")
        while self.running:
            start_time = time.time()
            self.elect_leader(self.current_epoch) # elect the new leader of the epoch
            if self.current_leader == self.id: # if this node is the leader
                self.run_leader_phase()

            # wait for the epoch duration
            elapsed_time = time.time() - start_time
            time.sleep(self.epoch_duration - elapsed_time)
            self.current_epoch += 1
            print(f"Epoch {self.current_epoch}")
            print(f"Chain: {self.blockchain.chain}")
            print(f"Finalized Chain: {[(i.epoch, i.length) for i in self.blockchain.get_finalized_chain()]}")

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

    def elect_leader(self, epoch: int):
        """
        @param epoch: epoch number
        Determine the leader of the epoch based on a VRF (Verifiable Random Function).
        It is "random" but verifiable. Concatenate the current leader with the epoch and hash it
        @param epoch: the epoch number
        """
        input = f"{self.current_leader}{epoch}" # concatenate node id and epoch as the input
        hash = hashlib.sha1(input.encode()).hexdigest()
        self.current_leader = int(hash, 16) % (len(self.peers) + 1)


if __name__ == "__main__":
    host = 'localhost'
    args = parse_program_args()
    node = Node(host, args.port, args.id, args.peers, args.epoch_duration)
    node.start()

    # keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down node...")
        node.stop()
