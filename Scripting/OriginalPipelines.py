import os, sys
import re
import subprocess
import importlib
from tqdm import trange, tqdm
import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.MessageWindow as messageWindow
import CoreModules.WEASEL.MeanROITimeCurveViewer as curveViewer

from PyQt5.QtWidgets import (QMessageBox, QFileDialog, QMdiSubWindow)
from PyQt5.QtCore import  Qt
from PyQt5.QtGui import  QIcon
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

    @property
    def paths(self):
        """
        Returns a list of file paths of the list of images.
        """
        listPaths = [image.path for image in self]
        return listPaths

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
        if isinstance(value, list) and len(self) == len(value):
            for index, image in enumerate(self):
                image.set_value(tag, value[index])
        else:
            for image in self:
                image.set_value(tag, value)
    
    def __getitem__(self, tag):
        if isinstance(tag, int):
            return self[tag]
        else:
            return self.get_value(tag)

    def __setitem__(self, tag, value):
        if isinstance(tag, str) and len(tag.split(' ')) == 3:
            dicom_tag = tag.split(' ')[0]
            logical_operator = tag.split(' ')[1]
            target_value = tag.split(' ')[2]
            listImages = self.where(dicom_tag, logical_operator, target_value)
            listImages.set_value(dicom_tag, value)
        elif isinstance(tag, str):
            self.set_value(tag, value)
        elif isinstance(tag, int) and isinstance(value, Image):
            self[tag] = value
        elif isinstance(tag, list) and isinstance(value, list):
            for index, dicom_tag in enumerate(tag):
                self.set_value(dicom_tag, value[index])


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
        print(message)
        logger.info(message)

    def log_error(self, message):
        print(message)
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
            if self.cmd == True:
                print("=====================================")
                print(msg)
                print("=====================================")
            else:
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
            if self.cmd == True:
                print("=====================================")
                print(msg)
                print("=====================================")
            else:
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
            if self.cmd == True:
                print("=====================================")
                print(msg)
                print("=====================================")
            else:
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
            if self.cmd == True:
                print("=====================================")
                print(msg)
                print("=====================================")
            else:
                UserInterfaceTools(self).showMessageWindow(msg=msg)
        else:
            for subject in self.checkedSubjectList:
                subjectList.append(Subject(self, subject))
            
        return SubjectList(subjectList)

    def message(self, msg="Message in the box", title="Window Title"):
        """
        Displays a Message window with the text in "msg" and the title "title".
        """
        if self.cmd == True:
            print("=====================================")
            print(title + ": " + msg)
            print("=====================================")
        else:
            messageWindow.displayMessageSubWindow(self, "<H4>" + msg + "</H4>", title)

    def close_message(self):
        """
        Closes the message window 
        """
        if self.cmd == False:
            self.msgSubWindow.close()

    def information(self, msg="Message in the box", title="Window Title"):
        """
        Display a Window with information message and the user must press 'OK' to continue.
        """
        if self.cmd == True:
            print("=====================================")
            print("INFORMATION")
            print(title + ": " + msg)
            print("=====================================")
        else:
            QMessageBox.information(self, title, msg)

    def warning(self, msg="Message in the box", title="Window Title"):
        """
        Display a Window with warning message and the user must press 'OK' to continue.
        """
        if self.cmd == True:
            print("=====================================")
            print("WARNING")
            print(title + ": " + msg)
            print("=====================================")
        else:
            QMessageBox.warning(self, title, msg)

    def error(self, msg="Message in the box", title="Window Title"):
        """
        Display a Window with error message and the user must press 'OK' to continue.
        """
        if self.cmd == True:
            print("=====================================")
            print("ERROR")
            print(title + ": " + msg)
            print("=====================================")
        else:
            QMessageBox.critical(self, title, msg)

    def question(self, question="You wish to proceed (OK) or not (Cancel)?", title="Message Window Title"):
        """
        Displays a question window in the User Interface with the title in "title" and
        with the question in "question". The 2 strings in the arguments are the input by default.
        The user has to click either "OK" or "Cancel" in order to continue using the interface.
        It returns 0 if reply is "Cancel" and 1 if reply is "OK".
        """
        if self.cmd == True:
            print("=====================================")
            print("QUESTION")
            reply = input(question)
            print("=====================================")
            if reply == "OK" or reply == "Ok" or reply == "ok" or reply == "Y" or reply == "y" or reply == "YES" \
                or reply == "yes" or reply == "Yes" or reply == "1" or reply == '':
                return True
            else:
                return False
        else:
            buttonReply = QMessageBox.question(self, title, question, 
                          QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
            if buttonReply == QMessageBox.Ok:
                return True
            else:
                return False
    
    def select_folder(self, title="Select Folder", initial_folder=None):
        """
        Prompts a native FileDialog window where the user can select the desired folder in the system's file explorer.
        """
        if initial_folder is None:
            initial_folder = self.weaselDataFolder
        scan_directory = QFileDialog.getExistingDirectory(self, title, initial_folder, QFileDialog.ShowDirsOnly)
        if scan_directory == '':
            return None
        else:
            return scan_directory
    
    def select_file_to_read(self, title='Save file as ...', initial_folder=None, extension="All files (*.*)"):
        """
        Prompts a native FileDialog window where the user can select the desired file to read in the system's file explorer.
        """
        if initial_folder is None:
            initial_folder = self.weaselDataFolder
        filename, _ = QFileDialog.getOpenFileName(self, title, initial_folder, extension)
        if filename == '':
            return None
        else:
            return filename

    def select_file_to_save(self, title='Save file as ...', initial_folder=None, extension="All files (*.*)"):
        """
        Prompts a native FileDialog window where the user can select the desired file to save in the system's file explorer.
        """
        if initial_folder is None:
            initial_folder = self.weaselDataFolder
        filename, _ = QFileDialog.getSaveFileName(self, title, initial_folder, extension)
        if filename == '':
            return None
        else:
            return filename

    def progress_bar(self, max=1, index=0, msg="Progressing...", title="Progress Bar"):
        """
        Displays a progress bar with the unit set in "index".
        Note: launching a new progress bar at each iteration costs time, so this
        should only be used in iterations where the progress bar is updated infrequently
        For iterations with frequent updates, use progress_bar outside the iteration
        and then update_progress_bar inside the iteration
        """
        if self.cmd == True:
            print("=====================================")
            print(title + ": " + msg)
            print("=====================================")
            self.tqdm_prog = tqdm(total=max)
            self.tqdm_prog.update(index)
        else:
            messageWindow.displayMessageSubWindow(self, ("<H4>" + msg + "</H4>").format(index), title)
            messageWindow.setMsgWindowProgBarMaxValue(self, max)
            messageWindow.setMsgWindowProgBarValue(self, index)

    def update_progress_bar(self, index=0, msg=None):
        """
        Updates the progress bar with a new index.
        """
        if self.cmd == True:
            if msg is not None: print(msg)
            self.tqdm_prog.update(index)
        else:
            messageWindow.setMsgWindowProgBarValue(self, index, msg)

    def close_progress_bar(self):
        """
        Closes the Progress Bar.
        """
        if self.cmd == True and self.tqdm_prog:
            self.tqdm_prog.close()
        else:
            messageWindow.hideProgressBar(self)
            messageWindow.closeMessageSubWindow(self)

    def refresh(self, new_series_name=None):
        """
        Refreshes the Weasel display.
        """
        self.close_progress_bar()
        ui = UserInterfaceTools(self)
        ui.refreshWeasel(new_series_name=new_series_name)

    def reset_treeview(self):
        """
        Resets the Weasel treeview.
        """
        treeView.callUnCheckTreeViewItems(self)

    def close_all_windows(self):
        """
        Closes all open windows.
        """
        if self.cmd == False:
            self.mdiArea.closeAllSubWindows()

    def plot(self, signalName, maskName, x, y, x_axis_label, y_axis_label, title="Time/Curve Plot"):
        curveViewer.displayTimeCurve(self, signalName, maskName, x, y, x_axis_label, y_axis_label, title=title)
        

    def launchExternalApp(self, appWidget, title=None, icon=None):
        """This method takes a composite widget created by an external 
        application, makes it the central widget of an MDI subwindow
        and displays that subwindow in the Weasel MDI"""
        try:
            logger.info("OriginalPipelines.launchExternalApp called")
            subWindow = QMdiSubWindow()
            subWindow.setWindowFlags(Qt.CustomizeWindowHint | 
                                      Qt.WindowCloseButtonHint | 
                                      Qt.WindowMinimizeButtonHint |
                                      Qt.WindowMaximizeButtonHint)
            height, width = self.getMDIAreaDimensions()
            subWindow.setGeometry(0, 0, width, height)
            self.mdiArea.addSubWindow(subWindow)
            
            subWindow.setWidget(appWidget)

            if title is not None:
                subWindow.setWindowTitle(title)
            if icon is not None:
                subWindow.setWindowIcon(QIcon(icon))
            
            subWindow.show()
        except Exception as e:
            print('Error in OriginalPipelines.launchExternalApp: ' + str(e))
            logger.error('OriginalPipelines.launchExternalApp: ' + str(e)) 


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
    
    @staticmethod
    def pip_install_external_package(package_name, module_name=None):
        # For example, "pip install ukat" and "import ukat"
        # But "pip install opencv-python" and "import cv2"
        try:
            try:
                subprocess.check_call(["pip", "install", package_name])
            except:
                subprocess.check_call(["pip3", "install", package_name])
            if module_name:
                module = importlib.import_module(module_name)
            else:
                module = importlib.import_module(package_name)
            importlib.reload(module)
        except Exception as e:
            print('Error in OriginalPipelines.pip_install_external_package: ' + str(e))
            logger.error('OriginalPipelines.pip_install_external_package: ' + str(e)) 
