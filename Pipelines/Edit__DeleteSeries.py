def isEnabled(weasel):
    return True
    
#**************************************************************************
# Template part of a tutorial 
# Deletes the selected series
# showing progress with a status bar 
#***************************************************************************

def main(weasel):
    list_of_series = weasel.series()                
    for i, series in enumerate(list_of_series):   
        weasel.progress_bar(max=len(list_of_series), index=i+1, msg="Deleting series {}")
        series.delete()                       
    weasel.refresh()               
    