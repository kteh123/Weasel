
    
#**************************************************************************
# Creates a copy of all of the checked series
# as siblings in the same study
# showing progress with a status bar 
# and displaying the copied series
#***************************************************************************

def main(weasel):
    list_of_series = weasel.series()                  # get the list of series checked by the user
    for i, series in enumerate(list_of_series):      # Loop over Series in the list and display a progress Bar
        weasel.progress_bar(max=len(list_of_series), index=i+1, msg="Copying series {}")
        series.copy().display()     # Copy and display the new series  
    weasel.refresh()                # Refresh weasel
    