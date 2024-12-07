import queue

from domain.block import Block


class BlockChain:
    def __init__(self, node_id: int, num_nodes: int):
        self.node_id = node_id
        self.num_nodes = num_nodes
        self.votes = {}

        genesis = Block(previous_hash=b'0', epoch=0, length=0, transactions=[])
        genesis.isFinalized = True

        self.chain = [genesis]

    def add_block(self, block: Block):
        """
        Adds a block to the blockchain
        :param block: the block to be added
        """
        self.chain.append(block)
        self.votes[block.hash()] = set()

    def add_vote(self, block: Block, node_id: int):
        """
        Adds a vote to a Block of the blockchain
        :param block: the block to be voted
        :param node_id: the id of the node that voted
        """
        if block.hash() in self.votes:
            self.votes[block.hash()].add(node_id)

    def update_finalization(self):
        """
        Checks the finalization of blocks and finalizes if it identifies
        three consecutive notarized blocks with consecutive epochs.
        If so, it finalizes the second block and all its previous blocks
        """
        if len(self.chain) >= 3:
            for i in range(1, self.length() - 1):
                previous = self.chain[i - 1]
                current = self.chain[i]
                next = self.chain[i + 1]

                blocks = [previous, current, next]
                epochs = [block.epoch for block in blocks]
                all_notarized = all(self.check_notarization(i) for i in blocks)
                all_consecutive = all(epochs[i] + 1 == epochs[i + 1] for i in range(len(epochs) - 1))

                if all_notarized and all_consecutive:
                    for j in range(i + 1):
                        if not self.chain[j].isFinalized:
                            self.chain[j].isFinalized = True

    def check_notarization(self, block: Block) -> bool:
        """
        Checks if a block is notarized
        :param block: the block to be checked
        :return: True if the block is notarized, False otherwise
        """
        if block.genesis: # genesis block is always notarized
            return True
        return len(self.votes[block.hash()]) > self.num_nodes / 2

    def length(self):
        """
        Returns the length of the blockchain
        :return: the length of the blockchain
        """
        return len(self.chain) - 1

    def __getitem__(self, item):
        """
        Returns the block at the given index
        :param item: the index of the block
        :return: the block at the given index
        """
        return self.chain[item]

    def __str__(self):
        """
        String representation of both the blockchain and the finalized chain
        :return: the string representation of the blockchain and the finalized chain
        """
        chain_repr = self.__format_chain(self.chain, "Blockchain")
        not_notarized = [block.epoch for block in self.chain if not self.check_notarization(block)]
        finalized_chain = [block for block in self.chain if block.isFinalized]
        finalized_repr = self.__format_chain(finalized_chain, "Finalized")
        return f"{chain_repr}\nNot Notarized: {not_notarized}\n{finalized_repr}"

    def __format_chain(self, chain, label):
        max_blocks = 10
        few_blocks = len(chain) < max_blocks
        blocks = [str(b.epoch) for b in chain]
        blocks_to_show = blocks if few_blocks else ["...", *blocks[-max_blocks+1:]]
        return f"{label}: {" <- ".join(blocks_to_show)}"
