from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import Series, Image
import numpy as np
FILE_SUFFIX = '_Multiplied'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True


def main(objWeasel):
    # Get all series in the Checkboxes
    seriesList = ui.getCheckedSeries(objWeasel)
    # If all dimensions are not the same then return error
    if checkDimensionsMatch(seriesList) is None: return

    #newSeries = Series.newSeriesFrom(seriesList[0], suffix=FILE_SUFFIX)
    newSeries = seriesList[0].new(suffix=FILE_SUFFIX)
    nrOfImages = seriesList[0].numberChildren
    for i in range(nrOfImages):
        outputArray = seriesList[0].children[i].PixelArray
        for series in seriesList[1:]:
            outputArray *= series.children[i].PixelArray
        newImage = seriesList[0].children[i].new(series=newSeries)
        newImage.write(outputArray, series=newSeries)
    # Refresh the UI screen
    ui.refreshWeasel(objWeasel, newSeriesName=newSeries.seriesID)
    # Display series
    newSeries.DisplaySeries()


def checkDimensionsMatch(seriesList):
    dimensionsArray = []
    for series in seriesList:
        dimensionsArray.append(series.Dimensions)
    if len(np.unique(dimensionsArray, axis=0))==1:
        return True
    else:
        return None
