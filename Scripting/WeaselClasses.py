import CoreModules.WEASEL.TreeView as treeView

class WeaselImages(list):
    """
    A class for handling a collection of DICOM images. 
    """
    def __init__(self, weasel, files):
        self.weasel = weasel
        super().__init__(files)

    def copy(self):
        """
        Creates a copy of all images in the same series. 
        """
        weasel = self.weasel
        weasel.progress_bar(max=len(self), msg='Copying images')
        for i, filepath in enumerate(self):  
            weasel.update_progress_bar(index=i+1)
            weasel.copy_dicom_file(filepath)
        weasel.close_progress_bar()

class WeaselClasses():
    """
    A collection of classes for handling DICOM data inside weasel scripts. 
    """
    def images(self, msg='Please select one or more images'):
        """
        Returns a list of Images checked by the user.
        """
        files = [] 
        for image in treeView.returnCheckedImages(self):
            filepath = image.text(4) 
            files.append(filepath)
        if files == []:
            self.information(msg = msg)
        return WeaselImages(self, files)