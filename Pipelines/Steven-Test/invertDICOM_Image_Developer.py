from CoreModules.DeveloperTools import UserInterfaceTools, Image
#**************************************************************************
from CoreModules.imagingTools import invertAlgorithm
FILE_SUFFIX = '_Invert'
#***************************************************************************

# Slice-by-slice approach + overwrite original image
def main(objWeasel):
    ui = UserInterfaceTools(objWeasel)
    # Get all images in the Checkboxes
    imageList = ui.getCheckedImages()
    if imageList is None: return # Exit function if no images are checked
    index_bar = 0
    for image in imageList:
        # Get PixelArray from the corresponding slice
        pixelArray = image.PixelArray
        dataset = image.PydicomObject
        # Apply Invert
        pixelArray = invertAlgorithm(pixelArray, dataset)
        # Progress Bar
        index_bar = ui.progressBar(maxNumber=len(imageList), index=index_bar, msg="Inverting and overwriting image {}", title="Invert checked series ")
        # Overwrite - write() checks if file already exists so it writes new or overwrite
        image.write(pixelArray)
    # Close the progress bar    
    ui.closeMessageWindow()
    # Refresh the UI screen
    ui.refreshWeasel(new_series_name=imageList[-1].seriesID)
    # Display all checked images
    imageList[0].display()
    #imageList[0].saveNIFTI()
    #Image.DisplayImages(imageList)
