import os
import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.MessageWindow as messageWindow
from CoreModules.DeveloperTools import UserInterfaceTools
from CoreModules.DeveloperTools import Subject
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
    def copy(self):
        """
        Returns a copy of the list of studies.
        """
        copy = []
        for study in self: 
            copy.append(study.copy())
        return StudyList(copy)

    def merge(self, study_name='MergedStudies'):
        """
        Merges a list of series into a new series under the same study
        """
        if len(self) == 0: return
        return self[0].merge(self, newStudyName=study_name, overwrite=True)


class SubjectList(ListOfDicomObjects):
    """
    A class containing a list of class Subject. 
    """
    def copy(self):
        """
        Returns a copy of the list of subjects.
        """
        copy = []
        for subject in self: 
            copy.append(subject.copy())
        return SubjectList(copy)

    def merge(self, subject_name='MergedSubjects'):
        """
        Merges a list of series into a new series under the same study
        """
        if len(self) == 0: return
        return self[0].merge(self, newSubjectName=subject_name, overwrite=True)

class OriginalPipelines():
    """
    A class for accessing GUI elements from within a pipeline script. 
    """
    def images(self, msg='Please select one or more images'):
        """
        Returns a list of Images checked by the user.
        """
        imagesList = [] 
        #imagesTreeViewList = treeView.returnCheckedImages(self)
        #if imagesTreeViewList == []:
        #    UserInterfaceTools(self).showMessageWindow(msg=msg)
        #else:
        #    for images in imagesTreeViewList:
        #        imagesList.append(Image.fromTreeView(self, images))
        
        treeView.buildListsCheckedItems(self)
        if self.checkedImageList == []:
            UserInterfaceTools(self).showMessageWindow(msg=msg)
        else:
            for image in self.checkedImageList:
                imagesList.append(Image(self, image[0], image[1], image[2], image[3]))

        return ImagesList(imagesList)

    def series(self, msg='Please select one or more series'):
        """
        Returns a list of Series checked by the user.
        """
        seriesList = []
        #seriesTreeViewList = treeView.returnCheckedSeries(self)
        #if seriesTreeViewList == []:
        #    UserInterfaceTools(self).showMessageWindow(msg=msg)
        #else:
        #    for series in seriesTreeViewList:
        #        seriesList.append(Series.fromTreeView(self, series))
        
        treeView.buildListsCheckedItems(self)
        if self.checkedSeriesList == []:
            UserInterfaceTools(self).showMessageWindow(msg=msg)
        else:
            for series in self.checkedSeriesList:
                images = self.objXMLReader.getImagePathList(series[0], series[1], series[2])
                seriesList.append(Series(self, series[0], series[1], series[2], listPaths=images))

        return SeriesList(seriesList)

    def studies(self, msg='Please select one or more studies'):
        """
        Returns a list of Studies checked by the user.
        """
        studyList = []
        #studiesTreeViewList = treeView.returnCheckedStudies(self)
        #if studiesTreeViewList == []:
        #    UserInterfaceTools(self).showMessageWindow(msg=msg)
        #else:
        #    for study in studiesTreeViewList:
        #        studyList.append(Study.fromTreeView(self, study))

        treeView.buildListsCheckedItems(self)
        if self.checkedStudyList == []:
            UserInterfaceTools(self).showMessageWindow(msg=msg)
        else:
            for study in self.checkedStudyList:
                studyList.append(Study(self, study[0], study[1]))

        return StudyList(studyList)

    def subjects(self, msg='Please select one or more subjects'):
        """
        Returns a list of Subjects checked by the user.
        """
        subjectList = []
        #subjectsTreeViewList = treeView.returnCheckedSubjects(self)
        #if subjectsTreeViewList == []:
        #    UserInterfaceTools(self).showMessageWindow(msg=msg)
        #else:
        #    for subject in subjectsTreeViewList:
        #        subjectList.append(Subject.fromTreeView(self, subject))

        treeView.buildListsCheckedItems(self)
        if self.checkedSubjectList == []:
            UserInterfaceTools(self).showMessageWindow(msg=msg)
        else:
            for subject in self.checkedSubjectList:
                subjectList.append(Subject(self, subject[0]))
            
        return SubjectList(subjectList)
 
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

    def close_all_windows(self):
        """
        Closes all open windows.
        """
        self.mdiArea.closeAllSubWindows()