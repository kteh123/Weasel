import CoreModules.WEASEL.DisplayImageDrawROI as displayImageROI
import CoreModules.WEASEL.TreeView  as treeView
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
        #print('treeView.isAnItemSelected(self)={}'.format(treeView.isAnItemSelected(self)))
        #print('treeView.isAnImageSelected(self)={}'.format(treeView.isAnImageSelected(self)))
        #print('treeView.isASeriesSelected(self)={}'.format(treeView.isASeriesSelected(self)))
        
        if treeView.isAnItemSelected(self) == False:
            raise NoTreeViewItemSelected

        if treeView.isAnImageSelected(self):
            displayImageROI.displayImageROISubWindow(self)
        elif treeView.isASeriesSelected(self):
            studyName = self.selectedStudy 
            seriesName = self.selectedSeries
            self.imageList = self.objXMLReader.getImagePathList(studyName, seriesName)
            displayImageROI.displayMultiImageROISubWindow(self, self.imageList, studyName, seriesName)

    except NoTreeViewItemSelected:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("View DICOM series or image with ROI")
            msgBox.setText("Select either a series or an image")
            msgBox.exec()
    except Exception as e:
        print('Error in Menus.viewROIImage: ' + str(e))
        logger.error('Error in Menus.viewROIImage: ' + str(e))
