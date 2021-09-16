#<<<<<<< HEAD
#import Displays.ImageViewers.ImageViewerROI as imageViewerROI
#=======
from Displays.ImageViewers.ImageViewerROI import ImageViewerROI as imageViewerROI
#>>>>>>> cd8da5f6f3310a380f59879ed6c459feba97e49e

import logging
from PyQt5.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)

__author__ = "Steve Shillitoe"
#September 2021


def main(objWeasel):
        """Creates a subwindow that displays a DICOM image. 
        
        Either executed using the 
        'View Image' Menu item in the Tools menu or by double clicking the Image name 
        in the DICOM studies tree view."""
        try:
            logger.info("viewImage.main called")
            if objWeasel.objXMLReader.isAnItemChecked() == False:
                raise NoTreeViewItemSelected

            if objWeasel.objXMLReader.isASeriesChecked:
                if len(objWeasel.objXMLReader.checkedSeriesList)>0: 
                    for series in objWeasel.objXMLReader.checkedSeriesList:
                        subjectID = series[0]
                        studyID = series[1]
                        seriesID = series[2]
                        imageList = objWeasel.objXMLReader.getImagePathList(subjectID, studyID, seriesID)
                        imageViewerROI(objWeasel, subjectID, studyID, seriesID, imageList)
            elif objWeasel.objXMLReader.isAnImageChecked:
                if len(objWeasel.objXMLReader.checkedImageList)>0: 
                    for image in objWeasel.objXMLReader.checkedImageList:
                        subjectID = image[0]
                        studyID = image[1]
                        seriesID = image[2]
                        imagePath = image[3]
                        imageViewerROI(objWeasel, subjectID, studyID, 
                                    seriesID, imagePath, singleImageSelected=True)
                        
        except NoTreeViewItemSelected:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("View DICOM series or image with ROI")
            msgBox.setText("Select either a series or an image")
            msgBox.exec()
        except Exception as e:
            print('Error in ViewImageMultiSlider.main: ' + str(e))
            logger.error('Error in ViewImageMultiSlider.main: ' + str(e))
