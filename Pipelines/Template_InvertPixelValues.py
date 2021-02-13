from CoreModules.DeveloperTools import UserInterfaceTools, Image

# Invert all pixel values and overwrite existing images
# The calculation is done slice-by-slice with an update through a progress bar

def main(Weasel):
    ui = UserInterfaceTools(Weasel)
    # Get all images in the Checkboxes
    # imageList = ui.getCheckedImages()
    imageList = Weasel.images()
    if len(imageList) == 0: return # Exit function if no images are checked
    index_bar = 0
    for image in imageList:
        # Progress Bar
        index_bar = ui.progressBar(maxNumber=len(imageList), index=index_bar, msg="Inverting and overwriting image {}", title="Invert pixel values ")
        # Invert Pixel Array
        pixelArray = - image.PixelArray
        # Overwrite - write() checks if file already exists so it writes new or overwrite
        image.write(pixelArray)
    # Close the progress bar    
    ui.closeMessageWindow()
    # Display all checked images
    Image.DisplayImages(imageList)