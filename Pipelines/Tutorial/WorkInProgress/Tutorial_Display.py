#**************************************************************************
# Template part of a tutorial 
# Displays the checked images and series
#***************************************************************************

def main(weasel):               
    for image in weasel.images(): 
        image.display()                 
    for series in weasel.series():      
        series.display()              

    