from domain.block import Block
from utils.utils import parse_chain
from threading import RLock

class BlockChain:
    def __init__(self, node_id: int, num_nodes: int):
        self.node_id = node_id
        self.num_nodes = num_nodes
        self.votes = {}  # tracks votes for each block by hash
        genesis = Block(previous_hash=b'0', epoch=0, length=0, transactions=[])
        genesis.is_finalized = True
        self.finalized_chain = [genesis] # contains only finalized blocks
        self.blocks_tree = {genesis.hash(): genesis} # tree-like structure to manage forks
        self.lock = RLock() # reentrant lock for thread safety

    def add_block(self, block: Block):
        """
        Adds a block to the blockchain and updates the forks
        :param block: The block to be added
        """
        with self.lock:
            parent_hash = block.previous_hash
            if parent_hash in self.blocks_tree:
                parent_block = self.blocks_tree[parent_hash]
                parent_block.children.append(block) # maintain parent-child relationship
                self.blocks_tree[block.hash()] = block
                # print(f"Block {block} added with parent {parent_block}")
            

    def add_vote(self, block: Block, node_id: int):
        """
        Adds a vote to a block of the blockchain
        :param block: The block to be voted on
        :param node_id: The ID of the node casting the vote
        """
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
            longest_fork = None
            for block in self.blocks_tree.values():
                fork = self.get_fork_from_block(block)
                epochs = [b.epoch for b in fork]
                if len(fork) < 3:
                    continue # not enough blocks

                for e in range(0, len(epochs) - 2):
                    triplet = epochs[e:e + 3]
                    all_notarized = all(self.check_notarization(b) for b in fork[e:e + 3])
                    all_consecutive = all(triplet[j] + 1 == triplet[j + 1] for j in range(2))
                    if all_notarized and all_consecutive:
                        if longest_fork is None or len(fork) > len(longest_fork):
                            longest_fork = fork

            # finalize the longest notarized fork
            if longest_fork:
                self.stabilize_fork(longest_fork)

    def check_notarization(self, block: Block) -> bool:
        """
        Checks if a block is notarized
        :param block: The block to be checked
        :return: True if the block is notarized, False otherwise
        """
        if block.genesis:  # Genesis block is always notarized
            return True
        votes = self.votes.get(block.hash(), set())
        result = len(votes) > self.num_nodes / 2  # Majority required for notarization

        return result

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
                block = next((b for b in self.blocks_tree.values() if b.hash() == block.previous_hash), None)
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

            # update the blocks_tree to contain only the finalized chain and its direct descendants
            last_finalized = self.finalized_chain[-1]
            last_finalized_hash = last_finalized.hash()

            # get all reachable descendants of the last finalized block
            reachable_blocks = self.get_descendants(last_finalized_hash)
            self.blocks_tree = {b.hash(): b for b in reachable_blocks}

            print(f"Fork stabilized by finalizing up to {to_finalize[-1]}")

    def get_descendants(self, start_hash):
        """
        Retrieves all descendants of a block in the blockchain
        """
        visited = []
        to_visit = [self.blocks_tree[start_hash]] if start_hash in self.blocks_tree else []
        while to_visit:
            current = to_visit.pop()
            visited.append(current)
            to_visit.extend(current.children)
        return visited

    def get_all_forks(self):
        """
        Retrieves all forks in the blockchain as a list of lists
        Each fork is a path from the genesis block to a leaf block
        :return: A list of forks, where each fork is a list of blocks in order
        """
        with self.lock:
            def dfs_fork(block, path):
                path.append(block)
                if not block.children: # leaf block
                    forks.append(path[:]) # add a copy of the path
                else:
                    for child in block.children:
                        dfs_fork(child, path)
                path.pop() # backtrack

            forks = []
            genesis = next((b for b in self.blocks_tree.values() if b.genesis), None)
            if genesis:
                dfs_fork(genesis, [])
            return forks

    def get_non_notarized_blocks(self):
        """
        Retrieves all blocks in the blockchain that are not yet notarized
        :return: A list of non-notarized blocks
        """
        with self.lock:
            non_notarized = [block for block in self.blocks_tree.values() if not self.check_notarization(block)]
            return non_notarized

    def length(self):
        """
        Returns the length of the finalized blockchain
        :return: The length of the finalized blockchain
        """
        return len(self.finalized_chain) - 1

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
        blocks_repr = sorted([b.epoch for b in self.blocks_tree.values()])[1:]
        chain_repr = parse_chain([str(b) for b in self.finalized_chain], "Finalized Blockchain")
        forks = self.get_all_forks()
        forks_repr = "\n\t".join(parse_chain([str(b) for b in fork], "Fork") for fork in forks) if len(forks) > 1 else "No forks"
        non_notarized = self.get_non_notarized_blocks()
        return f"\nPending Blocks:{blocks_repr}\n{chain_repr}\nNon-Notarized blocks: {non_notarized}\n\t{forks_repr}\n"
