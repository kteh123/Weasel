#**************************************************************************
# Template part of a tutorial 
# Inverts a number of selected images in place, 
# series by series and showing a progress bar
#***************************************************************************

def main(Weasel):
    SeriesList = Weasel.series()    # get the list of all series checked by the user
    for i, Series in SeriesList.enumerate: # Loop over series and display a progress Bar
        Weasel.progress_bar(max=SeriesList.length, index=i+1, msg="Inverting series {}", title="Invert pixel values ")
        Series.write(-Series.PixelArray)     # Invert the pixel array and overwrite existing pixel array
    Weasel.close_progress_bar()   # Close the progress bar
    SeriesList.display()        # Display all Series in the list