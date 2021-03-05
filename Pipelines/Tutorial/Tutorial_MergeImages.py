#**************************************************************************
# Template part of a tutorial 
# Merges the Images checked by the user into a new series under the same study,
#***************************************************************************


def main(weasel):
    
    list_of_images = weasel.images() 
    if list_of_images.empty(): return
    list_of_images.merge(series_name='MergedSeries').display()
    weasel.refresh()
    