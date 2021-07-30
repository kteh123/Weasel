import CoreModules.WEASEL.DisplayImageMultiSliders  as displayImageColour
import CoreModules.WEASEL.TreeView  as treeView

from CoreModules.WEASEL.ImageViewer import ImageViewer as imageViewer
import logging
from PyQt5.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)

class NoTreeViewItemSelected(Exception):
   """Raised when the name of the function corresponding 
   to a module is not returned from the XML configuration file."""
   pass

def main(objWeasel):
        """Creates a subwindow that displays a DICOM image. Either executed using the 
        'View Image' Menu item in the Tools menu or by double clicking the Image name 
        in the DICOM studies tree view."""
        try:
            logger.info("viewImage.main called")
            if treeView.isAnItemChecked(objWeasel) == False:
                raise NoTreeViewItemSelected
            
            treeView.buildListsCheckedItems(objWeasel)

            if len(objWeasel.checkedSeriesList)>0: 
                for series in objWeasel.checkedSeriesList:
                    subjectID = series[0]
                    studyName = series[1]
                    seriesName = series[2]
                    imageList = treeView.returnSeriesImageList(objWeasel, subjectID, studyName, seriesName)
                    imageViewer(objWeasel, subjectID, studyName, seriesName, imageList)
            
            #if objWeasel.isASeriesChecked:
            #    displayImageColour.displayManyMultiImageSubWindows(objWeasel)
            #elif objWeasel.isAnImageChecked:
            #    displayImageColour.displayManySingleImageSubWindows(objWeasel)

        except NoTreeViewItemSelected:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("View DICOM series or image with ROI")
            msgBox.setText("Select either a series or an image")
            msgBox.exec()
        except Exception as e:
            print('Error in ViewImage.main: ' + str(e))
            logger.error('Error in ViewImage.main: ' + str(e))
