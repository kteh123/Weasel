import os
import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.MessageWindow as messageWindow
from CoreModules.DeveloperTools import UserInterfaceTools
from CoreModules.DeveloperTools import Study as StudyJoao
from CoreModules.DeveloperTools import Series as SeriesJoao
from CoreModules.DeveloperTools import Image as ImageJoao


class List:
    """
    A superclass for managing Lists. 
    """
    def __init__(self, List):
        self.List = List

    def Empty(self):
        """
        Checks if the list is empty.
        """
        return len(self.List) == 0

    def Count(self):
        """
        Returns the number of items in the list.
        """
        return len(self.List)

    def Enumerate(self):
        """
        Enumerates the items in the list.
        """
        return enumerate(self.List)

    def Delete(self):
        """
        Deletes all items in the list
        """
        for item in self.List:
            item.Delete()


class ImagesList(List):
    """
    A class containing a list of objects of class Image. 
    """
    def Display(self):
        """
        Displays all images in the list.
        """
        if len(self.List) == 0: return
        self.List[0].DisplayImages(self.List)

    def Merge(self, series_name='MergedSeries'):
        """
        Merges a list of images into a new series under the same study
        """
        if len(self.List) == 0: return
        return self.List[0].merge(self.List, series_name=series_name)

    def NewParent(self, suffix="_Suffix"):
        """
        Creates a new parent series from the images in the list.
        """
        return self.List[0].newSeriesFrom(self.List, suffix=suffix)


class SeriesList(List):
    """
    A class containing a list of class Series. 
    """
    def Display(self):
        """
        Displays all series in the list.
        """
        if len(self.List) == 0: return
        for Series in self.List: Series.Display()
    
    def Merge(self, series_name='MergedSeries'):
        """
        Merges a list of series into a new series under the same study
        """
        if len(self.List) == 0: return
        return self.List[0].merge(self.List, series_name=series_name)


class StudyList(List):
    """
    A class containing a list of class Study. 
    """
    def Display(self):
        """
        Displays all studies in the list (NOT YET AVAILABLE).
        """


class Image(ImageJoao):
    """
    A class containing a single image. 
    """
    def Copy(self, series=None):
        """
        Creates a copy of the Series. 
        """       
        #Copy = self.new(suffix="_Copy")    
        #Copy.write(self.PixelArray) 
        Copy = self.copy(series=series)
        return Copy  

    def Delete(self):
        """
        Deletes the image
        """
        self.delete()


class Series(SeriesJoao):
    """
    A class containing a single Series. 
    """
    def Copy(self):
        """
        Creates a copy of the Series. 
        """       
        #Copy = self.new(suffix="_Copy")    
        #Copy.write(self.PixelArray)
        Copy = self.copy()
        return Copy   

    def Delete(self):
        """
        Deletes the Series
        """  
        self.delete()


class Study(StudyJoao):
    """
    A class containing a single Study. 
    """
    def Copy(self):
        """
        Creates a copy of the Study (Needs a new() method for studies). 
        """          

    def Delete(self):
        """
        Deletes the Study
        """  
        for Child in self.children(): 
            Child.Delete()


class Pipelines:
    """
    A class for accessing GUI elements from within a pipeline script. 
    """
    def Images(self):
        """
        Returns a list of Images checked by the user.
        """
        imagesList = [] 
        imagesTreeViewList = treeView.returnCheckedImages(self)
        if imagesTreeViewList == []:
            UserInterfaceTools(self).showMessageWindow(msg="Script didn't run successfully because"
                              " no images were checked in the Treeview.",
                              title="No Images Checked")
            return
        else:
            for images in imagesTreeViewList:
                imagesList.append(Image.fromTreeView(self, images))
        # When Tutorials is finished, the above can be replaced by the following 2 lines 
        #imagesList = UserInterfaceTools(self).getCheckedImages()
        #if imagesList is None: imagesList = []
        return ImagesList(imagesList)

    def Series(self):
        """
        Returns a list of Series checked by the user.
        """
        seriesList = []
        seriesTreeViewList = treeView.returnCheckedSeries(self)
        if seriesTreeViewList == []:
            UserInterfaceTools(self).showMessageWindow(msg="Script didn't run successfully because"
                              " no series were checked in the Treeview.",
                              title="No Series Checked")
        else:
            for series in seriesTreeViewList:
                seriesList.append(Series.fromTreeView(self, series))
        # When Tutorials is finished, the above can be replaced by the following 2 lines 
        #seriesList = UserInterfaceTools(self).getCheckedSeries()
        #if seriesList is None: seriesList = []
        return SeriesList(seriesList)

    def Studies(self):
        """
        Returns a list of Studies checked by the user.
        """
        studyList = []
        studiesTreeViewList = treeView.returnCheckedStudies(self)
        if studiesTreeViewList == []:
            UserInterfaceTools(self).showMessageWindow(msg="Script didn't run successfully because"
                              " no studies were checked in the Treeview.",
                              title="No Studies Checked")
        else:
            for study in studiesTreeViewList:
                studyList.append(Study.fromTreeView(self, study))
        # When Tutorials is finished, the above can be replaced by the following 2 lines 
        #studyList = UserInterfaceTools(self).getCheckedStudies()
        #if studyList is None: studyList = []
        return StudyList(studyList)
 
    def ProgressBar(self, max=1, index=0, msg="Iteration Number {}", title="Progress Bar"):
        """
        Displays a Progress Bar with the unit set in "index".
        """
        messageWindow.displayMessageSubWindow(self, ("<H4>" + msg + "</H4>").format(index), title)
        messageWindow.setMsgWindowProgBarMaxValue(self, max)
        messageWindow.setMsgWindowProgBarValue(self, index)

    def CloseProgressBar(self):
        """
        Closes the Progress Bar.
        """
        messageWindow.hideProgressBar(self)
        messageWindow.closeMessageSubWindow(self)

    def Refresh(self, new_series_name=None):
        """
        Refreshes the Weasel display.
        """
        self.CloseProgressBar()
        ui = UserInterfaceTools(self)
        ui.refreshWeasel(new_series_name=new_series_name)
