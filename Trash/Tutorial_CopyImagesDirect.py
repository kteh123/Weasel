#**************************************************************************
# Creates a copy of the checked images in the same series
# in shorthand notation without a progress bar
#***************************************************************************

def main(weasel):

    weasel.images().copy()
    weasel.refresh()                

    