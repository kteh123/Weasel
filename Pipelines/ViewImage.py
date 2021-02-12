import CoreModules.WEASEL.DisplayImageColour  as displayImageColour
import CoreModules.WEASEL.TreeView  as treeView
import logging
logger = logging.getLogger(__name__)

def main(self):
        """Creates a subwindow that displays a DICOM image. Either executed using the 
        'View Image' Menu item in the Tools menu or by double clicking the Image name 
        in the DICOM studies tree view."""
        try:
            logger.info("viewImage.main called")
            studyName = self.selectedStudy 
            seriesName = self.selectedSeries
            if treeView.isASeriesSelected(self):
                self.imageList = self.objXMLReader.getImagePathList(studyName, seriesName)
                displayImageColour.displayMultiImageSubWindow(self, self.imageList, studyName, seriesName)
            elif treeView.isAnImageSelected(self):
                displayImageColour.displayImageSubWindow(self, studyName, seriesName)
        except Exception as e:
            print('Error in ViewImage.main: ' + str(e))
            logger.error('Error in ViewImage.main: ' + str(e))
