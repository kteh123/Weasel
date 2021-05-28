import os
import re
#import itertools
import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.MessageWindow as messageWindow
import CoreModules.WEASEL.MeanROITimeCurveViewer as curveViewer

from PyQt5.QtWidgets import (QMessageBox, QFileDialog)
from ast import literal_eval # Convert strings to their actual content. Eg. "[a, b]" becomes the actual list [a, b]
from CoreModules.WEASEL.DeveloperTools import UserInterfaceTools
from CoreModules.WEASEL.DeveloperTools import Subject
from CoreModules.WEASEL.DeveloperTools import Study
from CoreModules.WEASEL.DeveloperTools import Series
from CoreModules.WEASEL.DeveloperTools import Image
import logging
logger = logging.getLogger(__name__)

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
    @property
    def label(self):
        """
        Returns a list of names of the list of images.
        """
        listNames = [image.label for image in self]
        return listNames

    def copy(self):
        """
        Returns a copy of the list of images.
        """
        copy = []
        for image in self:
            copy.append(image.copy())
        return ImagesList(copy)
        
    def merge(self, series_number=None,series_name='MergedSeries', study_name=None, patient_name=None, overwrite=True, progress_bar=True):
        """
        Merges a list of images into a new series under the same study
        """
        if len(self) == 0: return
        return self[0].merge(self, series_id=series_number, series_name=series_name, study_name=study_name, patient_id=patient_name, overwrite=overwrite, progress_bar=progress_bar)

    def new_parent(self, suffix="_Suffix"):
        """
        Creates a new parent series from the images in the list.
        """
        return self[0].newSeriesFrom(self, suffix=suffix)

    @property
    def parent(self):
        """
        Returns a list of unique series to which the images belong to.
        """
        parentsList = []
        listParentsAttribute = []
        for image in self:
            series = image.parent
            listIndividualAttributes = [series.subjectID, series.studyID, series.seriesID,
                                        series.images, series.studyUID, series.seriesUID, series.suffix]
            listParentsAttribute.append(listIndividualAttributes)
        listUniqueParentsAttribute = OriginalPipelines.unique_elements(listParentsAttribute)
        for listAtt in listUniqueParentsAttribute:
            series = Series(self[0].objWeasel, listAtt[0], listAtt[1], listAtt[2], listAtt[3], listAtt[4], listAtt[5], listAtt[6])
            parentsList.append(series)
        return SeriesList(parentsList)

    def display(self):
        """
        Displays all images as a series.
        """
        self[0].displayListImages(self)

    def sort(self, *argv, reverse=False):
        """
        Sort the list of images by the given DICOM tags.
        """
        tuple_to_sort = []
        list_to_sort = []
        list_to_sort.append(self)
        for tag in argv:
            if len(self.get_value(tag)) > 0:
                attributeList = self.get_value(tag)
                list_to_sort.append(attributeList)
        for index, _ in enumerate(self):
            individual_tuple = []
            for individual_list in list_to_sort:
                individual_tuple.append(individual_list[index])
            tuple_to_sort.append(tuple(individual_tuple))
        tuple_sorted = sorted(tuple_to_sort, key=lambda x: x[1:], reverse=reverse)
        list_sorted_images = []
        for individual in tuple_sorted:
            list_sorted_images.append(individual[0])
        self = ImagesList(list_sorted_images)
        return self

    def where(self, tag, condition, target):
        list_images = []
        for image in self:
            value = image[tag]
            statement = repr(value) + ' ' + repr(condition) + ' ' + repr(target)
            if eval(literal_eval(statement)) == True:
                list_images.append(image)
        self = ImagesList(list_images)
        return self

    def get_value(self, tag):
        """
        Returns a list of values of the given DICOM tag in the list of images
        """
        attributes_list = []
        for image in self:
            attributes_list.append(image.get_value(tag))
        return attributes_list

    def set_value(self, tag, value):
        """
        Set the variable "value" to the given DICOM tag in the list of images
        """
        for image in self:
            image.set_value(tag, value)


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

    def merge(self, series_name='MergedSeries', study_name=None, patient_name=None, overwrite=True, progress_bar=True):
        """
        Merges a list of series into a new series under the same study
        """
        if len(self) == 0: return
        return self[0].merge(self, series_name=series_name, study_name=study_name, patient_id=patient_name, overwrite=overwrite, progress_bar=progress_bar)
    
    @property
    def parent(self):
        """
        Returns a list of unique studies to which the series belong to.
        """
        parentsList = []
        listParentsAttribute = []
        for series in self:
            study = series.parent
            listIndividualAttributes = [study.subjectID, study.studyID, study.studyUID, study.suffix]
            listParentsAttribute.append(listIndividualAttributes)
        listUniqueParentsAttribute = OriginalPipelines.unique_elements(listParentsAttribute)
        for listAtt in listUniqueParentsAttribute:
            study = Study(self[0].objWeasel, listAtt[0], listAtt[1], listAtt[2], listAtt[3])
            parentsList.append(study)
        return StudyList(parentsList)

    @property
    def children(self):
        """
        Returns a list of lists of images where each list refers to the various images of a series.
        """
        childrenList = []
        for series in self:
            # We're returning list of lists by using append.
            # If we want a flat list, we'll have to use extend instead.
            childrenList.append(series.children)
        return childrenList


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

    def merge(self, study_name='MergedStudies', overwrite=True, progress_bar=True):
        """
        Merges a list of series into a new series under the same study
        """
        if len(self) == 0: return
        return self[0].merge(self, newStudyName=study_name, overwrite=overwrite, progress_bar=progress_bar)

    @property
    def parent(self):
        """
        Returns a list of unique subjects to which the studies belong to.
        """
        parentsList = []
        listParentsAttribute = []
        for study in self:
            subject = study.parent
            listIndividualAttributes = [subject.subjectID, subject.suffix]
            listParentsAttribute.append(listIndividualAttributes)
        listUniqueParentsAttribute = OriginalPipelines.unique_elements(listParentsAttribute)
        for listAtt in listUniqueParentsAttribute:
            subject = Subject(self[0].objWeasel, listAtt[0], listAtt[1])
            parentsList.append(subject)
        return SubjectList(parentsList)

    @property
    def children(self):
        """
        Returns a list of lists of series where each list refers to the various series of a study.
        """
        childrenList = []
        for study in self:
            # We're returning list of lists by using append.
            # If we want a flat list, we'll have to use extend instead.
            childrenList.append(study.children)
        return childrenList


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

    def merge(self, subject_name='MergedSubjects', overwrite=True, progress_bar=True):
        """
        Merges a list of series into a new series under the same study
        """
        if len(self) == 0: return
        return self[0].merge(self, newSubjectName=subject_name, overwrite=overwrite, progress_bar=progress_bar)

    @property
    def children(self):
        """
        Returns a list of lists of series where each list refers to the various series of a study.
        """
        childrenList = []
        for subject in self:
            # We're returning list of lists by using append.
            # If we want a flat list, we'll have to use extend instead.
            childrenList.append(subject.subject)
        return childrenList


