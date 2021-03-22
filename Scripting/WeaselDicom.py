import CoreModules.WEASEL.TreeView as treeView
from CoreModules.DeveloperTools import UserInterfaceTools
from CoreModules.DeveloperTools import Study
from CoreModules.DeveloperTools import Series
from CoreModules.DeveloperTools import Image


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


class WeaselDicom():
    """
    A collection of classes for handling DICOM data inside weasel scripts. 
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