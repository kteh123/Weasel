from Developer.MenuItems.DeveloperTools import UserInterfaceTools as ui
from Developer.MenuItems.DeveloperTools import PixelArrayDICOMTools as pixel
#**************************************************************************
#Added by third party developer to the template module. 
#The function containing the image processing algorithm must be given the 
#generic name, funcAlgorithm
#uncomment and edit the following line of code to import the function 
#containing your image processing algorith. 
from Developer.External.imagingTools import thresholdPixelArray
FILE_SUFFIX = '_Thresholded'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return False


def main(objWeasel):
    imagePathList = ui.getAllSelectedImages(objWeasel)
    # Lower and upper threshold from the input window. 
    # NO PARAMETER VALIDATION IS PERFORMED
    inputDict = {"Lower Threshold":"integer", "Upper Threshold":"integer"}
    info = "Insert a value between 0 and 100. Upper threshold must be greater than lower threshold"
    paramList = ui.inputWindow(inputDict, title="Input Parameters", helpText=info)
    low_thresh = paramList[0]
    high_thresh = paramList[1]
    for imagePath in imagePathList:    
        # Get the PixelArray from the selected DICOM
        pixelArray = pixel.getPixelArrayFromDICOM(imagePath)
        pixelArray = thresholdPixelArray(pixelArray, low_thresh, high_thresh)
        outputPath = pixel.writeNewPixelArray(objWeasel, pixelArray, imagePath, FILE_SUFFIX)
    ui.displayImage(objWeasel, outputPath)
