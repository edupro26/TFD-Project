import pickle

class Transaction:
    def __init__(self, sender: int, receiver: int, tx_id: int, amount: float):
        """
        @param sender: sender id
        @param receiver: receiver id
        @param tx_id: transaction id, unique with sender
        @param amount: amount to be transferred
        """
        self.sender = sender
        self.receiver = receiver
        self.tx_id = tx_id
        self.amount = amount

    def serialize(self) -> bytes:
        """
        Serialize the transaction (convert object to bytes)
        """
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data) -> 'Transaction':
        """
        Deserialize the transaction (convert from bytes to object)
        """
        return pickle.loads(data)

    def __repr__(self) -> str:
        return f"Transaction(sender={self.sender}, receiver={self.receiver}, tx_id={self.tx_id}, amount={self.amount})"