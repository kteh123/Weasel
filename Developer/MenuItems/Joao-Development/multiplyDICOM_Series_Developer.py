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
    # Get all series in the Checkboxes
    seriesList = ui.getCheckedSeries(objWeasel)
    dimensions = seriesList[0].Dimensions
    # If all dimensions are not the same then return error 
    if checkDimensionsMatch(seriesList, dimensions) is None: return
    ######## GROUPWISE ###########
    # Multiplication Loop
    outputArray = seriesList[0].PixelArray
    for nextSeries in seriesList[1:]: # tupleSeries
        # Multiply inside the loop with the previous result
        outputArray *= nextSeries.PixelArray

    # HOW TO SAVE!?
    # outputPath, tupleSeries = pixel.writeNewPixelArray(objWeasel, outputArray, imagePathList, FILE_SUFFIX)
    # Refresh the UI screen
    ui.refreshWeasel(objWeasel)

    # Display series
    # ui.displayImage(objWeasel, outputPath) # tuple in place of outputPath
    # Make series as a potential input
    # ui.displaySeries(objWeasel, seriesID)


def SliceBySlice(objWeasel):
    # Get all series in the Checkboxes
    seriesList = ui.getCheckedSeries(objWeasel)
    dimensions = seriesList[0].Dimensions
    # If all dimensions are not the same then return error
    if checkDimensionsMatch(seriesList, dimensions) is None: return
    ######## SLICE-BY-SLICE ########
    # seriesNumber, seriesUID = dicom.generateSeriesIDs(imagePathList)
    
    #newSeries = SeriesList[0].duplicate
    #nr_of_images = SeriesList[0].numberChildren
    #for i in range(nr_of_images):
    #    outputArray = seriesList[0].children[i].PixelArray
    #    for series in seriesList[1:]
    #        outputArray *= series.children[i].PixelArray
    #    newSeries.child[i].PixelArray(OutputArray)


def checkDimensionsMatch(seriesList, dimensions):
    for series in seriesList:
        if series.Dimensions != dimensions:
            return None
    return True
