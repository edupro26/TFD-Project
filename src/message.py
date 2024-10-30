from __future__ import annotations      #imports redudantes e fix do erro da uniao no __init__
from enum import Enum
from block import Block
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

class Message:
    def __init__(self, msg_type: MessageType, content: 'Message' | Block, sender: int):
        """
        @param msg_type: type of the message
        @param content: content of the message 
        @param sender: sender id
        """
        self.msg_type = msg_type
        self.content = content
        self.sender = sender

    def serialize(self) -> bytes:
        return pickle.dumps(self) # serialize the message (convert object to bytes)

    @staticmethod
    def deserialize(data) -> 'Message':
        return pickle.loads(data) # deserialize the message (convert from bytes to object)

    def __repr__(self) -> str:
        return f"Message(type={self.msg_type}, sender={self.sender})"