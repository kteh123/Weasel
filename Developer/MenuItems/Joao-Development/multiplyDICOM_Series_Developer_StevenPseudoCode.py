from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import PixelArrayDICOMTools as pixel
import operator
from functools import reduce
FILE_SUFFIX = '_Multiplied'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True


def main(objWeasel):
    # THIS IS PSEUDO-CODE SUGGESTED BY STEVEN SOURBRON

    # Get all series in the Checkboxes
    seriesList = ui.getListOfCheckedSeries(objWeasel)
    dimensions = getArrayDimensions(seriesList) # getEchoTimes but in a generic way
    checkDimensionsMatch(dimension) # If all dimensions are not the same then return error 

    ######## GROUPWISE ###########
    # Multiplication Loop
    outputArray = seriesList[0].getPixelArrayFromDICOM
    for nextSeries in seriesList[1:]: # tupleSeries
        # Multiply inside the loop with the previous result
        outputArray *= nextSeries.getPixelArrayFromDICOM

    ######## SLICE-BY-SLICE ########
    seriesNumber, seriesUID = dicom.generateSeriesIDs(imagePathList)



    outputhPath, tupleSeries = pixel.writeNewPixelArray(objWeasel, outputArray, imagePathList, FILE_SUFFIX)
    # Refresh the UI screen
    ui.refreshWeasel(objWeasel)
    # Display series
    ui.displayImage(objWeasel, outputhPath) # tuple in place of outputPath
    # Make series as a potential input
    # ui.displaySeries(objWeasel, seriesID)