"""
Creates a copy of the checked images in the same series showing progress with a status bar.
"""

def main(weasel):

    list_of_images = weasel.images()                 # get the list of series checked by the user
    weasel.progress_bar(max=len(list_of_images), msg="Copying images..")
    for i, image in enumerate(list_of_images):      # Loop over Series in the list and display a progress Bar
        weasel.update_progress_bar(index=i+1)
        image.copy()                # Copy the image
    weasel.close_progress_bar()
    weasel.refresh()                # Refresh weasel

#   This works too but does not show progress:
#   weasel.images().copy()

