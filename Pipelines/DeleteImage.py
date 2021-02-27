from PyQt5.QtWidgets import QMessageBox
import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.WEASEL.DisplayImageCommon as displayImageCommon
import os
import logging
logger = logging.getLogger(__name__)

class NoTreeViewItemSelected(Exception):
   """Raised when the name of the function corresponding 
   to a model is not returned from the XML configuration file."""
   pass


def main(self):
        """This method deletes an image or a series of images by 
        deleting the physical file(s) and then removing their entries
        in the XML file."""
        logger.info("DeleteImage.main called")
        try:
            if treeView.isAnItemChecked(self) == False:
                raise NoTreeViewItemSelected

            studyName = self.selectedStudy
            seriesName = self.selectedSeries
            if self.isAnImageChecked:
                imageName = self.selectedImageName
                imagePath = self.selectedImagePath
                buttonReply = QMessageBox.question(self, 
                  'Delete DICOM image', "You are about to delete image {}".format(imageName), 
                  QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                if buttonReply == QMessageBox.Ok:
                    #Delete physical file if it exists
                    if os.path.exists(imagePath):
                        os.remove(imagePath)
                    #If this image is displayed, close its subwindow
                    displayImageCommon.closeSubWindow(self, imagePath)
                    #Is this the last image in a series?
                    #Get the series containing this image and count the images it contains
                    #If it is the last image in a series then remove the
                    #whole series from XML file
                    #No it is not the last image in a series
                    #so just remove the image from the XML file 
                    images = self.objXMLReader.getImageList(studyName, seriesName)
                    if len(images) == 1:
                        #only one image, so remove the series from the xml file
                        #need to get study (parent) containing this series (child)
                        #then remove child from parent
                        self.objXMLReader.removeSeriesFromXMLFile(studyName, seriesName)
                    elif len(images) > 1:
                        #more than 1 image in the series, 
                        #so just remove the image from the xml file
                        self.objXMLReader.removeOneImageFromSeries(
                            studyName, seriesName, imagePath)
                    #Update tree view with xml file modified above
                    treeView.refreshDICOMStudiesTreeView(self)
            elif self.isASeriesChecked:
                buttonReply = QMessageBox.question(self, 
                  'Delete DICOM series', "You are about to delete series {}".format(seriesName), 
                  QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                if buttonReply == QMessageBox.Ok:
                    #Delete each physical file in the series
                    #Get a list of names of images in that series
                    imageList = self.objXMLReader.getImagePathList(studyName, 
                                                                   seriesName) 
                    #Iterate through list of images and delete each image
                    for imagePath in imageList:
                        if os.path.exists(imagePath):
                            os.remove(imagePath)
                    #Remove the series from the XML file
                    self.objXMLReader.removeSeriesFromXMLFile(studyName, seriesName)
                    displayImageCommon.closeSubWindow(self, seriesName)
                treeView.refreshDICOMStudiesTreeView(self)
        except NoTreeViewItemSelected:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Delete a DICOM series or image")
            msgBox.setText("Select either a series or an image")
            msgBox.exec()
        except Exception as e:
            print('Error in DeleteImage.main: ' + str(e))
            logger.error('Error in DeleteImage.main: ' + str(e))
