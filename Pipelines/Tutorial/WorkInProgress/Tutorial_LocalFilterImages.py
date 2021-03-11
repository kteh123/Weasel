#**************************************************************************
# Template part of a tutorial 
# Applies a local filter to checked images and saves them in a new series, 
# image by image and showing a progress bar. 
# Filter settings are derived through user input.
#***************************************************************************

import scipy.ndimage as ndimage
from scipy.signal import wiener

def main(weasel):

    # Get images checked by the user

    list_of_images = weasel.images(msg = "Please select the images to filter")     
    if list_of_images.empty(): return 

    # Get user input: type of filter and size

    filters = ["Gaussian", "Uniform", "Median", "Maximum", "Wiener"]
    cancel, tmp, filter, size = weasel.user_input(
        {"type":"listview", "label":"Which filter?", "list":filters},
        {"type":"dropdownlist", "label":"Which filter?", "list":filters, "default": 2},
        {"type":"integer", "label":"Filter size in pixels", "default":20}, 
        title = "Filter settings")
    if cancel: return

    # Apply the filter and save results in a new series

    # filtered = list_of_images.copy().merge(series_name='Filter') 

    for i, image in list_of_images.enumerate():
        weasel.progress_bar(max=list_of_images.length(), index=i+1, msg="Filtering image {}")
        if filter == "Gaussian":
            image.write(-ndimage.gaussian_filter(image.PixelArray, sigma=size))
        elif filter == "Uniform":
            image.write(ndimage.uniform_filter(image.PixelArray, size=size))
        elif filter == "Median":
            image.write(ndimage.median_filter(image.PixelArray, size))
        elif filter == "Maximum":
            image.write(ndimage.maximum_filter(image.PixelArray, size=size))
        elif filter == "Wiener":
            image.write(wiener(image.PixelArray, (size, size)))

    # Display the new series and refresh weasel
  
    list_of_images.display()            
    weasel.refresh()