#**************************************************************************
# Template part of a tutorial 
# Creates a copy of the checked series
# showing progress with a status bar 
# WORKS APART FROM THE DISPLAY() ISSUE
#***************************************************************************

def main(Weasel):
    List = Weasel.Series()                  # get the list of series checked by the user
    for i, Series in List.Enumerate():      # Loop over Series in the list and display a progress Bar
        Weasel.ProgressBar(max=List.Count(), index=i+1, msg="Copying series {}")
        newSeries = Series.Copy()
        newSeries.Display()     # Display the new series
    Weasel.Refresh()            # Refresh weasel
    