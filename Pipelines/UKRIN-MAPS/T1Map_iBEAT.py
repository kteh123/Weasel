from CoreModules.DeveloperTools import UserInterfaceTools, Series
from External.ukat.mapping.t1 import T1, magnitude_correct
from CoreModules.imagingTools import formatArrayForAnalysis
from External.ukrinAlgorithms import ukrinMaps
# 
import re
#***************************************************************************
import numpy as np
FILE_SUFFIX = '_T1Map'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True


def main(objWeasel):
    ui = UserInterfaceTools(objWeasel)
    # Get the series in the Checkboxes
    seriesList = ui.getCheckedSeries()
    if seriesList is None: return # Exit function if no series are checked
    series = seriesList[0]
    if checkT1(series):
        seriesMagnitude = series.Magnitude
        try:
            seriesMagnitude.sort("InversionTime")
        except:
            seriesMagnitude.sort(0x20051572)
        seriesMagnitude.sort("SliceLocation")
        numSlices = seriesMagnitude.NumberOfSlices
        ti = np.array(seriesMagnitude.InversionTimes) # array of length = 50 or 10
        ti = ti.reshape((int(len(ti)/numSlices), numSlices)) # array of size (10, 5) or (10, 1)
        pixelArray = np.transpose(seriesMagnitude.PixelArray) # (256, 256, 50) or (256, 256, 10)
        reformatShape = (np.shape(pixelArray)[0], np.shape(pixelArray)[1], numSlices, int(np.shape(pixelArray)[2]/numSlices))
        pixelArray = pixelArray.reshape(reformatShape) # (256, 256, 5, 10) or (256, 256, 1, 10)
        #######################################################
        outputArray = []
        for zSlice in range(np.shape(pixelArray)[2]):
            tempImage = ukrinMaps(np.squeeze(pixelArray[:, :, zSlice, :])).T1Map(ti[:, zSlice]) # There's MATLAB version T1MapMolli
            outputArray.append(np.transpose(tempImage))
        outputArray = np.squeeze(np.array(outputArray))
        del tempImage
        ########################################################
        outputSeries = series.new(series_name="T1Map_iBEAT", suffix=FILE_SUFFIX)
        outputSeries.write(outputArray)
        # Refresh Weasel
        ui.refreshWeasel(new_series_name=outputSeries.seriesID)
        # Display series
        outputSeries.display()
    else:
        ui.showMessageWindow(msg='The checked series doesn\'t meet the criteria to calculate the T1 Map', title='NOT POSSIBLE TO CALCULATE T1 MAP')


def checkT1(series):
    numberTIs = len(np.unique(series.InversionTimes))
    if (numberTIs > 0) and (re.match(".*ti.*", series.seriesID.lower()) or re.match(".*molli.*", series.seriesID.lower()) or re.match(".*tfl.*", series.seriesID.lower()) or re.match(".*ir.*", series.seriesID.lower())):
        return True
    else:
        return None
