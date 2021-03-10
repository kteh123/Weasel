#**************************************************************************
# Template part of a tutorial 
# Merges the Images checked by the user into a new series under the same study,
# Preserving a copy of the original images in the original series
#***************************************************************************

def main(weasel):
    
    list_of_images = weasel.images() 
    if list_of_images.empty(): return
    list_of_images.copy().merge(series_name='MergedSeries')
    weasel.refresh()

"""
def main(weasel):
    list_of_images = weasel.images()                 
    for i, image in list_of_images.enumerate():      
        weasel.progress_bar(max=list_of_images.length(), index=i+1, msg="Copying images {}")
        list_of_images.image(i) = image.copy()  
    list_of_images.merge(series_name='MergedSeries').display()               
    weasel.refresh() 
"""               
    