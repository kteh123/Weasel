#**************************************************************************
# Thresholds a number of selected images into a new series
#***************************************************************************

def main(weasel):
    list_of_images = weasel.images()    # get the list of images checked by the user
    if len(list_of_images) == 0: return   # if the user cancels then exit
    series = list_of_images.new_parent(suffix="_Thresholded")
    for i, image in enumerate(list_of_images): # Loop over images and display a progress Bar
        weasel.progress_bar(max=len(list_of_images), index=i+1, msg="Thresholding image {}")
        image.copy(series=series).write(-image.PixelArray)
    series.display()            # Display all images in the list in a single display
    