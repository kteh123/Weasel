from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import PixelArrayDICOMTools as pixel
import operator
from functools import reduce
FILE_SUFFIX = '_Multiplied'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True


def main(objWeasel):
    # Get all series in the Checkboxes
    seriesList = ui.getListOfCheckedSeries(objWeasel)
    # dictionarySelected = ui.getDictOfCheckedItems(objWeasel)
    stackedImages = []
    for subject, study, series in seriesList:
        imagePathList = ui.getImagesFromSeries(objWeasel, study, series)
        imageArray = pixel.getPixelArrayFromDICOM(imagePathList)
        stackedImages.append(imageArray)
    pixelArray = reduce(operator.mul, stackedImages)
    outputhPath = pixel.writeNewPixelArray(objWeasel, pixelArray, imagePathList, FILE_SUFFIX) # tuple in place of imagePathList
    # Refresh the UI screen
    ui.refreshWeasel(objWeasel)
    # Display series
    ui.displayImage(objWeasel, outputhPath) # tuple in place of outputPath