from Displays.ImageViewers.ImageViewerROI import ImageViewerROI as imageViewerROI


import logging
logger = logging.getLogger(__name__)

__author__ = "Steve Shillitoe"
#September 2021


def main(weasel):
        """Displays a DICOM image or series with ROI drawing tools"""
        try:
            logger.info("viewImage.main called")

            checked_series = weasel.series()
            if checked_series != []: 
                for series in checked_series:
                    imageViewerROI(weasel, series)
            else: 
                for image in weasel.images():
                    imageViewerROI(weasel, image)
                        
        except Exception as e:
            print('Error in ViewImageMultiSlider.main: ' + str(e))
            logger.error('Error in ViewImageMultiSlider.main: ' + str(e))
