"""
Displays a DICOM image or series with ROI drawing tools.
"""

from Displays.ImageViewers.ImageViewerROI import ImageViewerROI as imageViewerROI
import logging
logger = logging.getLogger(__name__)

__author__ = "Steve Shillitoe"

def main(weasel):
    try:
        logger.info("viewImage.main called")
        checked_series = weasel.series()
        if checked_series != []: 
            for series in checked_series:
                imageViewerROI(weasel, series)
        else: 
            for image in weasel.images():
                imageViewerROI(weasel, image)
    except (IndexError, AttributeError):
        weasel.information(msg="Select either a series or an image", title="View DICOM header")                
    except Exception as e:
        print('Error in View_ImageMultiSliderROI.main: ' + str(e))
        logger.error('Error in View_ImageMultiSliderROI.main: ' + str(e))
