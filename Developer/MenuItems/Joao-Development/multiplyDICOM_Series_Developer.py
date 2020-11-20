from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import Series, Image
FILE_SUFFIX = '_Multiplied'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True


def madddin(objWeasel):
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
    ui.refreshWeasel(objWeasel)
    # Display series
    newSeries.DisplaySeries()


def main(objWeasel):
    # Get all series in the Checkboxes
    seriesList = ui.getCheckedSeries(objWeasel)
    dimensions = seriesList[0].Dimensions
    # If all dimensions are not the same then return error
    if checkDimensionsMatch(seriesList, dimensions) is None: return
    ######## SLICE-BY-SLICE ########
    # seriesNumber, seriesUID = dicom.generateSeriesIDs(imagePathList)
    
    #nr_of_images = SeriesList[0].numberChildren
    #for i in range(nr_of_images):
    #    outputArray = seriesList[0].children[i].PixelArray
    #    for series in seriesList[1:]
    #        outputArray *= series.children[i].PixelArray
    #    newSeries.child[i].PixelArray(OutputArray)
    newSeries = Series.newSeriesFrom(seriesList[0], suffix=FILE_SUFFIX)
    nrOfImages = seriesList[0].numberChildren
    for i in range(nrOfImages):
        newImage = Image.newImageFrom(seriesList[0].children[i], series=newSeries)
        outputArray = seriesList[0].children[i].PixelArray
        for series in seriesList[1:]:
            outputArray *= series.children[i].PixelArray
        newImage.write(outputArray, series=newSeries)
    # Refresh the UI screen
    ui.refreshWeasel(objWeasel)
    # Display series
    newSeries.DisplaySeries()

        


def checkDimensionsMatch(seriesList, dimensions):
    for series in seriesList:
        if series.Dimensions != dimensions: # [(128,128), (256,256)] Try to be as close to DICOM as possible - Rows and Columns
            return None
    return True
