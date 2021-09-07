
    
#**************************************************************************
# Merges the series checked by the user 
# into a new series under the same study
#***************************************************************************

def main(weasel):

    list_of_series = weasel.series() 
    if len(list_of_series) <= 1: return
    list_of_series.copy().merge(series_name='MergedSeries')
    weasel.refresh()
    