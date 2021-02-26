#**************************************************************************
# Template part of a tutorial 
# Inverts the images in a number of selected series
# and saves them in a new series, 
# series by series and showing a progress bar
# BUG: Throws an error
#***************************************************************************

def main(Weasel):
    List = Weasel.series()      # get the list of series checked by the user
    for i, Series in List.enumerate:              # Loop over Series in the list and display a progress Bar
        Weasel.progress_bar(max=List.length, index=i+1, msg="Inverting series {}")
        newSeries = Series.new(suffix="_Invert")    # Derive a new series
        newSeries.write(-Series.PixelArray)         # Write the results in the new series
        newSeries.display()     # Display the new series 
    Weasel.refresh() # Refresh weasel
    