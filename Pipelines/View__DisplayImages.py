"""
Displays a subwindow in the Weasel GUI containing a viewer of the selected images.
"""
    
def main(weasel):
    series = weasel.series()
    if series == []: 
        weasel.images(msg = 'No images checked').display()
    else:
        series.display()