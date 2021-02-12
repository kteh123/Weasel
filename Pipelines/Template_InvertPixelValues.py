from CoreModules.DeveloperTools import UserInterfaceTools, Image

# Slice-by-slice approach + overwrite original image
def main(Weasel):
    ui = UserInterfaceTools(Weasel)
    # Get all images in the Checkboxes
    imageList = ui.getCheckedImages()
    if imageList is None: return # Exit function if no images are checked
    index_bar = 0
    for image in imageList:
        # Progress Bar
        index_bar = ui.progressBar(maxNumber=len(imageList), index=index_bar, msg="Inverting and overwriting image {}", title="Invert checked series ")
        # Invert Pixel Array
        pixelArray = - image.PixelArray
        # Overwrite - write() checks if file already exists so it writes new or overwrite
        image.write(pixelArray)
    # Close the progress bar    
    ui.closeMessageWindow()
    # Refresh the UI screen
    ui.refreshWeasel(new_series_name=imageList[-1].seriesID)
    # Display all checked images
    Image.DisplayImages(imageList)