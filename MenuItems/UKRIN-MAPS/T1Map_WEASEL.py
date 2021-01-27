from CoreModules.DeveloperTools import UserInterfaceTools, Series
from External.ukat.mapping.t1 import T1, magnitude_correct
from External.ukat.utils.tools import convert_to_pi_range
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
    # Get all series in the Checkboxes
    seriesList = ui.getCheckedSeries() # getSelectedStudy()
    # List of series that will be used for T1 Map calculation
    seriesListTI = []
    for series in seriesList:
        # First, collect all series that belong to T1 calculation. This is because 1 series <=> 1 image/TI
        if checkT1(series):
            seriesListTI.append(series)
    if seriesListTI:
        mergedSeries = Series.merge(seriesListTI, series_name='All_TIs', overwrite=False)
        mergedSeries.sort("SliceLocation", "InversionTime")
        magnitudeSeries = mergedSeries.Magnitude
        # CONSIDER REFORMAT_SHAPE - 4D such as (256, 256, 5, 10) for eg.
        ti = magnitudeSeries.InversionTimes
        magnitude = magnitudeSeries.PixelArray
        phaseSeries = mergedSeries.Phase
        if phaseSeries.images:
            phase = convert_to_pi_range(phaseSeries.PixelArray)
            complex_data = magnitude * (np.cos(phase) + 1j * np.sin(phase)) # convert magnitude and phase into complex data
            magnitude_corrected = magnitude_correct(complex_data)
            inputArray = magnitude_corrected
        else:
            inputArray = magnitude
        mapper = T1(np.transpose(inputArray), ti, multithread=False, parameters=2)
        pixelArray = mapper.t1_map
        #outputSeries = mergedSeries.new(series_name="T1Map_UKRIN", suffix=FILE_SUFFIX)
        outputSeries = seriesListTI[0].new(series_name="T1Map_UKRIN", suffix=FILE_SUFFIX)
        outputSeries.write(np.transpose(pixelArray))
        # Refresh Weasel
        ui.refreshWeasel(new_series_name=outputSeries.seriesID)
        # Display series
        outputSeries.DisplaySeries()
    else:
        ui.showMessageWindow(msg='The checked series doesn\'t meet the criteria to calculate the T1 Map', title='NOT POSSIBLE TO CALCULATE T1 MAP')


def checkT1(series):
    numberTIs = len(np.unique(series.InversionTimes))
    if (numberTIs > 0) and (re.search(r'molli', series.seriesID, re.IGNORECASE) or
        re.search(r'tfl', series.seriesID, re.IGNORECASE) or re.search(r'ir', series.seriesID, re.IGNORECASE)):
        return True
    else:
        return None
