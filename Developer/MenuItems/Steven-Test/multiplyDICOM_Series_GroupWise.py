from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import Series, Image
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
    newSeries = Series.newSeriesFrom(seriesList[0], suffix=FILE_SUFFIX)
    outputArray = seriesList[0].PixelArray
    for nextSeries in seriesList[1:]: # tupleSeries
        # Multiply inside the loop with the previous result
        outputArray *= nextSeries.PixelArray
    newSeries.write(outputArray)
    # Refresh the UI screen
    ui.refreshWeasel(objWeasel, newSeriesName=newSeries.seriesID)
    # Display series
    newSeries.DisplaySeries()


def checkDimensionsMatch(seriesList, dimensions):
    for series in seriesList:
        if series.Dimensions != dimensions: # [(128,128), (256,256)] Try to be as close to DICOM as possible - Rows and Columns
            return None
    return True
