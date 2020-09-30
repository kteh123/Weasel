import Developer.MenuItems.ToolsFunctions  as toolFunctions
#**************************************************************************
#Added by third party developer to the template module. 
#The function containing the image processing algorithm must be given the 
#generic name, funcAlgorithm
from Developer.ScientificLibrary.imagingTools import invertAlgorithm as funcAlgorithm
FILE_SUFFIX = '_Invert'
#***************************************************************************

def processImages(objWeasel):
    toolFunctions.processImages(objWeasel, FILE_SUFFIX, funcAlgorithm)