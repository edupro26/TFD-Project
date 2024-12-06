from domain.block import Block


class BlockChain:
    def __init__(self, node_id: int, num_nodes: int):
        self.node_id = node_id
        self.num_nodes = num_nodes
        self.chain = [Block(previous_hash=b'0', epoch=0, length=0, transactions=[])]
        self.finalized_chain = [self.chain[0]]
        self.votes = {}

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
        for i in range(self.finalized_chain[-1].length, self.length() - 2):
            # three consecutive blocks
            blocks = self.chain[i:i + 3]
            epochs = [block.epoch for block in blocks]
            all_notarized = all(self.__check_notarization(block) for block in blocks)
            all_consecutive = all(epochs[i]+1 == epochs[i+1] for i in range(len(epochs) - 1))

            if all_notarized and all_consecutive:
                self.finalized_chain.append(blocks[1]) # finalize the second block

    def __check_notarization(self, block: Block) -> bool:
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
        str = "Blockchain: ["
        str += ", ".join(f"(e={b.epoch}, l={b.length})" for b in self.chain)
        str += "]\nFinalized Chain: ["
        str += ", ".join(f"(e={b.epoch}, l={b.length})" for b in self.finalized_chain)
        str += "]"
        return str