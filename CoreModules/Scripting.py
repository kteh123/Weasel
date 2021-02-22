import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.MessageWindow as messageWindow
from CoreModules.DeveloperTools import UserInterfaceTools
from CoreModules.DeveloperTools import Image as ImageJoao
from CoreModules.DeveloperTools import Series as SeriesJoao
import os
import CoreModules.WEASEL.DisplayImageCommon as displayImageCommon

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


class Image(ImageJoao):
    """
    A class containing a single image. 
    """
    def Copy(self):
        """
        Creates a copy of the Series. 
        """       
        Copy = self.new(suffix="_Copy")    
        Copy.write(self.PixelArray) 
        return Copy  

    def Delete(self):
        """
        Deletes the image
        """
        displayImageCommon.closeSubWindow(self.objWeasel, self.path)
        if os.path.exists(self.path): os.remove(self.path)
        NrOfImagesInSeries = len(self.objWeasel.objXMLReader.getImageList(self.studyID, self.seriesID))
        if NrOfImagesInSeries == 1:
            self.objWeasel.objXMLReader.removeSeriesFromXMLFile(self.studyID, self.seriesID)
        else:
            self.objWeasel.objXMLReader.removeOneImageFromSeries(self.studyID, self.seriesID, self.path)


class Series(SeriesJoao):
    """
    A class containing a single Series. 
    """
    def Copy(self):
        """
        Creates a copy of the Series. 
        """       
        Copy = self.new(suffix="_Copy")    
        Copy.write(self.PixelArray) 
        return Copy   

    def Delete(self):
        """
        Deletes the series
        """  
        for Image in self.children(): 
            Image.Delete()


class Pipelines:
    """
    A class for accessing GUI elements from within a pipeline script. 
    """
    def Images(self):
        """
        Returns a list of Images checked by the user.
        """
        imagesList = [] 
        for image in treeView.returnCheckedImages(self):
            imagesList.append(Image.fromTreeView(self, image))
        return ImagesList(imagesList)

    def Series(self):
        """
        Returns a list of Series checked by the user.
        """
        seriesList = []
        for series in treeView.returnCheckedSeries(self):
            seriesList.append(Series.fromTreeView(self, series))
        return SeriesList(seriesList)
 
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

    def Refresh(self, new_series_name='Series'):
        """
        Refreshes the Weasel display.
        """
        self.CloseProgressBar()
        ui = UserInterfaceTools(self)
        ui.refreshWeasel(new_series_name=new_series_name)

