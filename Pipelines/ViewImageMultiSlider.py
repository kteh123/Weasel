
from Displays.ImageViewers.ImageViewer import ImageViewer as imageViewer

import logging
logger = logging.getLogger(__name__)

__author__ = "Steve Shillitoe"
#September 2021



def main(weasel):
        """Creates a subwindow that displays a DICOM image. Either executed using the 
        'View Image' Menu item in the Tools menu or by double clicking the Image name 
        in the DICOM studies tree view."""
        try:
            logger.info("viewImage.main called")

            if weasel.series() != []: 
                for series in weasel.objXMLReader.checkedSeriesList:
                    id = weasel.objXMLReader.objectID(series)
                    imageList = [image.find('name').text for image in series]
                    imageViewer(weasel, id[0], id[1], id[2], imageList)
            elif weasel.images() != []:
                for image in weasel.objXMLReader.checkedImageList:
                    id = weasel.objXMLReader.objectID(image)
                    imageViewer(weasel, id[0], id[1], id[2], id[3], singleImageSelected=True)
                        
        except Exception as e:
            print('Error in ViewImageMultiSlider.main: ' + str(e))
            logger.error('Error in ViewImageMultiSlider.main: ' + str(e))