class OriginalPipelines():
    """
    A class for accessing GUI elements from within a pipeline script. 
    """
    def log(self, message):
        logger.exception(message)

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
                subjectList.append(Subject(self, subject))
            
        return SubjectList(subjectList)

    def message(self, msg="Message in the box", title="Window Title"):
        """
        Displays a Message window with the text in "msg" and the title "title".
        """
        messageWindow.displayMessageSubWindow(self, "<H4>" + msg + "</H4>", title)

    def close_message(self):
        """
        Closes the message window 
        """
        self.msgSubWindow.close()

    def information(self, msg="Message in the box", title="Window Title"):
        """
        Display a Window with information message and the user must press 'OK' to continue.
        """
        QMessageBox.information(self, title, msg)

    def warning(self, msg="Message in the box", title="Window Title"):
        """
        Display a Window with warning message and the user must press 'OK' to continue.
        """
        QMessageBox.warning(self, title, msg)

    def error(self, msg="Message in the box", title="Window Title"):
        """
        Display a Window with error message and the user must press 'OK' to continue.
        """
        QMessageBox.critical(self, title, msg)

    def question(self, question="You wish to proceed (OK) or not (Cancel)?", title="Message Window Title"):
        """
        Displays a question window in the User Interface with the title in "title" and
        with the question in "question". The 2 strings in the arguments are the input by default.
        The user has to click either "OK" or "Cancel" in order to continue using the interface.
        It returns 0 if reply is "Cancel" and 1 if reply is "OK".
        """
        buttonReply = QMessageBox.question(self, title, question, 
                      QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if buttonReply == QMessageBox.Ok:
            return True
        else:
            return False
 
    def progress_bar(self, max=1, index=0, msg="Progressing...", title="Progress Bar"):
        """
        Displays a progress bar with the unit set in "index".
        Note: launching a new progress bar at each iteration costs time, so this
        should only be used in iterations where the progress bar is updated infrequently
        For iterations with frequent updates, use progress_bar outside the iteration
        and then update_progress_bar inside the iteration
        """
        messageWindow.displayMessageSubWindow(self, ("<H4>" + msg + "</H4>").format(index), title)
        messageWindow.setMsgWindowProgBarMaxValue(self, max)
        messageWindow.setMsgWindowProgBarValue(self, index)

    def update_progress_bar(self, index=0):
        """
        Updates the progress bar with a new index.
        """
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


    def plot(self, signalName, maskName, x, y, x_axis_label, y_axis_label, title="Time/Curve Plot"):
        curveViewer.displayTimeCurve(self, signalName, maskName, x, y, x_axis_label, y_axis_label, title=title)
        #subWindow = ROITimeCurveViewer(x, y, x_axis_label, y_axis_label, title=title)
        #self.mdiArea.addSubWindow(subWindow)
        #subWindow.displaySubWindow(pointerToWeasel)


    @staticmethod
    def unique_elements(inputList):
        """
        Returns unique elements of any list.
        """
        #output = list(inp for inp,_ in itertools.groupby(inputList))
        output = []
        for x in inputList:
            if x not in output:
                output.append(x)
        return output
    
    @staticmethod
    def match_search(regex_string, target):
        """
        Returns True if the regex "expression" is in the string target. 
        """
        return re.search(regex_string, target, re.IGNORECASE)