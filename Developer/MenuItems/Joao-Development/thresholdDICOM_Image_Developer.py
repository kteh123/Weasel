from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import PixelArrayDICOMTools as pixel
from Developer.DeveloperTools import GenericDICOMTools as dicom
#**************************************************************************
from Developer.External.imagingTools import thresholdPixelArray
FILE_SUFFIX = '_Thresholded'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True


def main(objWeasel):
    imagePathList = ui.getListOfAllCheckedImages(objWeasel)
    # Lower and upper threshold from the input window 
    inputDict = {"Lower Threshold":"integer", "Upper Threshold":"integer"}
    info = "Insert a value between 0 and 100. Upper threshold must be greater than lower threshold"
    paramList = ui.inputWindow(inputDict, title="Input Parameters", helpText=info)
    # NO PARAMETER VALIDATION IS PERFORMED - Eg. LowThresh > HighThresh not possible
    if paramList is None: return # Exit function if the user hits the "Cancel" button
    low_thresh = paramList[0]
    high_thresh = paramList[1]
    seriesNumber, seriesUID = dicom.generateSeriesIDs(imagePathList)
    if isinstance(imagePathList, str): imagePathList = [imagePathList]
    index_bar=0
    for imagePath in imagePathList:
        # Get the PixelArray from the selected DICOM
        index_bar = ui.progressBar(objWeasel, maxNumber=len(imagePathList), index=index_bar, msg="Thresholding and saving image {}", title="Threshold")
        pixelArray = pixel.getPixelArrayFromDICOM(imagePath)
        pixelArray = thresholdPixelArray(pixelArray, low_thresh, high_thresh)
        outputPath = pixel.writeNewPixelArray(objWeasel, pixelArray, imagePath, FILE_SUFFIX, series_id=seriesNumber, series_uid=seriesUID)
    ui.closeMessageWindow(objWeasel)
    # Refresh the UI screen
    ui.refreshWeasel(objWeasel)
    # If I want to expand the tree, then I need to re-run the refresh in the following way
    seriesID = ui.getSeriesFromImages(objWeasel, outputPath)
    ui.refreshWeasel(objWeasel, newSeriesName=seriesID)
    # Display outputPath. In this case it's only one image
    ui.displayImage(objWeasel, outputPath) # tuple in place of outputPath
    # Make series as a potential input
    # ui.displaySeries(objWeasel, seriesID)
