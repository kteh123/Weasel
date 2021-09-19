
from Displays.ImageViewers.ImageViewer import ImageViewer as imageViewer

import logging
logger = logging.getLogger(__name__)

__author__ = "Steve Shillitoe"
#September 2021


def main(weasel):
    checked_series = weasel.series()
    if checked_series != []: 
        for series in checked_series:
            imageViewer(weasel, series)
    else:
        for image in weasel.images(msg = 'No images checked'):
            imageViewer(weasel, image)
                    
