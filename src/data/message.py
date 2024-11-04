from __future__ import annotations      #imports redudantes e fix do erro da uniao no __init__

import hashlib
from enum import Enum
import pickle # for serialization

from data.block import Block
from data.transaction import Transaction


class MessageType(Enum):
    """
    Enum class for the type of messages
    @param PROPOSE: to be used for proposing blocks - the content is a Block
    @param VOTE: to be used for voting on blocks - the content is a Block, with the Transactions field empty
    @param ECHO: to be used when echoing a message - the content is a Message
    """
    PROPOSE = 1
    VOTE = 2
    ECHO = 3

class Message:
    def __init__(self, type: MessageType, content: 'Transaction' | Block, sender: int):
        # TODO See if it is supposed to be 'Message' or 'Transaction' in the content field
        """
        @param type: type of the message
        @param content: content of the message
        @param sender: sender id
        """
        self.type = type
        self.content = content
        self.sender = sender

    def serialize(self) -> bytes:
        return pickle.dumps(self) # serialize the message (convert object to bytes)

    @staticmethod
    def deserialize(data) -> 'Message':
        return pickle.loads(data) # deserialize the message (convert from bytes to object)

    def hash(self) -> str:
        """
        Computes a SHA-1 hash of the message.
        """
        hasher = hashlib.sha1()
        hasher.update(self.type.name.encode('utf-8'))
        hasher.update(pickle.dumps(self.content))
        hasher.update(str(self.sender).encode('utf-8'))
        return hasher.hexdigest()

    def __repr__(self) -> str:
        return f"Message(type={self.type}, sender={self.sender})"