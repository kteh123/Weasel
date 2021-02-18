from CoreModules.DeveloperTools import UserInterfaceTools
from External.ukat.mapping.t2 import T2
import re
#***************************************************************************
import numpy as np
FILE_SUFFIX = '_T2Map'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True


def main(objWeasel):
    ui = UserInterfaceTools(objWeasel)
    # Get all series in the Checkboxes
    seriesList = ui.getCheckedSeries()
    if seriesList is None: return # Exit function if no series are checked
    for series in seriesList:
        seriesMagnitude = series.Magnitude
        if checkT2(seriesMagnitude):
            seriesMagnitude.sort("EchoTime")
            seriesMagnitude.sort("SliceLocation")
            te = np.unique(seriesMagnitude.EchoTimes)
            pixelArray = np.transpose(seriesMagnitude.PixelArray)
            reformatShape = (np.shape(pixelArray)[0], np.shape(pixelArray)[1], int(np.shape(pixelArray)[2]/len(te)), len(te))
            pixelArray = pixelArray.reshape(reformatShape)
            mapper = T2(pixelArray, te)
            t2Map =  mapper.t2_map
            newSeries = seriesMagnitude.new(suffix=FILE_SUFFIX)
            newSeries.write(np.transpose(t2Map))
            # Refresh the UI screen
            ui.refreshWeasel(new_series_name=newSeries.seriesID)
            # Display series
            newSeries.Display()
        else:
            ui.showMessageWindow(msg='The checked series doesn\'t meet the criteria to calculate the T2 Map', title='NOT POSSIBLE TO CALCULATE T2 MAP')


def checkT2(series):
    numberEchoes = len(np.unique(series.EchoTimes))
    if (numberEchoes > 6) and (re.match(".*t2.*", series.seriesID.lower()) or re.match(".*r2.*", series.seriesID.lower())):
        return True
    else:
        return None
