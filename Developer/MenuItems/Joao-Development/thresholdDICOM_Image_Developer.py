from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import PixelArrayDICOMTools as pixel
from Developer.DeveloperTools import GenericDICOMTools as dicom
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
    # Lower and upper threshold from the input window 
    inputDict = {"Lower Threshold":"integer", "Upper Threshold":"integer"}
    info = "Insert a value between 0 and 100. Upper threshold must be greater than lower threshold"
    paramList = ui.inputWindow(inputDict, title="Input Parameters", helpText=info)
    # NO PARAMETER VALIDATION IS PERFORMED - Eg. LowThresh > HighThresh not possible
    if paramList is None: return # Exit function if the user hits the "Cancel" button
    low_thresh = paramList[0]
    high_thresh = paramList[1]
    seriesNumber, seriesUID = dicom.generateSeriesIDs(imagePathList)
    if isinstance(imagePathList, str): imagePathList = [imagePathList] # Need to check Selecting/Checking and objWeasel
    for imagePath in imagePathList:
        # Get the PixelArray from the selected DICOM
        pixelArray = pixel.getPixelArrayFromDICOM(imagePath)
        pixelArray = thresholdPixelArray(pixelArray, low_thresh, high_thresh)
        outputPath = pixel.writeNewPixelArray(objWeasel, pixelArray, imagePath, FILE_SUFFIX, series_id=seriesNumber, series_uid=seriesUID)
    ui.displayImage(objWeasel, outputPath)
