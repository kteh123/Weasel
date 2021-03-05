#**************************************************************************
# Merges the series checked by the user 
# into a new series under the same study,
# Issue 79: Nothing happens.  
#***************************************************************************

def main(weasel):

    list_of_series = weasel.series() 
    if list_of_series.empty: return
    list_of_series.merge(series_name='MergedSeries').display()
    weasel.refresh()
    