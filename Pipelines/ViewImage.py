import CoreModules.WEASEL.DisplayImageColour  as displayImageColour
import CoreModules.WEASEL.TreeView  as treeView
import logging
from PyQt5.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)

class NoTreeViewItemSelected(Exception):
   """Raised when the name of the function corresponding 
   to a model is not returned from the XML configuration file."""
   pass

def main(self):
        """Creates a subwindow that displays a DICOM image. Either executed using the 
        'View Image' Menu item in the Tools menu or by double clicking the Image name 
        in the DICOM studies tree view."""
        try:
            logger.info("viewImage.main called")
            if treeView.isAnItemChecked(self) == False:
                raise NoTreeViewItemSelected

            if self.isASeriesChecked:
                displayImageColour.displayManyMultiImageSubWindows(self)
            elif self.isAnImageChecked:
                displayImageColour.displayManySingleImageSubWindows(self)

        except NoTreeViewItemSelected:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("View DICOM series or image with ROI")
            msgBox.setText("Select either a series or an image")
            msgBox.exec()
        except Exception as e:
            print('Error in ViewImage.main: ' + str(e))
            logger.error('Error in ViewImage.main: ' + str(e))
