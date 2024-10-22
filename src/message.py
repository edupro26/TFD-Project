from enum import Enum
from block import Block

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