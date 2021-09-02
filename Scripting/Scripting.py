from Scripting.Statics import Statics
from Scripting.Display import Display
from Scripting.Messaging import Messaging
from Scripting.ReadWrite import ReadWrite

class Pipelines( 
    Statics, # Temporary - these need to move to the library
    Display, 
    Messaging, 
    ReadWrite):
    """
    A collection of methods for weasel scripting. 
    Collected together to avoid multiple import statements 
    in Weasel.py
    """

 

