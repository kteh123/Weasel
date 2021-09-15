#from Displays.ImageViewers.ImageViewer import ImageViewer as imageViewer
import Displays.ImageViewers.ImageViewer  as imageViewer
import logging
from PyQt5.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)

__author__ = "Steve Shillitoe"
#September 2021

class NoTreeViewItemSelected(Exception):
   """Raised when the name of the function corresponding 
   to a module is not returned from the XML configuration file."""
   pass


def isEnabled(objWeasel):
    return True


def main(objWeasel):
        """Creates a subwindow that displays a DICOM image. Either executed using the 
        'View Image' Menu item in the Tools menu or by double clicking the Image name 
        in the DICOM studies tree view."""
        try:
            logger.info("viewImage.main called")
            if objWeasel.treeView.isAnItemChecked() == False:
                raise NoTreeViewItemSelected

            if objWeasel.treeView.isASeriesChecked:
                if len(objWeasel.treeView.checkedSeriesList)>0: 
                    for series in objWeasel.treeView.checkedSeriesList:
                        subjectID = series[0]
                        studyID = series[1]
                        seriesID = series[2]
                        imageList = objWeasel.objXMLReader.getImagePathList(subjectID, studyID, seriesID)
                        imageViewer(objWeasel, subjectID, studyID, seriesID, imageList)
            elif objWeasel.treeView.isAnImageChecked:
                if len(objWeasel.treeView.checkedImageList)>0: 
                    for image in objWeasel.treeView.checkedImageList:
                        subjectID = image[0]
                        studyID = image[1]
                        seriesID = image[2]
                        imagePath = image[3]
                        imageViewer(objWeasel, subjectID, studyID, 
                                    seriesID, imagePath, singleImageSelected=True)
                        
        except NoTreeViewItemSelected:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("View DICOM series or image with ROI")
            msgBox.setText("Select either a series or an image")
            msgBox.exec()
        except Exception as e:
            print('Error in ViewImageMultiSlider.main: ' + str(e))
            logger.error('Error in ViewImageMultiSlider.main: ' + str(e))
