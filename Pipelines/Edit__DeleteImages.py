"""
Deletes the selected images showing progress with a status bar.
"""

def main(weasel):
    list_of_images = weasel.images()                 # get the list of images checked by the user
    for i, image in enumerate(list_of_images):      # Loop over Images in the list and display a progress Bar
        weasel.progress_bar(max=len(list_of_images), index=i+1, msg="Deleting images {}")
        image.delete()                     # Delete the image  
    weasel.refresh()                
    