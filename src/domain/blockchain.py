from domain.block import Block
from utils.utils import parse_chain
from threading import RLock

class BlockChain:
    def __init__(self, node_id: int, num_nodes: int):
        self.node_id = node_id
        self.num_nodes = num_nodes
        self.votes = {}  # tracks votes for each block by hash
        self.genesis = Block(previous_hash=b'0', epoch=0, length=0, transactions=[])
        self.genesis.is_finalized = True
        self.finalized_chain = [self.genesis] # contains only finalized blocks
        self.not_finalized_blocks = {self.genesis.hash(): self.genesis} # tree-like structure to manage forks
        self.lock = RLock() # reentrant lock for thread safety
        self.last_block = self.genesis

    def add_block(self, block: Block):
        """
        Adds a block to the blockchain and updates the forks
        :param block: The block to be added
        """
        with self.lock:
            parent_hash = block.previous_hash
            parent_block = self.not_finalized_blocks.get(parent_hash, self.genesis)
            parent_block.children.append(block) # child parent relationship
            self.not_finalized_blocks[block.hash()] = block
            self.last_block = block

    def add_vote(self, block: Block, node_id: int):
        """
        Adds a vote to a block of the blockchain
        :param block: The block to be voted on
        :param node_id: The ID of the node casting the vote
        """
        with self.lock:
            if block.hash() not in self.votes:
                self.votes[block.hash()] = set()
            self.votes[block.hash()].add(node_id)
            # print(f"Vote added for block {block} by node {node_id}")

    def update_finalization(self):
        """
        Stabilizes on the longest fork with at least three consecutive notarized blocks
        Finalizes the fork and discards other blocks
        """
        with self.lock:
            longest_fork = []
            forks = self.get_forks()
            for fork in forks:
                # check for three consecutive notarized blocks
                for i in range(len(fork) - 2):
                    triplet = fork[i:i+3]
                    all_notarized = all(self.check_notarization(b) for b in triplet)
                    all_consecutive = all(triplet[j].epoch + 1 == triplet[j+1].epoch for j in range(2))
                    if all_notarized and all_consecutive:
                        if len(fork) > len(longest_fork):
                            longest_fork = fork
                
            if longest_fork: # finalize the longest notarized fork
                self.stabilize_fork(longest_fork)

    def check_notarization(self, block: Block) -> bool:
        """
        Checks if a block is notarized
        :param block: The block to be checked
        :return: True if the block is notarized, False otherwise
        """
        if block.genesis: # genesis block is always notarized
            return True
        votes = self.votes.get(block.hash(), set())
        return len(votes) > self.num_nodes / 2 # majority required for notarization

    def get_fork_from_block(self, block: Block):
        """
        Constructs a fork ending at the given block
        Traverses back from the given block to the genesis block
        :param block: The block to trace back from
        :return: The fork (list of blocks) in chronological order
        """
        with self.lock:
            fork = []
            while block:
                fork.append(block)
                block = next((b for b in self.not_finalized_blocks.values() if b.hash() == block.previous_hash), None)
            return fork[::-1] # return the fork in chronological order


    def stabilize_fork(self, fork: list[Block]):
        """
        Finalizes the chosen fork up to the block before the last notarized block in the triple
        """
        with self.lock:
            to_finalize = fork[:len(fork) - 2] # up until second last notarized block

            # mark blocks as finalized
            for block in to_finalize:
                block.is_finalized = True

            # add finalized blocks to the finalized chain
            finalized_hashes = {b.hash() for b in self.finalized_chain}
            new_finalized_blocks = [b for b in to_finalize if b.hash() not in finalized_hashes]
            self.finalized_chain.extend(new_finalized_blocks)

            # remove finalized blocks from the not finalized blocks
            last_finalized = self.finalized_chain[-1]
            last_finalized_hash = last_finalized.hash()

            # get all reachable descendants of the last finalized block
            reachable_blocks = self.get_descendants(last_finalized_hash)
            self.not_finalized_blocks = {b.hash(): b for b in reachable_blocks}

    def get_descendants(self, start_hash):
        """
        Retrieves all descendants of a block in the blockchain
        """
        visited = []
        to_visit = [self.not_finalized_blocks[start_hash]] if start_hash in self.not_finalized_blocks else []
        while to_visit:
            current = to_visit.pop()
            visited.append(current)
            to_visit.extend(current.children)
        return visited

    def get_forks(self):
        """
        Retrieves all forks in the blockchain as a list of lists
        Each fork is a path from a leaf block back to the genesis block
        :return: A list of forks, where each fork is a list of blocks in order
        """
        with self.lock:
            forks = []
            leaf_blocks = [block for block in self.not_finalized_blocks.values() if not block.children] 
            for leaf in leaf_blocks:
                fork = []
                current = leaf
                while current:
                    fork.append(current)
                    if current.genesis:
                        break  # stop at the genesis block
                    current = self.not_finalized_blocks.get(current.previous_hash, None)
                forks.append(fork[::-1]) # reverse to chronological order

            return forks

    
    def get_notarized_blocks(self):
        with self.lock:
            return [block for block in self.not_finalized_blocks.values() if self.check_notarization(block)]
    
    def get_non_notarized_blocks(self):
        with self.lock:
            return list(set(self.not_finalized_blocks.values()) - set(self.get_notarized_blocks()))

    def length(self):
        """
        Returns the length of the blockchain
        :return: The length of the blockchain
        """
        return self.last_block.length - 1

    def __getitem__(self, item):
        """
        Returns the block at the given index
        :param item: The index of the block
        :return: The block at the given index
        """
        return self.finalized_chain[item]

    def __str__(self):
        """
        String representation of both the blockchain and the finalized chain
        :return: The string representation of the blockchain and the finalized chain
        """
        blocks_repr = sorted([b.epoch for b in self.not_finalized_blocks.values()])[1:]
        chain_repr = parse_chain([str(b) for b in self.finalized_chain], "Finalized Blockchain")
        forks = self.get_forks()
        forks_repr = "\n\t".join(parse_chain([str(b) for b in fork], "Fork") for fork in forks) if len(forks) > 1 else "No forks"
        non_notarized = self.get_non_notarized_blocks()
        return f"\nNot Finalized Blocks:{blocks_repr}\n{chain_repr}\nNon-Notarized blocks: {non_notarized}\n\t{forks_repr}\n"