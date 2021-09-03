from API.StaticMethods import StaticMethods
from API.Display import Display
from API.BuildMenus import BuildMenus
from API.Messaging import Messaging
from API.ReadWrite import ReadWrite
from API.State import State
from API.UserInterfaceTools import UserInterfaceTools

class WeaselProgrammingInterface( 
    StaticMethods, # Temporary - these need to move to the library
    Display, 
    BuildMenus, 
    Messaging, 
    ReadWrite,
    State,
    UserInterfaceTools):
    """
    A collection of methods for weasel scripting. 
    Collected together to avoid multiple import statements 
    in Weasel.py
    """

 

