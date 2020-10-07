import Developer.MenuItems.developerToolsModule as tool
#**************************************************************************
#Added by third party developer to the template module. 
#The function containing the image processing algorithm must be given the 
#generic name, funcAlgorithm
from Developer.External.imagingTools import invertAlgorithm
FILE_SUFFIX = '_Invert'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True

# Slice-by-slice approach + overwrite original image
def main(objWeasel):
    # Get all images of the Selected Series
    imagePathList = tool.getImagePathList(objWeasel)
    for imagePath in imagePathList:
        # Get PixelArray from the corresponding slice
        pixelArray = tool.getPixelArrayFromDICOM(imagePath)
        dataset = tool.getDICOMobject(imagePath)
        # Apply Invert
        pixelArray = invertAlgorithm(pixelArray, dataset)
        # Need to set progress bars here
        # Save resulting image to DICOM (and update XML)
        tool.overwritePixelArray(pixelArray, imagePath)
    # Display series
    tool.displayImage(objWeasel, imagePathList)