import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.MessageWindow as messageWindow
from CoreModules.DeveloperTools import Image


class Images:
    """
    A class containing a list of DICOM images in the study. 
    """

    def __init__(self, ImagesList):
        self.List = ImagesList

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

    def Display(self):
        """
        Displays all images in the list.
        """
        if len(self.List) == 0: return
        Image.DisplayImages(self.List)

       
class Pipelines:

    def Images(self):
        """
        Returns a list with objects of class Images of the items checked in the Treeview.
        """
        imagesList = [] 
        for image in treeView.returnCheckedImages(self):
            imagesList.append(Image.fromTreeView(self, image))
        return Images(imagesList)

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

