#**************************************************************************
# Creates a copy of the checked images in the same series
# showing progress with a status bar
#***************************************************************************

def main(weasel):

    list_of_images = weasel.images()                 # get the list of series checked by the user
    for i, image in list_of_images.enumerate():      # Loop over Series in the list and display a progress Bar
        weasel.progress_bar(max=list_of_images.length(), index=i+1, msg="Copying images {}")
        image.copy()                # Copy the image 
    weasel.refresh()                # Refresh weasel

    