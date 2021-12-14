"""
Displays a subwindow in the Weasel GUI containing a viewer of the selected images.

If a series is selected, it displays a subwindow per series containing a slider (or multiple) that allows to scroll through the images belonging to the series.
"""

from Displays.ImageViewers.ImageViewer import ImageViewer as imageViewer
import logging
logger = logging.getLogger(__name__)

__author__ = "Steve Shillitoe"

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
