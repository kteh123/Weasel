#**************************************************************************
# Template part of a tutorial 
# Merges the series checked by the user into a new series under the same study,
# Issue 66: Error in refresh because no progress bar created. 
#***************************************************************************


def main(Weasel):
    Series = Weasel.Series()    # get the list of series checked by the user
    if Series.Empty(): return
    MergedSeries = Series.Merge(series_name='MergedSeries')
    MergedSeries.Display()
    Weasel.Refresh()
    