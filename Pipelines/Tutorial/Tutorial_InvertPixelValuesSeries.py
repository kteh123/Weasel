#**************************************************************************
# Template part of a tutorial 
# Inverts a number of selected images in place, 
# series by series and showing a progress bar
#***************************************************************************

def main(Weasel):
    SeriesList = Weasel.Series()    # get the list of all series checked by the user
    for i, Series in SeriesList.Enumerate(): # Loop over series and display a progress Bar
        Weasel.ProgressBar(max=SeriesList.Count(), index=i+1, msg="Inverting series {}", title="Invert pixel values ")
        Series.write(-Series.PixelArray)     # Invert the pixel array and overwrite existing pixel array
    Weasel.CloseProgressBar()   # Close the progress bar
    SeriesList.Display()        # Display all Series in the list