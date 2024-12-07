import hashlib
from domain.transaction import Transaction

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
        self.is_finalized = False

    def hash(self) -> bytes:
        """
        Generates the hash of the block
        :return: the hash of the block
        """
        block_str = f"{self.previous_hash}{self.epoch}{self.length}{[str(t) for t in self.transactions]}"
        return hashlib.sha1(block_str.encode()).digest()

    def __repr__(self) -> str:
        """
        String representation of the block
        :return: string representation of the block
        """
        return f"Block(epoch={self.epoch}, length={self.length})"
    
    @property
    def genesis(self) -> bool:
        return self.previous_hash == b'0'