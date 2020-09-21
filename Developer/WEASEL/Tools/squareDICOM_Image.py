
import Developer.WEASEL.Tools.ToolsFunctions  as toolFunctions
#**************************************************************************
#Added by third party developer to the template module. 
#The function containing the image processing algorithm must be given the 
#generic name, funcAlgorithm
#uncomment and edit the following line of code to import the function 
#containing your image processing algorith. 
from Developer.WEASEL.ScientificLibrary.imagingTools import squareAlgorithm as funcAlgorithm
FILE_SUFFIX = '_Square'
#***************************************************************************


def processImages(objWeasel):
    toolFunctions.processImages(objWeasel, FILE_SUFFIX, funcAlgorithm)

