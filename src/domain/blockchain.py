from domain.block import Block
from utils.utils import parse_chain


class BlockChain:
    def __init__(self, node_id: int, num_nodes: int):
        self.node_id = node_id
        self.num_nodes = num_nodes
        self.votes = {}
        genesis = Block(previous_hash=b'0', epoch=0, length=0, transactions=[])
        genesis.is_finalized = True
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
        if len(self.chain) < 3:
            return  # not enough blocks

        for i in range(0, self.length()):
            blocks = self.chain[i:i + 3]
            if len(blocks) < 3:
                break
            epochs = [block.epoch for block in blocks]
            all_notarized = all(self.check_notarization(block) for block in blocks)
            all_consecutive = all(epochs[k] + 1 == epochs[k + 1] for k in range(len(epochs) - 1))

            if all_notarized and all_consecutive:
                for j in range(i + 1):
                    self.chain[j].is_finalized = True

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
        chain_repr = parse_chain([str(b) for b in self.chain], "Blockchain")
        finalized_chain = [str(block) for block in self.chain if block.is_finalized]
        finalized_repr = parse_chain(finalized_chain, "Finalized")
        return f"{chain_repr}\n{finalized_repr}"
