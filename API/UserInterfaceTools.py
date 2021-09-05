import os
import logging
from PyQt5.QtWidgets import (QMessageBox, QFileDialog)
import CoreModules.WEASEL.DisplayImageColour as displayImageColour
import CoreModules.WEASEL.MessageWindow as messageWindow
from Displays.ViewMetaData import displayMetaDataSubWindow
from DICOM.Classes import (Subject, Study, Series, Image)

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

    # May be redundant
    def getCurrentSubject(self):
        """
        Returns the Subject ID of the latest item selected in the Treeview.
        """
        return self.selectedSubject

    # May be redundant
    def getCurrentStudy(self):
        """
        Returns the Study ID of the latest item selected in the Treeview.
        """
        return self.selectedStudy

    # May be redundant
    def getCurrentSeries(self):
        """
        Returns the Series ID of the latest item selected in the Treeview.
        """
        return self.selectedSeries
    
    # May be redundant
    def getCurrentImage(self):
        """
        Returns a string with the path of the latest selected image.
        """
        return self.selectedImagePath
    
    # Need to do one for subjects and to include treeView.buildListsCheckedItems(self)

    def getCheckedSubjects(self):
        """
        Returns a list with objects of class Subject of the items checked in the Treeview.
        """
        subjectList = []
        subjectsTreeViewList = self.treeView.returnCheckedSubjects()
        if subjectsTreeViewList == []:
            self.showMessageWindow(msg="Script didn't run successfully because"
                              " no subjects were checked in the Treeview.",
                              title="No Subjects Checked")
            return 
        else:
            for subject in subjectsTreeViewList:
                subjectList.append(Subject.fromTreeView(self, subject))
        return subjectList

    def getCheckedStudies(self):
        """
        Returns a list with objects of class Study of the items checked in the Treeview.
        """
        studyList = []
        studiesTreeViewList = self.treeView.returnCheckedStudies()
        if studiesTreeViewList == []:
            self.showMessageWindow(msg="Script didn't run successfully because"
                              " no studies were checked in the Treeview.",
                              title="No Studies Checked")
            return 
        else:
            for study in studiesTreeViewList:
                studyList.append(Study.fromTreeView(self, study))
        return studyList
    

    def getCheckedSeries(self):
        """
        Returns a list with objects of class Series of the items checked in the Treeview.
        """
        seriesList = []
        seriesTreeViewList = self.treeView.returnCheckedSeries()
        if seriesTreeViewList == []:
            self.showMessageWindow(msg="Script didn't run successfully because"
                              " no series were checked in the Treeview.",
                              title="No Series Checked")
            return 
        else:
            for series in seriesTreeViewList:
                seriesList.append(Series.fromTreeView(self, series))
        return seriesList
    

    def getCheckedImages(self):
        """
        Returns a list with objects of class Image of the items checked in the Treeview.
        """
        imagesList = []
        imagesTreeViewList = self.treeView.returnCheckedImages()
        if imagesTreeViewList == []:
            self.showMessageWindow(msg="Script didn't run successfully because"
                              " no images were checked in the Treeview.",
                              title="No Images Checked")
            return
        else:
            for images in imagesTreeViewList:
                imagesList.append(Image.fromTreeView(self, images))
        return imagesList

    
    def showMessageWindow(self, msg="Please insert message in the function call", title="Message Window Title"):
        """
        Displays a window in the User Interface with the title in "title" and
        with the message in "msg". The 2 strings in the arguments are the input by default.
        """
        messageWindow.displayMessageSubWindow(self, "<H4>" + msg + "</H4>", title)


    def showInformationWindow(self, title="Message Window Title", msg="Please insert message in the function call"):
        """
        Displays an information window in the User Interface with the title in "title" and
        with the message in "msg". The 2 strings in the arguments are the input by default.
        The user has to click "OK" in order to continue using the interface.
        """
        QMessageBox.information(self, title, msg)


    def showErrorWindow(self, title="Message Window Title", msg="Please insert message in the function call"):
        """
        Displays an error window in the User Interface with the title in "title" and
        with the message in "msg". The 2 strings in the arguments are the input by default.
        The user has to click "OK" in order to continue using the interface.
        """
        QMessageBox.critical(self, title, msg)


    def showQuestionWindow(self, title="Message Window Title", question="You wish to proceed (OK) or not (Cancel)?"):
        """
        Displays a question window in the User Interface with the title in "title" and
        with the question in "question". The 2 strings in the arguments are the input by default.
        The user has to click either "OK" or "Cancel" in order to continue using the interface.

        It returns 0 if reply is "Cancel" and 1 if reply is "OK".
        """
        buttonReply = QMessageBox.question(self, title, question, 
                      QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if buttonReply == QMessageBox.Ok:
            return 1
        else:
            return 0


    def closeMessageWindow(self):
        """
        Closes any message window present in the User Interface.
        """
        messageWindow.hideProgressBar(self)
        messageWindow.closeMessageSubWindow(self)


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


    def displayImages(self, inputPath, subjectID, studyID, seriesID):
        """
        Display the PixelArray in "inputPath" in the User Interface.
        """
        logger.info("UserInterfaceTools.displayImages called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                displayImageColour.displayImageSubWindow(self, inputPath, subjectID, seriesID, studyID)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                if len(inputPath) == 1:
                    displayImageColour.displayImageSubWindow(self, inputPath[0], subjectID, seriesID, studyID)
                else:
                    displayImageColour.displayMultiImageSubWindow(self, inputPath, subjectID, studyID, seriesID)
            return
        except Exception as e:
            print('Error in function UserInterfaceTools.displayImages: ' + str(e))
            logger.exception('Error in UserInterfaceTools.displayImages: ' + str(e))
        