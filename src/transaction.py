
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