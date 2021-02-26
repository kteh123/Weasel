#**************************************************************************
# Template part of a tutorial 
# Inverts a number of selected images in place, 
# image by image and showing a progress bar
#***************************************************************************

def main(Weasel):
    ImageList = Weasel.images()    # get the list of images checked by the user
    for i, Image in ImageList.enumerate: # Loop over images and display a progress Bar
        Weasel.progress_bar(max=ImageList.length, index=i+1, msg="Inverting image {}", title="Invert pixel values ")
        Image.write(-Image.PixelArray)      # Invert the pixel array and overwrite existing pixel array
    Weasel.close_progress_bar()   # Close the progress bar
    ImageList.display()            # Display all images in the list in a single display