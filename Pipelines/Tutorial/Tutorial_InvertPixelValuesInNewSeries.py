#**************************************************************************
# Template part of a tutorial 
# Inverts a number of selected images and saves them in a new series, 
# image by image and showing a progress bar
# BUG: IF YOU SELECT TWO IMAGES IN DIFFERENT SERIES, THEY ARE NOT SAVED IN THE SAME SERIES
# Note another way of writing this would be to do newSeries = Images.Merge()
# and then iterating over the images in the new series. 
# This should work but the bug needs to be fixed anyway.
#***************************************************************************

def main(weasel):
    list_of_images = weasel.images()    # get the list of images checked by the user
    if len(list_of_images) == 0: return   # if the user cancels then exit
    series = list_of_images.new_parent(suffix="_Invert")
    for i, image in enumerate(list_of_images): # Loop over images and display a progress Bar
        weasel.progress_bar(max=len(list_of_images), index=i+1, msg="Inverting image {}")
        image.copy(series=series).write(-image.PixelArray)
    series.display()            # Display all images in the list in a single display
    weasel.refresh()
    