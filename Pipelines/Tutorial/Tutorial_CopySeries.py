#**************************************************************************
# Template part of a tutorial 
# Creates a copy of the checked series
# showing progress with a status bar 
#***************************************************************************

def main(Weasel):
    List = Weasel.series()                  # get the list of series checked by the user
    for i, Series in List.enumerate:      # Loop over Series in the list and display a progress Bar
        Weasel.progress_bar(max=List.length, index=i+1, msg="Copying series {}")
        Series.copy().Display()     # Copy and Display the new series  
    Weasel.refresh()                # Refresh weasel
    