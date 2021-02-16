#**************************************************************************
# Template part of a tutorial 
# Inverts a number of selected images in place, 
# image by image and showing a progress bar
#***************************************************************************

def main(Weasel):
    ImageList = Weasel.Images()    # get the list of images checked by the user
    for i, Image in ImageList.Enumerate(): # Loop over images and display a progress Bar
        Weasel.ProgressBar(max=ImageList.Count(), index=i+1, msg="Inverting image {}", title="Invert pixel values ")
        Image.write(-Image.PixelArray)      # Invert the pixel array and overwrite existing pixel array
    Weasel.CloseProgressBar()   # Close the progress bar
    ImageList.Display()            # Display all images in the list in a single display