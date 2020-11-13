from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import PixelArrayDICOMTools as pixel
#**************************************************************************
#Uncomment and edit the following line of code to import the function 
#containing your image processing algorithm.
import numpy as np
FILE_SUFFIX = "_Square"
# Can be an external toolbox instead
# from Developer.External.imagingTools import squareAlgorithm
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return False


def main(objWeasel):
    imageList = ui.getCheckedImages(objWeasel)
    #newSeries =
    for image in imageList:
        pixelArray = image.PixelArray
        pixelArray = np.square(pixelArray)
        # Saving, which doesn't exist yet in the classes approach - Save into new Series
        # resultingPath = pixel.writeNewPixelArray(objWeasel, pixelArray, imagePathList, FILE_SUFFIX)
    ui.refreshWeasel(objWeasel)
    #newSeries.DisplayImage(objWeasel)
        
