from CoreModules.DeveloperTools import UserInterfaceTools, Image
#**************************************************************************
from CoreModules.imagingTools import gaussianFilter
FILE_SUFFIX = '_Gaussian'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True


def main(objWeasel):
    ui = UserInterfaceTools(objWeasel)
    # In this case, the user introduces the sigma value intended for the gaussian filter
    inputDict = {"Standard Deviation":"float"}
    paramList = ui.inputWindow(inputDict, title="Input Parameters for the Gaussian Filter")
    if paramList is None: return # Exit function if the user hits the "Cancel" button
    standard_deviation_filter = paramList[0]
    # Get checked images
    imageList = ui.getCheckedImages()
    if imageList is None: return # Exit function if no images are checked
    # Create new Series where the resulting images will be saved
    newSeries = Image.newSeriesFrom(imageList, suffix=FILE_SUFFIX)
    for image in imageList:
        # Create new image based on the current image
        newImage = image.new(series=newSeries)
        # Get PixelArray from the selected images
        pixelArray = image.PixelArray
        # Apply Gaussian Filter
        pixelArray = gaussianFilter(pixelArray, standard_deviation_filter)
        # Save as individual image into new Series
        newImage.write(pixelArray, series=newSeries)
    # Refresh the UI screen
    ui.refreshWeasel(new_series_name=newSeries.seriesID)
    # Display resulting image
    newSeries.DisplaySeries()
    