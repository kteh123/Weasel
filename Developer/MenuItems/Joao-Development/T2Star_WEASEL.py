from Developer.DeveloperTools import UserInterfaceTools
from Developer.External.ukat.mapping.t2star import T2Star
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

    for series in seriesList:
        seriesMagnitude = series.getMagnitude
        if checkT2Star(seriesMagnitude):
            seriesMagnitude.sort("SliceLocation")
            seriesMagnitude.sort("EchoTime")
            te = np.unique(seriesMagnitude.EchoTimes)
            image = np.transpose(seriesMagnitude.PixelArray)
            reformatShape = (np.shape(image)[0], np.shape(image)[1], int(np.shape(image)[2]/len(te)), len(te))
            image = image.reshape(reformatShape)
            # Initialise the loglin mapping object
            mapper_loglin = T2Star(image, te, method='loglin')
            # mapper_2p_exp = T2Star(image, te, method='2p_exp')
            # Extract the T2* map from the object
            t2star_loglin = mapper_loglin.t2star_map
            newSeries = seriesMagnitude.new(suffix=FILE_SUFFIX)
            newSeries.write(t2star_loglin)

    # Refresh the UI screen
    ui.refreshWeasel(new_series_name=newSeries.seriesID)
    # Display series
    newSeries.DisplaySeries()


def checkT2Star(series):
    numberEchoes = len(np.unique(series.EchoTimes))
    if (numberEchoes >  6) and (re.match(".*t2.*", series.seriesID.lower()) or re.match(".*r2.*", series.seriesID.lower())):
        return True
    else:
        return None
