import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.MessageWindow as messageWindow
from CoreModules.DeveloperTools import Image

class Scripting():

    def images(self):
        """
        Returns a list with objects of class Images of the items checked in the Treeview.
        """
        imagesList = []
        imagesTreeViewList = treeView.returnCheckedImages(self)
        for images in imagesTreeViewList:
            imagesList.append(Image.fromTreeView(self, images))
        return imagesList

    def progressBar(self, maxNumber=1, index=0, msg="Iteration Number {}", title="Progress Bar"):
        """
        Displays a Progress Bar with the unit set in "index".
        """
        messageWindow.displayMessageSubWindow(self, ("<H4>" + msg + "</H4>").format(index), title)
        messageWindow.setMsgWindowProgBarMaxValue(self, maxNumber)
        messageWindow.setMsgWindowProgBarValue(self, index)

    def closeProgressBar(self):
        """
        Closes the Progress Bar.
        """
        messageWindow.hideProgressBar(self)
        messageWindow.closeMessageSubWindow(self)

    def DisplayImages(self, imageList):
        """
        Displays all images in a list of images.
        """
        if len(imageList) == 0: return
        Image.DisplayImages(imageList)
