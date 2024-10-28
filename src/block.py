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
        block_str = f"{self.previous_hash}{self.epoch}{self.length}{[str(t) for t in self.transactions]}"
        return hashlib.sha1(block_str.encode()).hexdigest()

    def __repr__(self) -> str:
        return f"Block(epoch={self.epoch}, length={self.length}, hash={self.compute_hash()})"