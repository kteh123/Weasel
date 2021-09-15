import CoreModules.WEASEL.DisplayImageDrawROI as displayImageROI

from PyQt5.QtWidgets import QMessageBox
import logging
logger = logging.getLogger(__name__)


class NoTreeViewItemSelected(Exception):
   """Raised when the name of the function corresponding 
   to a model is not returned from the XML configuration file."""
   pass


def main(objWeasel):
    """Creates a subwindow that displays a DICOM image with ROI creation functionality. 
    Executed using the 'View Image with ROI' Menu item in the Tools menu."""
    try:
        logger.info("Menus.viewROIImage called")
        
        
        if objWeasel.treeView.isAnItemChecked() == False:
            raise NoTreeViewItemSelected

        if objWeasel.treeView.isASeriesChecked:
            displayImageROI.displayManyMultiImageSubWindows(objWeasel)
        elif objWeasel.treeView.isAnImageChecked:
            displayImageROI.displayManySingleImageSubWindows(objWeasel)

    except NoTreeViewItemSelected:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("View DICOM series or image with ROI")
            msgBox.setText("Select either a series or an image")
            msgBox.exec()
    except Exception as e:
        print('Error in Menus.viewROIImage: ' + str(e))
        logger.error('Error in Menus.viewROIImage: ' + str(e))
