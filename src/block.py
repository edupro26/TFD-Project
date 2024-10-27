import hashlib

from transaction import Transaction

class Block:
    def __init__(self, previous_hash: bytes, epoch: int, length: int, transactions: list[Transaction]):
        """
        @param previous_hash: SHA1 hash of the previous block
        @param epoch: the epoch number the block was generated
        @param length: the number of the block in the proposer blockchain
        @param transactions: list of transactions on the block
        """
        self.previous_hash = previous_hash
        self.epoch = epoch
        self.length = length
        self.transactions = transactions

    def calculate_hash(self) -> bytes:
        h = hashlib.sha1()
        h.update(str(self.previous_hash).encode('utf-8'))
        h.update(str(self.epoch).encode('utf-8'))
        h.update(str(self.length).encode('utf-8'))
        for t in self.transactions:
            h.update(str(t).encode('utf-8'))

        return h.digest()