from CoreModules.DeveloperTools import UserInterfaceTools
from External.ukat.mapping.t2star import T2Star
import re
#***************************************************************************
import numpy as np
FILE_SUFFIX = '_T2Star'
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
        if checkT2Star(seriesMagnitude):
            if seriesMagnitude.Multiframe:
                seriesMagnitude.sort("PerFrameFunctionalGroupsSequence.MREchoSequence.EffectiveEchoTime", "PerFrameFunctionalGroupsSequence.FrameContentSequence.InStackPositionNumber")
            else:
                seriesMagnitude.sort("EchoTime", "SliceLocation")
            te = np.unique(seriesMagnitude.EchoTimes)
            pixelArray = np.transpose(seriesMagnitude.PixelArray) # (256, 256, 60)
            reformatShape = (np.shape(pixelArray)[0], np.shape(pixelArray)[1], int(np.shape(pixelArray)[2]/len(te)), len(te))
            pixelArray = pixelArray.reshape(reformatShape) # (256, 256, 5, 12)
            # Initialise the loglin mapping object
            mapper_loglin = T2Star(pixelArray, te, method='loglin')
            # mapper_2p_exp = T2Star(pixelArray, te, method='2p_exp')
            # Extract the T2* map from the object
            t2star_loglin = mapper_loglin.t2star_map  # (256, 256, 5)
            newSeries = seriesMagnitude.new(suffix=FILE_SUFFIX)
            newSeries.write(np.transpose(t2star_loglin))  # (5, 256, 256)
            # Refresh the UI screen
            ui.refreshWeasel(new_series_name=newSeries.seriesID)
            # Display series
            newSeries.Display()
        else:
            ui.showMessageWindow(msg='The checked series doesn\'t meet the criteria to calculate the T2* Map', title='NOT POSSIBLE TO CALCULATE T2* MAP')


def checkT2Star(series):
    numberEchoes = len(np.unique(series.EchoTimes))
    if (numberEchoes > 6) and (re.search(r't2', series.seriesID, re.IGNORECASE) or re.search(r'r2', series.seriesID, re.IGNORECASE)):
        return True
    else:
        return None
