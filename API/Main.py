"""
A collection of methods for weasel scripting. These are bundled together to avoid multiple import statements in Weasel.py.
"""

from API.StaticMethods import StaticMethods
from API.Display import Display
from API.EditMenus import EditMenus
from API.Messaging import Messaging
from API.ReadWrite import ReadWrite
from API.UserInterfaceTools import UserInterfaceTools

class WeaselProgrammingInterface( 
    StaticMethods,
    Display, 
    EditMenus, 
    Messaging, 
    ReadWrite,
    UserInterfaceTools):
    """
    A collection of methods for weasel scripting.

    StaticMethods, Display, EditMenus, Messaging, ReadWrite and UserInterfaceTools are bundled together to avoid multiple import statements in Weasel.py
    """

