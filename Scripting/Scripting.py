from Scripting.WeaselUserInput import WeaselUserInput
from Scripting.WeaselDisplay import WeaselDisplay
from Scripting.WeaselDicom import WeaselDicom
from Scripting.WeaselDataFrame import WeaselDataFrame
from Scripting.WeaselFiles import WeaselFiles
from Scripting.WeaselElementTree import WeaselElementTree

class Pipelines(
    WeaselUserInput, 
    WeaselDisplay, 
    WeaselDicom, 
    WeaselDataFrame, 
    WeaselFiles, 
    WeaselElementTree):
    """
    A collection of methods for weasel scripting. 
    Collected together to avoid multiple import statements 
    in Weasel.py
    """

 

