#**************************************************************************
# Template part of a tutorial 
# Deletes the selected images
# showing progress with a status bar 
# ISSUE 60: Does not close window if image on display
# ISSUE 61: Deleting images is very slow
# ISSUE 62: Deleting all images in a series does not delete the series
#***************************************************************************

def main(Weasel):
    List = Weasel.images()                 # get the list of images checked by the user
    for i, Image in List.enumerate:      # Loop over Images in the list and display a progress Bar
        Weasel.progress_bar(max=List.length, index=i+1, msg="Deleting images {}")
        Image.delete()                     # Delete the image  
    Weasel.refresh()                
    