from typing import Set, Any

from domain.block import Block


class BlockChain:
    def __init__(self, node_id: int, num_nodes: int):
        self.node_id = node_id
        self.num_nodes = num_nodes
        self.chain = [Block(previous_hash=b'0', epoch=0, length=0, transactions=[])]
        self.__finalized_chain = []
        self.__votes = {}

    def add_block(self, block: Block):
        """
        Adds a block to the blockchain
        :param block: the block to be added
        """
        self.chain.append(block)
        self.__votes[block.hash()] = set()

    def add_vote(self, block: Block, node_id: int):
        """
        Adds a vote to a Block of the blockchain
        :param block: the block to be voted
        :param node_id: the id of the node that voted
        """
        self.__votes[block.hash()].add(node_id)

    def update_finalization(self):
        """
        Checks the finalization of blocks and finalizes if it identifies
        three consecutive notarized blocks with consecutive epochs.
        If so, it finalizes the second block and all its previous blocks
        """
        start = self.__finalized_chain[-1].length if self.__finalized_chain else 0
        for i in range(start + 1, self.length() - 2):
            # three consecutive blocks
            blocks = self.chain[i:i + 3]
            block1, block2, block3 = blocks
            epochs = [block.epoch for block in blocks]
            all_notarized = all(self.__check_notarization(block) for block in blocks)
            all_consecutive = all(epochs[i]+1 == epochs[i+1] for i in range(len(epochs) - 1))

            if all_notarized and all_consecutive:
                self.__finalized_chain.extend([block1, block2])

    def __check_notarization(self, block: Block) -> bool:
        """
        Checks if a block is notarized
        :param block: the block to be checked
        :return: True if the block is notarized, False otherwise
        """
        return len(self.__votes[block.hash()]) > self.num_nodes / 2

    def get_finalized_chain(self) -> list[Block]:
        """
        Returns the finalized chain
        :return: the finalized chain
        """
        return self.__finalized_chain

    def length(self):
        """
        Returns the length of the blockchain
        :return: the length of the blockchain
        """
        return len(self.chain) - 1

    def __str__(self):
        """
        Returns a string representation of the finalized blockchain
        :return: the string representation of the finalized blockchain
        """
        chain_str = f"Blockchain (Node {self.node_id}):\n"
        for block in self.__finalized_chain:
            chain_str += f"Block {block.length}:\n"
            chain_str += f"  Epoch: {block.epoch}\n"
            chain_str += f"  Transactions: {block.transactions}\n"
        return chain_str

    def __getitem__(self, item):
        """
        Returns the block at the given index
        :param item: the index of the block
        :return: the block at the given index
        """
        return self.chain[item]