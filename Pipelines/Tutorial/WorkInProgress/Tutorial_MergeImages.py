#**************************************************************************
# Template part of a tutorial 
# Merges the Images checked by the user into a new series under the same study,
# Issue 66: Error in refresh because no progress bar created. 
#***************************************************************************


def main(Weasel):
    Images = Weasel.Images()    # get the list of images checked by the user
    if Images.Empty(): return
    MergedSeries = Images.Merge(series_name='MergedSeries')
    MergedSeries.Display()
    Weasel.Refresh()
    