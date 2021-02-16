import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.MessageWindow as messageWindow
from CoreModules.DeveloperTools import Image, Series


class ImagesList:
    """
    A class containing a list of DICOM images. 
    """
    def __init__(self, List):
        self.List = List

    def Empty(self):
        """
        Checks if the list of images is empty.
        """
        return len(self.List) == 0

    def Count(self):
        """
        Returns the number images in the list.
        """
        return len(self.List)

    def Enumerate(self):
        """
        Enumerates the images in the list.
        """
        return enumerate(self.List)

    def Display(self):
        """
        Displays all images in the list.
        """
        if len(self.List) == 0: return
        self.List[0].DisplayImages(self.List)


class SeriesList:
    """
    A class containing a list of DICOM series. 
    """
    def __init__(self, List):
        self.List = List

    def Empty(self):
        """
        Checks if the list of images is empty.
        """
        return len(self.List) == 0

    def Count(self):
        """
        Returns the number images in the list.
        """
        return len(self.List)

    def Enumerate(self):
        """
        Enumerates the images in the list.
        """
        return enumerate(self.List)

    def Display(self):
        """
        Displays all series in the list.
        """
        if len(self.List) == 0: return
        for Series in self.List: Series.DisplaySeries()


class Pipelines:

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

