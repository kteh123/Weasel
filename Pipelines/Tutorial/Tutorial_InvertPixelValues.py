#**************************************************************************
# Inverts a number of selected images in place, 
# image by image and showing a progress bar
#***************************************************************************

def main(weasel):
    list_of_images = weasel.images()    # get the list of images checked by the user
    for i, image in list_of_images.enumerate(): # Loop over images and display a progress Bar
        weasel.progress_bar(max=list_of_images.length(), index=i+1, msg="Inverting image {}")
        image.write(-image.PixelArray)      # Invert the pixel array and overwrite existing pixel array
    weasel.close_progress_bar()   # Close the progress bar
    list_of_images.display()            # Display all images in the list in a single display