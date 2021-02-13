import CoreModules.WEASEL.TreeView as treeView
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
