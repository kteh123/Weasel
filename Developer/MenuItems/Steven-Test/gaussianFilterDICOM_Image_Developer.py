from Developer.MenuItems.DeveloperTools import UserInterfaceTools as ui
from Developer.MenuItems.DeveloperTools import PixelArrayDICOMTools as pixel
#**************************************************************************
#Uncomment and edit the following line of code to import the function 
#containing your image processing algorithm. 
from Developer.External.imagingTools import gaussianFilter
FILE_SUFFIX = '_Gaussian'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True


def main(objWeasel):
    # In this case, the user introduces the sigma value intended for the gaussian filter
    inputDict = {"Standard Deviation":"float"}
    paramList = ui.inputWindow(inputDict, title="Input Parameters for the Gaussian Filter")
    standard_deviation_filter = paramList[0]
    # Get selected images
    imagePathList = ui.getAllSelectedImages(objWeasel)
    # Get PixelArray from the selected images
    pixelArray = pixel.getPixelArrayFromDICOM(imagePathList)
    # Apply Gaussian Filter
    pixelArray = gaussianFilter(pixelArray, standard_deviation_filter)
    # Save resulting image to DICOM (and update XML)
    outputhPath = pixel.writeNewPixelArray(objWeasel, pixelArray, imagePathList, FILE_SUFFIX)
    # Display resulting image
    ui.displayImage(objWeasel, outputhPath)
