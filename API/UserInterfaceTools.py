import os
import logging
from PyQt5.QtWidgets import (QMessageBox, QFileDialog)
import CoreModules.WEASEL.MessageWindow as messageWindow
from Displays.ViewMetaData import displayMetaDataSubWindow

logger = logging.getLogger(__name__)

class UserInterfaceTools():
    """
    This class contains functions that read the items selected in the User Interface
    and return variables that are used in processing pipelines. It also contains functions
    that allow the user to insert inputs and give an update of the pipeline steps through
    message windows. 
    """
    
    def __repr__(self):
       return '{}'.format(self.__class__.__name__)


    def progressBar(self, maxNumber=1, index=0, msg="Iteration Number {}", title="Progress Bar"):
        """
        Updates the ProgressBar to the unit set in "index".
        """
        index += 1
        messageWindow.displayMessageSubWindow(self, ("<H4>" + msg + "</H4>").format(index), title)
        messageWindow.setMsgWindowProgBarMaxValue(self, maxNumber)
        messageWindow.setMsgWindowProgBarValue(self, index)
        return index
    

    def selectFolder(self, title="Select the directory"):
        """Displays an open folder dialog window to allow the
        user to select afolder """
        scan_directory = QFileDialog.getExistingDirectory(self, title, self.weaselDataFolder, QFileDialog.ShowDirsOnly)
        return scan_directory


    def displayMetadata(self, inputPath):
        """
        Display the metadata in "inputPath" in the User Interface.
        If "inputPath" is a list, then it displays the metadata of the first image.
        """
        logger.info("UserInterfaceTools.displayMetadata called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                dataset = PixelArrayDICOMTools.getDICOMobject(inputPath)
                displayMetaDataSubWindow(self, "Metadata for image {}".format(inputPath), dataset)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                dataset = PixelArrayDICOMTools.getDICOMobject(inputPath[0])
                displayMetaDataSubWindow(self, "Metadata for image {}".format(inputPath[0]), dataset)
        except Exception as e:
            print('Error in function UserInterfaceTools.displayMetadata: ' + str(e))
            logger.exception('Error in UserInterfaceTools.displayMetadata: ' + str(e))

        