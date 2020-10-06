import Developer.MenuItems.developerToolsModule as tool
#**************************************************************************
#Added by third party developer to the template module. 
#The function containing the image processing algorithm must be given the 
#generic name, funcAlgorithm
from Developer.WEASEL.Packages.imagingTools import invertAlgorithm
import numpy as np
FILE_SUFFIX = '_Invert'
#***************************************************************************

def main(objWeasel):
    # Slice-by-slice approach + overwrite original image
    # Get all images of the Selected Series
    imagePathList = tool.getImagePathList(objWeasel)
    for imagePath in imagePathList:
        pixelArray = tool.getPixelArrayFromDICOM(imagePath)
        pixelArray = invertAlgorithm(pixelArray, dtype=np.uint16)
        # Need to set progress bars here
        tool.overwritePixelArray(pixelArray, imagePath)
    # Display series
    tool.displayImage(objWeasel, imagePathList)