from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import Image
#**************************************************************************
from Developer.External.imagingTools import invertAlgorithm
FILE_SUFFIX = '_Invert'
#***************************************************************************

# Slice-by-slice approach + overwrite original image
def main(objWeasel):
    # Get all images in the Checkboxes
    imageList = ui.getCheckedImages(objWeasel)
    index_bar = 0
    for image in imageList:
        # Get PixelArray from the corresponding slice
        pixelArray = image.PixelArray
        dataset = image.PydicomObject
        # Apply Invert
        pixelArray = invertAlgorithm(pixelArray, dataset)
        # Progress Bar
        index_bar = ui.progressBar(objWeasel, maxNumber=len(imageList), index=index_bar, msg="Inverting and overwriting image {}", title="Invert checked series ")
        # Overwrite - write() checks if file already exists so it writes new or overwrite
        image.write(pixelArray)
    # Close the progress bar    
    ui.closeMessageWindow(objWeasel)
    # Refresh the UI screen
    ui.refreshWeasel(objWeasel)
    # If I want to expand the tree, then I need to re-run the refresh in the following way
    ui.refreshWeasel(objWeasel, newSeriesName=imageList[-1].seriesID) # Still need to solve this double-call
    # Display all checked images
    Image.DisplayImages(imageList)