import Developer.MenuItems.developerToolsModule as tool
#**************************************************************************
#Added by third party developer to the template module. 
#The function containing the image processing algorithm must be given the 
#generic name, funcAlgorithm
#uncomment and edit the following line of code to import the function 
#containing your image processing algorith. 
from Developer.External.imagingTools import gaussianFilter
FILE_SUFFIX = '_Gaussian'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True


def main(objWeasel):
    # In this case, the user introduces the sigma value intended for the gaussian filter
    inputDict = {"Standard Deviation":"float"}
    paramList = tool.inputWindow(inputDict, title="Input Parameters for the Gaussian Filter")
    standard_deviation_filter = paramList[0]
    # Get selected images
    imagePathList = tool.getImagePathList(objWeasel)
    # Get PixelArray from the selected images
    pixelArray = tool.getPixelArrayFromDICOM(imagePathList)
    # Apply Gaussian Filter
    pixelArray = gaussianFilter(pixelArray, standard_deviation_filter)
    # Save resulting image to DICOM (and update XML)
    outputhPath = tool.writeNewPixelArray(objWeasel, pixelArray, imagePathList, FILE_SUFFIX)
    # Display resulting image
    tool.displayImage(objWeasel, outputhPath)
