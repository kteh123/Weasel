#**************************************************************************
# Template part of a tutorial 
# Inverts a number of selected images and saves them in a new series, 
# image by image and showing a progress bar
# BUG: IF YOU SELECT TWO IMAGES IN DIFFERENT SERIES, THEY ARE NOT SAVED IN THE SAME SERIES
# Note another way of writing this would be to do newSeries = Images.Merge()
# and then iterating over the images in the new series. 
# This should work but the bug needs to be fixed anyway.
#***************************************************************************

def main(Weasel):
    ImageList = Weasel.images()    # get the list of images checked by the user
    if ImageList.empty: return   # if none are checked then do nothing
    newSeries = ImageList.new_parent(suffix="_Invert")
    for i, Image in ImageList.enumerate: # Loop over images and display a progress Bar
        Weasel.progress_bar(max=ImageList.length, index=i+1, msg="Inverting image {}")
        newImage = Image.new(series=newSeries)
        newImage.write(-Image.PixelArray)
    newSeries.display()            # Display all images in the list in a single display
    Weasel.refresh()
    