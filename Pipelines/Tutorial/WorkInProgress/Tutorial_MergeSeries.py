#**************************************************************************
# Template part of a tutorial 
# Merges the series checked by the user into a new series under the same study,
# Issue 66: Error in refresh because no progress bar created. 
#***************************************************************************


def main(Weasel):
    Series = Weasel.series()    # get the list of series checked by the user
    if Series.empty: return
    MergedSeries = Series.merge(series_name='MergedSeries')
    MergedSeries.display()
    Weasel.refresh()
    