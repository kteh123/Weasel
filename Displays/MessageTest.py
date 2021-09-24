
from Message import Message

weasel = None

message = Message(
    parent = weasel, 
    message = 'Hello World!')

print('First message delivered')

message = Message(
    parent = weasel, 
    message = 'Hello Again World!')

print('Second message delivered')
