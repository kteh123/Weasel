"""
Tutorial showing the use of the Message Window in the Weasel GUI.
"""

from Displays.Messaging import Message

def main(weasel):

    msg1 = Message(parent = weasel, message = 'Hello World!')

    print('First message delivered')

    msg2 = Message(parent = weasel, message = 'Hello Again World!')

    print('Second message delivered')

    weasel.message('And once again Hello World!')

    print('Third message delivered')

    maximum = 100
    for i in range(maximum):
        weasel.progress_bar(
            msg = 'Killing some time before closing the messages..',
            index = i,
            max = maximum)

    weasel.close_progress_bar()
    msg1.close()
    msg2.close()
    weasel.close_message()
