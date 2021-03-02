import os
import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.MessageWindow as messageWindow
from CoreModules.DeveloperTools import UserInterfaceTools
from CoreModules.DeveloperTools import Study
from CoreModules.DeveloperTools import Series
from CoreModules.DeveloperTools import Image


class List:
    """
    A superclass for managing Lists. 
    """
    def __init__(self, List):
        self.List = List

    @property
    def empty(self):
        """
        Checks if the list is empty.
        """
        return len(self.List) == 0

    @property
    def length(self):
        """
        Returns the number of items in the list.
        """
        return len(self.List)

    @property
    def enumerate(self):
        """
        Enumerates the items in the list.
        """
        return enumerate(self.List)

    def delete(self):
        """
        Deletes all items in the list
        """
        for item in self.List:
            item.delete()


class ImagesList(List):
    """
    A class containing a list of objects of class Image. 
    """
    def display(self):
        """
        Displays all images in the list.
        """
        if len(self.List) == 0: return
        self.List[0].displayImages(self.List)

    def merge(self, series_name='MergedSeries'):
        """
        Merges a list of images into a new series under the same study
        """
        if len(self.List) == 0: return
        return self.List[0].merge(self.List, series_name=series_name)

    def new_parent(self, suffix="_Suffix"):
        """
        Creates a new parent series from the images in the list.
        """
        return self.List[0].newSeriesFrom(self.List, suffix=suffix)


class SeriesList(List):
    """
    A class containing a list of class Series. 
    """
    def display(self):
        """
        Displays all series in the list.
        """
        if len(self.List) == 0: return
        for Series in self.List: Series.display()
    
    def merge(self, series_name='MergedSeries'):
        """
        Merges a list of series into a new series under the same study
        """
        if len(self.List) == 0: return
        return self.List[0].merge(self.List, series_name=series_name)


class StudyList(List):
    """
    A class containing a list of class Study. 
    """
    def display(self):
        """
        Displays all studies in the list (NOT YET AVAILABLE).
        """


class Pipelines:
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
        # When Tutorials is finished, the above can be replaced by the following 2 lines 
        #imagesList = UserInterfaceTools(self).getCheckedImages()
        #if imagesList is None: imagesList = []
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
        # When Tutorials is finished, the above can be replaced by the following 2 lines 
        #seriesList = UserInterfaceTools(self).getCheckedSeries()
        #if seriesList is None: seriesList = []
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
        # When Tutorials is finished, the above can be replaced by the following 2 lines 
        #studyList = UserInterfaceTools(self).getCheckedStudies()
        #if studyList is None: studyList = []
        return StudyList(studyList)
 
    def progress_bar(self, max=1, index=0, msg="Iteration Number {}", title="Progress Bar"):
        """
        Displays a Progress Bar with the unit set in "index".
        """
        messageWindow.displayMessageSubWindow(self, ("<H4>" + msg + "</H4>").format(index), title)
        messageWindow.setMsgWindowProgBarMaxValue(self, max)
        messageWindow.setMsgWindowProgBarValue(self, index)

    def close_progress_bar(self):
        """
        Closes the Progress Bar.
        """
        messageWindow.hideProgressBar(self)
        messageWindow.closeMessageSubWindow(self)

    def refresh(self, new_series_name=None):
        """
        Refreshes the Weasel display.
        """
        self.close_progress_bar()
        ui = UserInterfaceTools(self)
        ui.refreshWeasel(new_series_name=new_series_name)

    def user_input(self, title="User input window", *fields):
        """
        Creates a pop-up window to get user input.
        """
        inputDict = {}
        lists = []
        for field in fields:
            if field["type"] == "float": 
                inputDict[field["label"]] = "float"
            if field["type"] == "int":
                inputDict[field["label"]] = "int"
            if field["type"] == "string":
                inputDict[field["label"]] = "string"
        ui = UserInterfaceTools(self)
        paramList = ui.inputWindow(inputDict, title=title, lists=lists)
        if paramList is None: 
            return (1,) + tuple(paramList)
        return (0,) + tuple(paramList)