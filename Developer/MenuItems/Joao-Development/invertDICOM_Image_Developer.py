from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import PixelArrayDICOMTools as pixel
from Developer.DeveloperTools import GenericDICOMTools as dicom
#**************************************************************************
#Uncomment and edit the following line of code to import the function 
#containing your image processing algorithm. 
from Developer.External.imagingTools import invertAlgorithm
FILE_SUFFIX = '_Invert'
#***************************************************************************

# Slice-by-slice approach + overwrite original image
def main(objWeasel):
    # Get all images in the Checkboxes
    imagePathList = ui.getListOfAllCheckedImages(objWeasel)
    # seriesNumber, seriesUID = dicom.generateSeriesIDs(imagePathList)
    if isinstance(imagePathList, str): imagePathList = [imagePathList]
    for imagePath in imagePathList:
        # Get PixelArray from the corresponding slice
        pixelArray = pixel.getPixelArrayFromDICOM(imagePath)
        dataset = pixel.getDICOMobject(imagePath)
        # Apply Invert
        pixelArray = invertAlgorithm(pixelArray, dataset)
        # Need to set progress bars here
        # Save resulting image to DICOM (and update XML)
        pixel.overwritePixelArray(pixelArray, imagePath)
        # If the developer wishes to create a new series with the resulting images
        # outputPath = pixel.writeNewPixelArray(objWeasel, pixelArray, imagePath, FILE_SUFFIX, series_name="INVERT-WEASEL", series_id=seriesNumber, series_uid=seriesUID)
    # Refresh the UI screen
    ui.refreshWeasel(objWeasel)
    # If I want to expand the tree, then I need to re-run the refresh in the following way
    # seriesID = ui.getSeriesFromImages(objWeasel, outputPath)
    # ui.refreshWeasel(objWeasel, newSeriesName=seriesID)
    # Display series
    ui.displayImage(objWeasel, imagePathList)