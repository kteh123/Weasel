import Developer.MenuItems.ToolsFunctions  as toolFunctions
#**************************************************************************
#Added by third party developer to the template module. 
#The function containing the image processing algorithm must be given the 
#generic name, funcAlgorithm
from Developer.External.imagingTools import invertAlgorithm as funcAlgorithm
FILE_SUFFIX = '_Invert'
#***************************************************************************

def main(objWeasel):
    toolFunctions.main(objWeasel, FILE_SUFFIX, funcAlgorithm)