from PyQt5.QtWidgets import QMessageBox, QApplication
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

            #print("self.checkedImageList={}".format(self.checkedImageList))
           # print("self.checkedSeriesList={}".format(self.checkedSeriesList))

            if self.isASeriesChecked:
                #get list of series to be deleted
                listOfSeries = ""
                counter = 0
                for series in self.checkedSeriesList:
                    counter += 1
                    if counter < len(self.checkedSeriesList):
                        listOfSeries = listOfSeries + series[2] + ", "
                    else:
                        listOfSeries = listOfSeries + series[2] 

                buttonReply = QMessageBox.question(self, 
                  'Delete DICOM series', "You are about to delete the followi series {}".format(listOfSeries), 
                  QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                if buttonReply == QMessageBox.Ok:
                    #Delete each physical file in the series
                    #Get a list of names of images in that series

                    if len(self.checkedSeriesList)>0: 
                        for series in self.checkedSeriesList:
                            subjectName = series[0]
                            studyName = series[1]
                            seriesName = series[2]
                            imageList = treeView.returnSeriesImageList(self, subjectName, studyName, seriesName)

                            #Iterate through list of images and delete each image
                            for imagePath in imageList:
                                if os.path.exists(imagePath):
                                    os.remove(imagePath)
                            #Remove the series from the XML file
                            self.objXMLReader.removeSeriesFromXMLFile(studyName, seriesName)
                            #Close subwindow displaying series if there is one
                            displayImageCommon.closeSubWindow(self, seriesName)
                treeView.refreshDICOMStudiesTreeView(self)
            elif self.isAnImageChecked:
                listOfImages = ""
                counter = 0
                for image in self.checkedImageList:
                    counter += 1
                    imageName = os.path.basename(image[2])
                    if counter < len(self.checkedImageList):
                        listOfImages = listOfImages + imageName + ", "
                    else:
                        listOfImages = listOfImages + imageName 
                buttonReply = QMessageBox.question(self, 
                  'Delete DICOM image', "You are about to delete images: {}".format(listOfImages), 
                  QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                if buttonReply == QMessageBox.Ok:
                    if len(self.checkedImageList)>0: 
                        for image in self.checkedImageList:
                            studyName = image[0]
                            seriesName = image[1]
                            imagePath = image[2]
                            subjectName = image[3]
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
                            imageList = treeView.returnSeriesImageList(self, subjectName, studyName, seriesName)
                            if len(imageList) == 1:
                                #only one image, so remove the series from the xml file
                                #need to get study (parent) containing this series (child)
                                #then remove child from parent
                                self.objXMLReader.removeSeriesFromXMLFile(studyName, seriesName)
                            elif len(imageList) > 1:
                                #more than 1 image in the series, 
                                #so just remove the image from the xml file
                                self.objXMLReader.removeOneImageFromSeries(
                                    subjectName, studyName, seriesName, imagePath)
                            #Update tree view with xml file modified above
                    treeView.refreshDICOMStudiesTreeView(self)
        except NoTreeViewItemSelected:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Delete a DICOM series or image")
            msgBox.setText("Select either a series or an image")
            msgBox.exec()
        except Exception as e:
            print('Error in DeleteImage.main: ' + str(e))
            logger.error('Error in DeleteImage.main: ' + str(e))
