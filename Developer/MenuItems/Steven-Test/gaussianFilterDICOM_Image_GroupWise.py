from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import Series, Image
#**************************************************************************
from Developer.External.imagingTools import gaussianFilter
FILE_SUFFIX = '_Gaussian'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True


def main(objWeasel):
    # In this case, the user introduces the sigma value intended for the gaussian filter
    inputDict = {"Standard Deviation":"float"}
    paramList = ui.inputWindow(inputDict, title="Input Parameters for the Gaussian Filter")
    if paramList is None: return # Exit function if the user hits the "Cancel" button
    standard_deviation_filter = paramList[0]
    # Get checked series
    seriesList = ui.getCheckedSeries(objWeasel)
    for series in seriesList:
        # Create a new Series for each Series checked
        newSeries = series.new(series_name="GaussianFiltered_"+str(series.seriesID))
        # Get series' PixelArray
        pixelArray = series.PixelArray
        # Apply Gaussian filter
        pixelArray = gaussianFilter(pixelArray, standard_deviation_filter)
        # Save resulting PixelArray into the new Series
        newSeries.write(pixelArray)
    # Refresh the UI screen
    ui.refreshWeasel(objWeasel, newSeriesName=newSeries.seriesID)
    # Display resulting image
    newSeries.DisplaySeries() 
