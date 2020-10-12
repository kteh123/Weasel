from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import PixelArrayDICOMTools as pixel
#**************************************************************************
#Uncomment and edit the following line of code to import the function 
#containing your image processing algorithm. 
from Developer.External.imagingTools import invertAlgorithm
FILE_SUFFIX = '_Invert'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True

# Slice-by-slice approach + overwrite original image
def main(objWeasel):
    # Get all images of the Selected Series
    imagePathList = ui.getAllSelectedImages(objWeasel)
    if isinstance(imagePathList, str):
        pixelArray = pixel.getPixelArrayFromDICOM(imagePathList)
        dataset = pixel.getDICOMobject(imagePathList)
        # Apply Invert
        pixelArray = invertAlgorithm(pixelArray, dataset)
        # Need to set progress bars here
        # Save resulting image to DICOM (and update XML)
        pixel.overwritePixelArray(pixelArray, imagePathList)
    else:
        for imagePath in imagePathList:
            # Get PixelArray from the corresponding slice
            pixelArray = pixel.getPixelArrayFromDICOM(imagePath)
            dataset = pixel.getDICOMobject(imagePath)
            # Apply Invert
            pixelArray = invertAlgorithm(pixelArray, dataset)
            # Need to set progress bars here
            # Save resulting image to DICOM (and update XML)
            pixel.overwritePixelArray(pixelArray, imagePath)
    # Display series
    ui.displayImage(objWeasel, imagePathList)