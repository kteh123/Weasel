from API.StaticMethods import StaticMethods
from API.Display import Display
from API.Messaging import Messaging
from API.ReadWrite import ReadWrite
from API.State import State

class WeaselProgrammingInterface( 
    StaticMethods, # Temporary - these need to move to the library
    Display, 
    Messaging, 
    ReadWrite,
    State):
    """
    A collection of methods for weasel scripting. 
    Collected together to avoid multiple import statements 
    in Weasel.py
    """

 

