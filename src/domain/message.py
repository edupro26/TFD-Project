from __future__ import annotations
from enum import Enum
from domain.block import Block
import hashlib
import pickle # for serialization


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

    def __str__(self) -> str:
        return self.name

class Message:
    def __init__(self, type: MessageType, content: 'Message' | Block, sender: int, epoch: int):
        """
        @param type: type of the message
        @param content: content of the message
        @param sender: sender id
        """
        self.type = type
        self.content = content
        self.sender = sender
        self.epoch = epoch

    def serialize(self) -> bytes:
        """
        Serialize the message (convert object to bytes)
        :return: the serialized message
        """
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data) -> 'Message':
        """
        Deserialize the message (convert from bytes to object)
        :param data: the serialized message
        :return: the deserialized message
        """
        return pickle.loads(data)

    def hash(self) -> str:
        """
        Computes a SHA-1 hash of the message.
        :return: the hash of the message
        """
        hasher = hashlib.sha1()
        hasher.update(self.type.name.encode('utf-8'))
        hasher.update(pickle.dumps(self.content))
        hasher.update(str(self.sender).encode('utf-8'))
        return hasher.hexdigest()

    def __repr__(self) -> str:
        """
        String representation of the message
        :return: string representation of the message
        """
        return f"Message(type={self.type}, sender={self.sender})"