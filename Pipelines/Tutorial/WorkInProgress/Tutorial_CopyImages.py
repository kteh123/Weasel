#**************************************************************************
# Template part of a tutorial 
# Creates a copy of the checked images in the same series
# showing progress with a status bar 
# ISSUE 63: Saves the copies in a new series
#***************************************************************************

def main(Weasel):
    Images = Weasel.images()                 # get the list of series checked by the user
    newSeries = Images.new_parent(suffix="_Copy")
    for i, Image in Images.enumerate:      # Loop over Series in the list and display a progress Bar
        Weasel.progress_bar(max=Images.length, index=i+1, msg="Copying images {}")
        Image.copy(series=newSeries)                # Copy the new image  
    Weasel.refresh()                # Refresh weasel

    