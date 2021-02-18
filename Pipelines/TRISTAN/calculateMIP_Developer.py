from CoreModules.DeveloperTools import UserInterfaceTools
from External.tristanAlgorithms import TRISTAN
import numpy as np
FILE_SUFFIX = '_MIP'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True


def main(objWeasel):
    ui = UserInterfaceTools(objWeasel)
    seriesList = ui.getCheckedSeries()
    if seriesList is None: return # Exit function if no series are checked
    for series in seriesList:
        # Pre-processing
        series.sort("SliceLocation")
        pixelArray = series.PixelArray
        reformatShape = (series.NumberOfSlices, int(np.shape(pixelArray)[0]/series.NumberOfSlices), np.shape(pixelArray)[1], np.shape(pixelArray)[2])
        pixelArray = pixelArray.reshape(reformatShape)
        # Run MIP
        pixelArray = TRISTAN(pixelArray).MIP() # Can definitely improve MIP itself
        # Save resulting image to new DICOM series(and update XML)
        newSeries = series.new(suffix=FILE_SUFFIX)
        newSeries.write(pixelArray)
    # Refresh the UI screen
    ui.refreshWeasel()
    # Display resulting image
    newSeries.Display()