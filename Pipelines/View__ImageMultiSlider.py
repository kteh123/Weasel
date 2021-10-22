
from Displays.ImageViewers.ImageViewer import ImageViewer as imageViewer

import logging
logger = logging.getLogger(__name__)

__author__ = "Steve Shillitoe"
#September 2021


def main(weasel):
    try:
        checked_series = weasel.series()
        if checked_series != []: 
            for series in checked_series:
                imageViewer(weasel, series)
        else:
            for image in weasel.images(msg = 'No images checked'):
                imageViewer(weasel, image)
    except (IndexError, AttributeError):
        weasel.information(msg="Select either a series or an image", title="View DICOM header")
    except Exception as e:
            print('Error in View_ImageMultiSlider.main: ' + str(e))
            logger.error('Error in View_ImageMultiSlider.main: ' + str(e))               
