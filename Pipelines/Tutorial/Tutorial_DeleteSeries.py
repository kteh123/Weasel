#**************************************************************************
# Template part of a tutorial 
# Deletes the selected series
# showing progress with a status bar 
#***************************************************************************

def main(weasel):
    list_of_series = weasel.series()                
    for i, series in list_of_series.enumerate():   
        weasel.progress_bar(max=list_of_series.length(), index=i+1, msg="Deleting series {}")
        series.delete()                       
    weasel.refresh()               
    