#**************************************************************************
# Template part of a tutorial 
# Creates a copy of the checked images in the same series
# showing progress with a status bar 
# ISSUE 63: Saves the copies in a new series
#***************************************************************************

# What's the real purpose in the code below? The code below saves a copy of each image in a new series.
def main(Weasel):
    Images = Weasel.Images()                 # get the list of series checked by the user
    for i, Image in Images.Enumerate():      # Loop over Series in the list and display a progress Bar
        Weasel.ProgressBar(max=Images.Count(), index=i+1, msg="Copying images {}")
        Image.Copy()                # Copy and Display the new image  
    Weasel.Refresh()                # Refresh weasel

# In order to save the each copy of an Image into a new series, this should probably be the method?
# def main(Weasel):
    # Images = Weasel.Images()                 # get the list of series checked by the user
    # newSeries = Images.NewParent(suffix="_Copy")
    # for i, Image in Images.Enumerate():      # Loop over Series in the list and display a progress Bar
        # Weasel.ProgressBar(max=Images.Count(), index=i+1, msg="Copying images {}")
        # Image.Copy(series=newSeries)            # Copy and Display the new image  
    # Weasel.Refresh()                            # Refresh weasel


# Still need to consider creating copies of each Image and save in the same series
    