"""
This help button forwards the user to the website https://weasel.pro.
"""
import webbrowser

def isEnabled(weasel):
    return True

def main(weasel):
    webbrowser.open("Weasel.pro")
