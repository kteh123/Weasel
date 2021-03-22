import os
from PyQt5.QtWidgets import (QMessageBox, QFileDialog)
import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.MessageWindow as messageWindow
from CoreModules.DeveloperTools import UserInterfaceTools
from CoreModules.DeveloperTools import Study
from CoreModules.DeveloperTools import Series
from CoreModules.DeveloperTools import Image
from CoreModules.UserInput import UserInput

class ListOfDicomObjects(list):
    """
    A superclass for managing Lists of Subjects, Studies, Series or Images. 
    """
    def delete(self):
        """
        Deletes all items in the list
        """
        for item in self: 
            item.delete()

    def display(self):
        """
        Displays all items in the list.
        """
        for item in self: 
            item.display()


class ImagesList(ListOfDicomObjects):
    """
    A class containing a list of objects of class Image. 
    """

    def copy(self):
        """
        Returns a copy of the list of images.
        """
        copy = []
        for image in self: 
            copy.append(image.copy())
        return ImagesList(copy)
        
    def merge(self, series_name='MergedSeries'):
        """
        Merges a list of images into a new series under the same study
        """
        if len(self) == 0: return
        return self[0].merge(self, series_name=series_name, overwrite=True)

    def new_parent(self, suffix="_Suffix"):
        """
        Creates a new parent series from the images in the list.
        """
        return self[0].newSeriesFrom(self, suffix=suffix)

    def Item(self, *args):
        """
        Applies the Item method to all images in the list
        """
        return [image.Item(args) for image in self]

    def display(self):
        """
        Displays all images as a series.
        """
        self[0].displayListImages(self)


class SeriesList(ListOfDicomObjects):
    """
    A class containing a list of class Series. 
    """  
    def copy(self):
        """
        Returns a copy of the list of series.
        """
        copy = []
        for series in self: 
            copy.append(series.copy())
        return SeriesList(copy)

    def merge(self, series_name='MergedSeries'):
        """
        Merges a list of series into a new series under the same study
        """
        if len(self) == 0: return
        return self[0].merge(self, series_name=series_name, overwrite=True)


class StudyList(ListOfDicomObjects):
    """
    A class containing a list of class Study. 
    """


class Pipelines(UserInput):
    """
    A class for accessing GUI elements from within a pipeline script. 
    """
    def images(self, msg='Please select one or more images'):
        """
        Returns a list of Images checked by the user.
        """
        imagesList = [] 
        imagesTreeViewList = treeView.returnCheckedImages(self)
        if imagesTreeViewList == []:
            UserInterfaceTools(self).showMessageWindow(msg=msg)
        else:
            for images in imagesTreeViewList:
                imagesList.append(Image.fromTreeView(self, images))
        return ImagesList(imagesList)

    def series(self, msg='Please select one or more series'):
        """
        Returns a list of Series checked by the user.
        """
        seriesList = []
        seriesTreeViewList = treeView.returnCheckedSeries(self)
        if seriesTreeViewList == []:
            UserInterfaceTools(self).showMessageWindow(msg=msg)
        else:
            for series in seriesTreeViewList:
                seriesList.append(Series.fromTreeView(self, series))
        return SeriesList(seriesList)

    def studies(self, msg='Please select one or more studies'):
        """
        Returns a list of Studies checked by the user.
        """
        studyList = []
        studiesTreeViewList = treeView.returnCheckedStudies(self)
        if studiesTreeViewList == []:
            UserInterfaceTools(self).showMessageWindow(msg=msg)
        else:
            for study in studiesTreeViewList:
                studyList.append(Study.fromTreeView(self, study))
        return StudyList(studyList)
 
    def progress_bar(self, max=1, index=0, msg="Iteration Number {}", title="Progress Bar"):
        """
        Displays a progress bar with the unit set in "index".
        Note: launching a new progress bar at each iteration costs time, so this
        should only be used in iterations where the progress bar is updated infrequently
        For iterations with frequent updates, use progress_bar outside the iteration
        and then update_progress_bar inside the iteration
        """
        messageWindow.displayMessageSubWindow(self, ("<H4>" + msg + "</H4>").format(index), title)
        messageWindow.setMsgWindowProgBarMaxValue(self, max)
        messageWindow.setMsgWindowProgBarValue(self, index)

    def update_progress_bar(self, index=0):
        """
        Updates the progress bar with a new index.
        """
        messageWindow.setMsgWindowProgBarValue(self, index)

    def close_progress_bar(self):
        """
        Closes the Progress Bar.
        """
        messageWindow.hideProgressBar(self)
        messageWindow.closeMessageSubWindow(self)

    def message(self, msg="Hello world!", title="Message window"):
        """
        Displays a window in the User Interface with the title in "title" and
        with the message in "msg". 
        """
        messageWindow.displayMessageSubWindow(self, "<H4>" + msg + "</H4>", title)

    def close_message(self):
        """
        Closes the message window 
        """
        self.msgSubWindow.close()

    def information(self, msg="Are you OK today?", title="Message window"):
        """
        Displays an information window in the User Interface with the title in "title" and
        with the message in "msg". The user has to click "OK" in order to continue using the interface.
        """
        QMessageBox.information(self, title, msg)

    def question(self, msg="Shall we carry on?", title="Message Window Title"):
        """
        Displays a question window in the User Interface with the title in "title" and
        with the question in "msg". 
        The user has to click either "OK" or "Cancel" in order to continue using the interface.
        It returns 0 if reply is "Cancel" and 1 if reply is "OK".
        """
        buttonReply = QMessageBox.question(self, title, msg, 
                      QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if buttonReply == QMessageBox.Ok:
            return 1
        else:
            return 0

    def refresh(self, new_series_name=None):
        """
        Refreshes the Weasel display.
        """
        self.close_progress_bar()
        ui = UserInterfaceTools(self)
        ui.refreshWeasel(new_series_name=new_series_name)

    def close_all_windows(self):
        """
        Closes all open windows.
        """
        self.mdiArea.closeAllSubWindows()

    def folder(self, msg='Please select a folder'):
        """
        Ask the user to select a folder
        """
        return QFileDialog.getExistingDirectory(self,
            msg, 
            self.weaselDataFolder, 
            QFileDialog.ShowDirsOnly
        )

