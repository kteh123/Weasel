"""
Displays a message window in the Weasel GUI saying "Hello World".
"""

def enable(weasel):
    return True

def main(weasel):

    weasel.message(
        msg = "Hello World!",
        title = 'My first tutorial')