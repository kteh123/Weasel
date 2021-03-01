import CoreModules.WEASEL.DisplayImageDrawROI as displayImageROI
import CoreModules.WEASEL.TreeView  as treeView
from PyQt5.QtWidgets import QMessageBox
import logging
logger = logging.getLogger(__name__)


class NoTreeViewItemSelected(Exception):
   """Raised when the name of the function corresponding 
   to a model is not returned from the XML configuration file."""
   pass


def main(self):
    """Creates a subwindow that displays a DICOM image with ROI creation functionality. 
    Executed using the 'View Image with ROI' Menu item in the Tools menu."""
    try:
        logger.info("Menus.viewROIImage called")
        #print('treeView.isAnItemChecked(self)={}'.format(treeView.isAnItemChecked(self)))
        #print('treeView.isAnImageSelected(self)={}'.format(treeView.isAnImageSelected(self)))
        #print('self.isASeriesChecked={}'.format(self.isASeriesChecked))
        
        if treeView.isAnItemChecked(self) == False:
            raise NoTreeViewItemSelected

        if self.isASeriesChecked:
            displayImageROI.displayManyMultiImageSubWindows(self)
        elif self.isAnImageChecked:
            displayImageROI.displayManySingleImageSubWindows(self)

    except NoTreeViewItemSelected:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("View DICOM series or image with ROI")
            msgBox.setText("Select either a series or an image")
            msgBox.exec()
    except Exception as e:
        print('Error in Menus.viewROIImage: ' + str(e))
        logger.error('Error in Menus.viewROIImage: ' + str(e))
