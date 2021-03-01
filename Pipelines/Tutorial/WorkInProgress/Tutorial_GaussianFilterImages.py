#**************************************************************************
# Template part of a tutorial 
# Applies a Gaussian filter to checked images and saves them in a new series, 
# image by image and showing a progress bar. 
# Filter settings are derived through user input (COMING).
#***************************************************************************

from CoreModules.imagingTools import gaussianFilter

def main(Weasel):
    Images = Weasel.images(msg = "Please select the images to filter")     
    if Images.empty: return    
    cancel, width = Weasel.user_input( 
        {"type":"float", "label":"Filter width in pixels", "default":1.0}, 
        title="Gaussian filter settings")
    if cancel: return
    Filtered = Images.merge(series_name='Gaussian Filter') 
    for i, Image in Filtered.enumerate: 
        Weasel.progress_bar(max=Filtered.length, index=i+1, msg="Filtering image {}")
        PixelArray = gaussianFilter(Image.PixelArray, width)
        Image.write(PixelArray)
    Filtered.display()            
    Weasel.refresh()