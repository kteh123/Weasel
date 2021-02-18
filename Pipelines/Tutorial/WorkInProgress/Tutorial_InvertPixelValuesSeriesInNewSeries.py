#**************************************************************************
# Template part of a tutorial 
# Inverts the images in a number of selected series
# and saves them in a new series, 
# series by series and showing a progress bar
#***************************************************************************

def main(Weasel):
    List = Weasel.Series()      # get the list of series checked by the user
    if List.Empty(): return     # if none are checked then do nothing
    for i, Series in List.Enumerate():              # Loop over Series in the list and display a progress Bar
        Weasel.ProgressBar(max=List.Count(), index=i+1, msg="Inverting series {}", title="Invert pixel values ")
        newSeries = Series.new(suffix="_Invert")    # Derive a new series
        newSeries.write(-Series.PixelArray)         # Write the results in the new series
    newSeries.Display()     # Display the new series
    Weasel.CloseProgressBar()   # Close the progress bar
    Weasel.Refresh(new_series_name=newSeries.seriesID) # Refresh weasel
    