def main(weasel):

    series = weasel.series()
    if series == []: 
        weasel.images(msg = 'No images checked').display()
    else:
        series.display()