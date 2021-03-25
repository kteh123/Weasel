from Scripting.OriginalPipelines import OriginalPipelines

from Scripting.WeaselUserInput import WeaselUserInput
from Scripting.WeaselDisplay import WeaselDisplay
from Scripting.WeaselClasses import WeaselClasses
from Scripting.WeaselDicom import WeaselDicom
from Scripting.WeaselFiles import WeaselFiles
from Scripting.WeaselTree import WeaselTree

class Pipelines(
    WeaselUserInput, OriginalPipelines # The original scripting classes
#   WeaselUserInput, WeaselClasses, WeaselDisplay, WeaselDicom, WeaselFiles, WeaselTree # The new scripting classes
    ):
    """
    A collection of methods for weasel scripting. 
    Collected together to avoid multiple import statements 
    in Weasel.py
    """

 

