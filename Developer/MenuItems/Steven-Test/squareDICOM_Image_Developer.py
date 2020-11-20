from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import Series, Image
#**************************************************************************
import numpy as np
FILE_SUFFIX = "_Square"
# Can be an external toolbox instead
# from Developer.External.imagingTools import squareAlgorithm
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return False


def main(objWeasel):
    seriesList = ui.getCheckedSeries(objWeasel)
    for series in seriesList:
        newSeries = Series.newSeriesFrom(series, suffix=FILE_SUFFIX)
        pixelArray = series.PixelArray
        pixelArray = np.square(pixelArray)
        newSeries.write(pixelArray)
    ui.refreshWeasel(objWeasel)
    ui.refreshWeasel(objWeasel, newSeriesName=newSeries.seriesID) # Still need to solve this double-call
    newSeries.DisplaySeries()
        
