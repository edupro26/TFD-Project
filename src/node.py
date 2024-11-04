import socket
import threading
import time
import hashlib

from utils.args import parse_args
from data.block import Block
from data.message import Message, MessageType


class Node:
    def __init__(self, host: str, port: int, id: int, peers: list[int], epoch_duration: int):
        self.host = host
        self.port = port
        self.id = id
        self.peers = [(self.host, int(p)) for p in peers]
        self.running = False
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pending_tx = []
        self.current_leader = 0
        self.current_epoch = 0
        self.votes = {}
        self.notarized_blocks = set()
        self.epoch_duration = epoch_duration
        self.blockchain = []

        # To avoid processing the same message multiple times
        self.received_messages = set()

    def run(self):
        self.running = True
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        server_thread.start()

    def stop(self):
        self.running = False
        self.server_socket.close()

    def start_server(self):
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

    def listen_to_peers(self, client_socket):
        try:
            data = client_socket.recv(1024)
            message = Message.deserialize(data)
            if message:
                print(f"Received message: {message}")
                self.handle_message(message)
        except OSError as e:
            print(f"Node {self.id}: error listening to peers: {e} - while running? {self.running}")
        finally:
            client_socket.close()

    def urb_broadcast(self, message: Message):
        message_hash = message.hash()
        if message_hash not in self.received_messages:
            self.received_messages.add(message_hash)
            for peer in self.peers:
                try:
                    peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    peer_socket.connect(peer)
                    peer_socket.sendall(message.serialize())
                    peer_socket.close()
                except Exception as e:
                    print(f"Failed to send to {peer}: {e}")

    def handle_message(self, message: Message):
        match message.type:
            case MessageType.ECHO:
                self.urb_broadcast(message)
            case MessageType.PROPOSE:
                self.handle_block_proposal(message)
            case MessageType.VOTE:
                self.handle_block_vote(message)

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
            self.urb_broadcast(vote_message)

    def handle_block_vote(self, message: Message):
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

    def run_protocol(self):
        """
        Main logic of the node containing the protocol
        """
        print(f"Node {self.id} running protocol")
        while self.running:
            start_time = time.time()
            # TODO this needs fixing
            #self.elect_leader()  # elect the new leader of the epoch
            if self.current_leader == self.id:  # if this node is the leader
                # self.run_leader_phase() TODO this needs fixing
                pass

            # wait for the epoch duration
            elapsed_time = time.time() - start_time
            time.sleep(self.epoch_duration - elapsed_time)
            self.current_epoch += 1

    def check_finalization(self):
        # TODO
        pass

    def run_leader_phase(self):
        """
        Runs the leader phase by proposing a new block and broadcasting it
        """
        # propose new block
        previous_block = self.blockchain[-1]
        previous_hash = previous_block.compute_hash()
        new_block = Block(
            previous_hash=previous_hash,
            epoch=self.current_epoch,
            length=len(self.blockchain),
            transactions=self.pending_tx.copy()
        )
        # clear the pending transactions
        self.pending_tx.clear()

        # broadcast the proposed block
        propose_message = Message(MessageType.PROPOSE, new_block, self.id)
        self.urb_broadcast(propose_message)

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


if __name__ == "__main__":
    host = 'localhost'
    args = parse_args()
    node = Node(host, args.port, args.id, args.peers, args.epoch_duration)
    node.run()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down node...")
        node.stop()
