#**************************************************************************
# Template part of a tutorial 
# Applies a Gaussian filter to checked images and saves them in a new series, 
# image by image and showing a progress bar. 
# Filter settings are derived through user input (COMING).
#***************************************************************************

from CoreModules.imagingTools import gaussianFilter

def main(Weasel):
    Images = Weasel.images()     # get the list of images checked by the user
    if Images.empty: return    # if none are checked then do nothing
    Filtered = Images.merge(series_name='Gaussian Filter') # merge the images into a new series
    for i, Image in Filtered.enumerate: # Loop over images and display a progress Bar
        Weasel.progress_bar(max=Filtered.length, index=i+1, msg="Filtering image {}")
        PixelArray = gaussianFilter(Image.PixelArray, 3)
        Image.write(PixelArray)
    Filtered.display()            # Display all images in the new series in a single display
    Weasel.refresh()