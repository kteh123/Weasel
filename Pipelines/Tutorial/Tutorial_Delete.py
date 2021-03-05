#**************************************************************************
# Template part of a tutorial 
# Deletes the selected images
# showing progress with a status bar 
# ISSUE 60: Does not close window if image on display
# ISSUE 61: Deleting images is very slow
#***************************************************************************

def main(weasel):
    list_of_images = weasel.images()                 # get the list of images checked by the user
    for i, image in list_of_images.enumerate():      # Loop over Images in the list and display a progress Bar
        weasel.progress_bar(max=list_of_images.length(), index=i+1, msg="Deleting images {}")
        image.delete()                     # Delete the image  
    weasel.refresh()                
    