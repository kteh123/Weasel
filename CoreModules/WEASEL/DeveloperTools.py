import os
import datetime
import numpy as np
import random
import pydicom
import nibabel as nib
import copy
import itertools
import logging
import warnings
from PyQt5.QtWidgets import (QMessageBox, QFileDialog)
from ast import literal_eval # Convert strings to their actual content. Eg. "[a, b]" becomes the actual list [a, b]
import CoreModules.WEASEL.ReadDICOM_Image as ReadDICOM_Image
import CoreModules.WEASEL.SaveDICOM_Image as SaveDICOM_Image
import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.DisplayImageColour as displayImageColour
import CoreModules.WEASEL.MessageWindow as messageWindow
import CoreModules.WEASEL.InterfaceDICOMXMLFile as interfaceDICOMXMLFile
import CoreModules.WEASEL.InputDialog as inputDialog
from CoreModules.WEASEL.ViewMetaData import displayMetaDataSubWindow
logger = logging.getLogger(__name__)

class UserInterfaceTools:
    """
    This class contains functions that read the items selected in the User Interface
    and return variables that are used in processing pipelines. It also contains functions
    that allow the user to insert inputs and give an update of the pipeline steps through
    message windows. 
    """

    def __init__(self, objWeasel):
        self.objWeasel = objWeasel
    
    def __repr__(self):
       return '{}'.format(self.__class__.__name__)

    # May be redundant
    def getCurrentSubject(self):
        """
        Returns the Subject ID of the latest item selected in the Treeview.
        """
        return self.objWeasel.selecteSubject

    # May be redundant
    def getCurrentStudy(self):
        """
        Returns the Study ID of the latest item selected in the Treeview.
        """
        return self.objWeasel.selectedStudy

    # May be redundant
    def getCurrentSeries(self):
        """
        Returns the Series ID of the latest item selected in the Treeview.
        """
        return self.objWeasel.selectedSeries
    
    # May be redundant
    def getCurrentImage(self):
        """
        Returns a string with the path of the latest selected image.
        """
        return self.objWeasel.selectedImagePath
    
    # Need to do one for subjects and to include treeView.buildListsCheckedItems(self)

    def getCheckedSubjects(self):
        """
        Returns a list with objects of class Subject of the items checked in the Treeview.
        """
        subjectList = []
        subjectsTreeViewList = treeView.returnCheckedSubjects(self.objWeasel)
        if subjectsTreeViewList == []:
            self.showMessageWindow(msg="Script didn't run successfully because"
                              " no subjects were checked in the Treeview.",
                              title="No Subjects Checked")
            return 
        else:
            for subject in subjectsTreeViewList:
                subjectList.append(Subject.fromTreeView(self.objWeasel, subject))
        return subjectList

    def getCheckedStudies(self):
        """
        Returns a list with objects of class Study of the items checked in the Treeview.
        """
        studyList = []
        studiesTreeViewList = treeView.returnCheckedStudies(self.objWeasel)
        if studiesTreeViewList == []:
            self.showMessageWindow(msg="Script didn't run successfully because"
                              " no studies were checked in the Treeview.",
                              title="No Studies Checked")
            return 
        else:
            for study in studiesTreeViewList:
                studyList.append(Study.fromTreeView(self.objWeasel, study))
        return studyList
    

    def getCheckedSeries(self):
        """
        Returns a list with objects of class Series of the items checked in the Treeview.
        """
        seriesList = []
        seriesTreeViewList = treeView.returnCheckedSeries(self.objWeasel)
        if seriesTreeViewList == []:
            self.showMessageWindow(msg="Script didn't run successfully because"
                              " no series were checked in the Treeview.",
                              title="No Series Checked")
            return 
        else:
            for series in seriesTreeViewList:
                seriesList.append(Series.fromTreeView(self.objWeasel, series))
        return seriesList
    

    def getCheckedImages(self):
        """
        Returns a list with objects of class Image of the items checked in the Treeview.
        """
        imagesList = []
        imagesTreeViewList = treeView.returnCheckedImages(self.objWeasel)
        if imagesTreeViewList == []:
            self.showMessageWindow(msg="Script didn't run successfully because"
                              " no images were checked in the Treeview.",
                              title="No Images Checked")
            return
        else:
            for images in imagesTreeViewList:
                imagesList.append(Image.fromTreeView(self.objWeasel, images))
        return imagesList

    
    def showMessageWindow(self, msg="Please insert message in the function call", title="Message Window Title"):
        """
        Displays a window in the User Interface with the title in "title" and
        with the message in "msg". The 2 strings in the arguments are the input by default.
        """
        messageWindow.displayMessageSubWindow(self.objWeasel, "<H4>" + msg + "</H4>", title)


    def showInformationWindow(self, title="Message Window Title", msg="Please insert message in the function call"):
        """
        Displays an information window in the User Interface with the title in "title" and
        with the message in "msg". The 2 strings in the arguments are the input by default.
        The user has to click "OK" in order to continue using the interface.
        """
        QMessageBox.information(self.objWeasel, title, msg)


    def showErrorWindow(self, msg="Please insert message in the function call"):
        """
        Displays an error window in the User Interface with the title in "title" and
        with the message in "msg". The 2 strings in the arguments are the input by default.
        The user has to click "OK" in order to continue using the interface.
        """
        QMessageBox.critical(self.objWeasel, title, msg)


    def showQuestionWindow(self, title="Message Window Title", question="You wish to proceed (OK) or not (Cancel)?"):
        """
        Displays a question window in the User Interface with the title in "title" and
        with the question in "question". The 2 strings in the arguments are the input by default.
        The user has to click either "OK" or "Cancel" in order to continue using the interface.

        It returns 0 if reply is "Cancel" and 1 if reply is "OK".
        """
        buttonReply = QMessageBox.question(self, title, question, 
                      QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if buttonReply == QMessageBox.Ok:
            return 1
        else:
            return 0


    def closeMessageWindow(self):
        """
        Closes any message window present in the User Interface.
        """
        messageWindow.hideProgressBar(self.objWeasel)
        messageWindow.closeMessageSubWindow(self.objWeasel)


    def progressBar(self, maxNumber=1, index=0, msg="Iteration Number {}", title="Progress Bar"):
        """
        Updates the ProgressBar to the unit set in "index".
        """
        index += 1
        messageWindow.displayMessageSubWindow(self.objWeasel, ("<H4>" + msg + "</H4>").format(index), title)
        messageWindow.setMsgWindowProgBarMaxValue(self.objWeasel, maxNumber)
        messageWindow.setMsgWindowProgBarValue(self.objWeasel, index)
        return index
    

    def selectFolder(self, title="Select the directory"):
        """Displays an open folder dialog window to allow the
        user to select afolder """
        scan_directory = QFileDialog.getExistingDirectory(self.objWeasel, title, self.objWeasel.weaselDataFolder, QFileDialog.ShowDirsOnly)
        return scan_directory


    @staticmethod
    def inputWindow(paramDict, title="Input Parameters", helpText="", lists=None):
        """
        Display a window and prompts the user to insert input values in the fields of the prompted window.
        The user has the option to choose what fields and variables are present in this input window.
        The input window variables and respective types are defined in "paramDict". See below for examples.
        Variable "title" is the title of the window and "helpText" is the text
        displayed inside the window. It should be used to give important notes or 
        tips regarding the input process.

        The user may add extra validation of the parameters. Read the file
        thresholdDICOM_Image.py as it contains a good example of validation of the input parameters.

        This function is a wrap of function "ParameterInputDialog" and you can consult it's detailed documentation
        in CoreModules/WEASEL/InputDialog.py.

        Parameters
        ----------
        paramDict: Dictionary containing the input variables. The key is the field/variable name and the value is the
                   type of the variable. There are 5 possible variable types - [int, float, string, dropdownlist, listview].
                   The dictionary doesn't have any limit of number of fields, the developer can insert as many as wished.
                   The order of the fields displayed in the window is the order set in the dictionary.
                   Eg. paramDict = {"NumberStaff":"int", "Password":"string", "Course":"dropdownlist"}.
                   "NumberStaff" comes first in the window and only accepts integers, then "Password" and then "Course", which is
                   a dropdown where the user can select an option from a set of options, which is given in the parameter "lists".
                   It's possible to assign default values to the input variables. Eg.paramDict = {"NumberStaff":"int,100"} sets the
                   variable "NumberStaff" value to 100.
                   
        title: String that contains the title of the input window that is prompted.

        helpText: String that contains any text that the developer finds useful. 
                  It's the introductory text that comes before the input fields.
                  This is a good variable to write instructions of what to do and how to fill in the fields.

        lists: If the values "dropdownlist" or/and "listview" are given in paramDict, then the developer provides the list of
               options to select in this parameter. This becomes a list of lists if there is more than one of "dropdownlist" or/and "listview".
               The order of the lists in this parameter should be respective to the order of the variables in paramDict. See examples below for
               more details.

        Output
        ------
        outputList: List with the values typed or selected by the user in the prompted window.
                    It returns "None" if the Cancel button or close window are pressed.
                    Eg: if param paramDict = {"Age":"int", "Name":"string"} and the user types 
                    "30" for Age and "Weasel" for Name, then the outputList will be [30, "Weasel"].
                    If "30" and "Weasel" are the default values, then paramDict = {"Age":"int,30", "Name":"string,Weasel"}

        Eg. of paramDict using string:
            paramDict = {"Threshold":"float,0.5", "Age":"int,30"}
            The variable types are float and int. "0.5" and "30" are the default values.

        Eg. of paramDict using string:
            paramDict = {"DicomTag":"string", "TagValue":"string"}
            This a good example where "helpText" can make a difference. 
            For eg., "DicomTag" should be written in the format (XXXX,YYYY).

        Eg. of paramDict using dropdownlist and listview:
            inputDict = {"Algorithm":"dropdownlist", "Nature":"listview"}
            algorithmList = ["B0", "T2*", "T1 Molli"]
            natureList = ["Animals", "Plants", "Trees"]
            inputWindow(paramDict, lists=[algorithmList, natureList])
        """
        logger.info("UserInterfaceTools.inputWindow called")
        try:
            inputDlg = inputDialog.ParameterInputDialog(paramDict, title=title, helpText=helpText, lists=lists)
            # Return None if the user hits the Cancel button
            if inputDlg.closeInputDialog() == True: return None
            listParams = inputDlg.returnListParameterValues()
            outputList = []
            # Sometimes the values parsed could be list or hexadecimals in strings
            for param in listParams:
                try:
                    outputList.append(literal_eval(param))
                except:
                    outputList.append(param)
            return outputList
        except Exception as e:
            print('Error in function UserInterfaceTools.inputWindow: ' + str(e))
            logger.exception('Error in UserInterfaceTools.inputWindow: ' + str(e))


    def displayMetadata(self, inputPath):
        """
        Display the metadata in "inputPath" in the User Interface.
        If "inputPath" is a list, then it displays the metadata of the first image.
        """
        logger.info("UserInterfaceTools.displayMetadata called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                dataset = PixelArrayDICOMTools.getDICOMobject(inputPath)
                displayMetaDataSubWindow(self.objWeasel, "Metadata for image {}".format(inputPath), dataset)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                dataset = PixelArrayDICOMTools.getDICOMobject(inputPath[0])
                displayMetaDataSubWindow(self.objWeasel, "Metadata for image {}".format(inputPath[0]), dataset)
        except Exception as e:
            print('Error in function UserInterfaceTools.displayMetadata: ' + str(e))
            logger.exception('Error in UserInterfaceTools.displayMetadata: ' + str(e))


    def displayImages(self, inputPath, subjectID, studyID, seriesID):
        """
        Display the PixelArray in "inputPath" in the User Interface.
        """
        logger.info("UserInterfaceTools.displayImages called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                displayImageColour.displayImageSubWindow(self.objWeasel, inputPath, subjectID, seriesID, studyID)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                if len(inputPath) == 1:
                    displayImageColour.displayImageSubWindow(self.objWeasel, inputPath[0], subjectID, seriesID, studyID)
                else:
                    displayImageColour.displayMultiImageSubWindow(self.objWeasel, inputPath, subjectID, studyID, seriesID)
            return
        except Exception as e:
            print('Error in function UserInterfaceTools.displayImages: ' + str(e))
            logger.exception('Error in UserInterfaceTools.displayImages: ' + str(e))
        

    def refreshWeasel(self, new_series_name=None):
        """
        Refresh the user interface screen.
        """
        logger.info("UserInterfaceTools.refreshWeasel called")
        try:
            if new_series_name:
                treeView.refreshDICOMStudiesTreeView(self.objWeasel, newSeriesName=new_series_name)
            else:
                treeView.refreshDICOMStudiesTreeView(self.objWeasel)
        except Exception as e:
            print('Error in function UserInterfaceTools.refreshWeasel: ' + str(e))
            logger.exception('Error in UserInterfaceTools.refreshWeasel: ' + str(e))


class GenericDICOMTools:

    def __repr__(self):
       return '{}'.format(self.__class__.__name__)

    def copyDICOM(self, inputPath, series_id=None, series_uid=None, series_name=None, study_uid=None, study_name=None, patient_id=None, suffix="_Copy", output_dir=None):
        """
        Creates a DICOM copy of all files in "inputPath" (1 or more) into a new series.
        """
        logger.info("GenericDICOMTools.copyDICOM called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                if (series_id is None) and (series_uid is None):
                    series_id, series_uid = GenericDICOMTools.generateSeriesIDs(self, inputPath, studyUID=study_uid)
                elif (series_id is not None) and (series_uid is None):
                    _, series_uid = GenericDICOMTools.generateSeriesIDs(self, inputPath, seriesNumber=series_id, studyUID=study_uid)
                elif (series_id is None) and (series_uid is not None):
                    series_id = int(str(ReadDICOM_Image.getDicomDataset(inputPath).SeriesNumber) + str(random.randint(0, 9999)))
                newDataset = ReadDICOM_Image.getDicomDataset(inputPath)
                derivedPath = SaveDICOM_Image.returnFilePath(inputPath, suffix, output_folder=output_dir)
                SaveDICOM_Image.saveDicomToFile(newDataset, output_path=derivedPath)
                # The next lines perform an overwrite operation over the copied images
                if patient_id:
                        SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "PatientID", patient_id)
                if study_uid:
                    SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "StudyInstanceUID", study_uid)
                if study_name:
                    SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "StudyDescription", study_name)
                instance_uid = SaveDICOM_Image.generateUIDs(newDataset, seriesNumber=series_id, studyUID=study_uid)[2]
                SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "SOPInstanceUID", instance_uid)
                SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesInstanceUID", series_uid)
                SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesNumber", series_id)
                if series_name:
                    SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesDescription", series_name)
                else:
                    SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesDescription", str(newDataset.SeriesDescription + suffix))
                    #if hasattr(newDataset, "SeriesDescription"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesDescription", str(newDataset.SeriesDescription + suffix))
                    #elif hasattr(newDataset, "SequenceName"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "SequenceName", str(newDataset.SequenceName + suffix))
                    #elif hasattr(newDataset, "ProtocolName"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "ProtocolName", str(newDataset.ProtocolName + suffix))
                newSeriesID = interfaceDICOMXMLFile.insertNewImageInXMLFile(self, inputPath,
                                             derivedPath, suffix, newSeriesName=series_name, newStudyName=study_name, newSubjectName=patient_id)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                if (series_id is None) and (series_uid is None):
                    series_id, series_uid = GenericDICOMTools.generateSeriesIDs(self, inputPath, studyUID=study_uid)
                elif (series_id is not None) and (series_uid is None):
                    _, series_uid = GenericDICOMTools.generateSeriesIDs(self, inputPath, seriesNumber=series_id, studyUID=study_uid)
                elif (series_id is None) and (series_uid is not None):
                    series_id = int(str(ReadDICOM_Image.getDicomDataset(inputPath[0]).SeriesNumber) + str(random.randint(0, 9999)))
                derivedPath = []
                for path in inputPath:
                    newDataset = ReadDICOM_Image.getDicomDataset(path)
                    newFilePath = SaveDICOM_Image.returnFilePath(path, suffix, output_folder=output_dir)
                    SaveDICOM_Image.saveDicomToFile(newDataset, output_path=newFilePath)
                    derivedPath.append(newFilePath)
                    # The next lines perform an overwrite operation over the copied images
                    if patient_id:
                        SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "PatientID", patient_id)
                    if study_uid:
                        SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "StudyInstanceUID", study_uid)
                    if study_name:
                        SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "StudyDescription", study_name)
                    instance_uid = SaveDICOM_Image.generateUIDs(newDataset, seriesNumber=series_id, studyUID=study_uid)[2]
                    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SOPInstanceUID", instance_uid)
                    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesInstanceUID", series_uid)
                    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesNumber", series_id)
                    if series_name:
                        SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", series_name)
                    else:
                        SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", str(newDataset.SeriesDescription + suffix))
                        #if hasattr(newDataset, "SeriesDescription"):
                        #    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", str(newDataset.SeriesDescription + suffix))
                        #elif hasattr(newDataset, "SequenceName"):
                        #    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SequenceName", str(newDataset.SequenceName + suffix))
                        #elif hasattr(newDataset, "ProtocolName"):
                        #    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "ProtocolName", str(newDataset.ProtocolName + suffix))
                newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self,
                                inputPath, derivedPath, suffix, newSeriesName=series_name, newStudyName=study_name, newSubjectName=patient_id)
            return derivedPath, newSeriesID
        except Exception as e:
            print('Error in function GenericDICOMTools.copyDICOM: ' + str(e))
            logger.exception('Error in GenericDICOMTools.copyDICOM: ' + str(e))

    def deleteDICOM(self, inputPath):
        """
        This functions remove all files in inputhPath and updates the XML file accordingly.
        """
        logger.info("GenericDICOMTools.deleteDICOM called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                os.remove(inputPath)
                interfaceDICOMXMLFile.removeImageFromXMLFile(self, inputPath)
                for displayWindow in self.mdiArea.subWindowList():
                    if displayWindow.windowTitle().split(" - ")[-1] == os.path.basename(inputPath):
                        displayWindow.close()
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                for path in inputPath:
                    os.remove(path)
                interfaceDICOMXMLFile.removeMultipleImagesFromXMLFile(self, inputPath)
                for displayWindow in self.mdiArea.subWindowList():
                    if displayWindow.windowTitle().split(" - ")[-1] in list(map(os.path.basename, inputPath)):
                        displayWindow.close()
        except Exception as e:
            print('Error in function GenericDICOMTools.deleteDICOM: ' + str(e))
            logger.exception('Error in GenericDICOMTools.deleteDICOM: ' + str(e))

    def mergeDicomIntoOneSeries(self, imagePathList, series_id=None, series_name="New Series", series_uid=None, study_name=None, study_uid=None, patient_id=None, suffix="_Merged", overwrite=False, progress_bar=False):
        """
        Merges all DICOM files in "imagePathList" into 1 series.
        It creates a copy if "overwrite=False" (default).
        """
        logger.info("GenericDICOMTools.mergeDicomIntoOneSeries called")
        try:
            if os.path.exists(imagePathList[0]):
                if (series_id is None) and (series_uid is None):
                    series_id, series_uid = GenericDICOMTools.generateSeriesIDs(self, imagePathList, studyUID=study_uid)
                elif (series_id is not None) and (series_uid is None):
                    _, series_uid = GenericDICOMTools.generateSeriesIDs(self, imagePathList, seriesNumber=series_id, studyUID=study_uid)
                elif (series_id is None) and (series_uid is not None):
                    series_id = int(str(ReadDICOM_Image.getDicomDataset(imagePathList[0]).SeriesNumber) + str(random.randint(0, 9999)))
            newImagePathList = []
            if progress_bar == True: messageWindow.displayMessageSubWindow(self, ("<H4>Merging {} images</H4>").format(len(imagePathList)), "Progress Bar - Merging")
            if overwrite:
                originalPathList = imagePathList
                if progress_bar == True: messageWindow.setMsgWindowProgBarMaxValue(self, len(imagePathList))
                for index, path in enumerate(imagePathList):
                    if progress_bar == True: messageWindow.setMsgWindowProgBarValue(self, index+1)
                    if patient_id:
                        SaveDICOM_Image.overwriteDicomFileTag(path, "PatientID", patient_id)
                    if study_uid:
                        SaveDICOM_Image.overwriteDicomFileTag(path, "StudyInstanceUID", study_uid)
                    if study_name:
                        SaveDICOM_Image.overwriteDicomFileTag(path, "StudyDescription", study_name)
                    SaveDICOM_Image.overwriteDicomFileTag(path, "SeriesInstanceUID", series_uid)
                    SaveDICOM_Image.overwriteDicomFileTag(path, "SeriesNumber", series_id)
                    SaveDICOM_Image.overwriteDicomFileTag(path, "SeriesDescription", series_name)
                    #dataset = ReadDICOM_Image.getDicomDataset(path)
                    #if hasattr(dataset, "SeriesDescription"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(path, "SeriesDescription", series_name)
                    #elif hasattr(dataset, "SequenceName"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(path, "SequenceName", series_name)
                    #elif hasattr(dataset, "ProtocolName"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(path, "ProtocolName", series_name)
                newImagePathList = imagePathList
                newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self,
                                originalPathList, newImagePathList, suffix, newSeriesName=series_name, newStudyName=study_name, newSubjectName=patient_id)
                interfaceDICOMXMLFile.removeMultipleImagesFromXMLFile(self, originalPathList)
            else:
                if progress_bar == True: messageWindow.setMsgWindowProgBarMaxValue(self, len(imagePathList))
                for index, path in enumerate(imagePathList):
                    if progress_bar == True: messageWindow.setMsgWindowProgBarValue(self, index+1)
                    newDataset = ReadDICOM_Image.getDicomDataset(path)
                    newFilePath = SaveDICOM_Image.returnFilePath(path, suffix)
                    SaveDICOM_Image.saveDicomToFile(newDataset, output_path=newFilePath)
                    # The next lines perform an overwrite operation over the copied images
                    if patient_id:
                        SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "PatientID", patient_id)
                    if study_uid:
                        SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "StudyInstanceUID", study_uid)
                    if study_name:
                        SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "StudyDescription", study_name)
                    instance_uid = SaveDICOM_Image.generateUIDs(newDataset, seriesNumber=series_id, studyUID=study_uid)[2]
                    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SOPInstanceUID", instance_uid)
                    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesInstanceUID", series_uid)
                    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesNumber", series_id)
                    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", series_name)
                    #if hasattr(newDataset, "SeriesDescription"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", series_name)
                    #elif hasattr(newDataset, "SequenceName"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SequenceName", series_name)
                    #elif hasattr(newDataset, "ProtocolName"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "ProtocolName", series_name)
                    newImagePathList.append(newFilePath)
                newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self, imagePathList, newImagePathList, suffix, newSeriesName=series_name, newStudyName=study_name, newSubjectName=patient_id)
            return newImagePathList
        except Exception as e:
            print('Error in function GenericDICOMTools.mergeDicomIntoOneSeries: ' + str(e))
            logger.exception('Error in GenericDICOMTools.mergeDicomIntoOneSeries: ' + str(e))

    def generateSeriesIDs(self, inputPath, seriesNumber=None, studyUID=None):
        """
        This function generates and returns a SeriesUID and an InstanceUID.
        The SeriesUID is generated based on the StudyUID and on seriesNumber (if provided)
        The InstanceUID is generated based on SeriesUID.
        """
        logger.info("GenericDICOMTools.generateSeriesIDs called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                dataset = PixelArrayDICOMTools.getDICOMobject(inputPath)
                if seriesNumber is None:
                    (subjectID, studyID, seriesID) = self.objXMLReader.getImageParentIDs(inputPath)
                    seriesNumber = str(int(self.objXMLReader.getStudy(subjectID, studyID)[-1].attrib['id'].split('_')[0]) + 1)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                dataset = PixelArrayDICOMTools.getDICOMobject(inputPath[0])
                if seriesNumber is None:
                    (subjectID, studyID, seriesID) = self.objXMLReader.getImageParentIDs(inputPath[0])
                    seriesNumber = str(int(self.objXMLReader.getStudy(subjectID, studyID)[-1].attrib['id'].split('_')[0]) + 1)
            ids = SaveDICOM_Image.generateUIDs(dataset, seriesNumber=seriesNumber, studyUID=studyUID)
            seriesID = ids[0]
            seriesUID = ids[1]
            return seriesID, seriesUID
        except Exception as e:
            print('Error in function GenericDICOMTools.generateSeriesIDs: ' + str(e))
            logger.exception('Error in GenericDICOMTools.generateSeriesIDs: ' + str(e))

    @staticmethod
    def editDICOMTag(inputPath, dicomTag, newValue):
        """
        Overwrites all "dicomTag" of the DICOM files in "inputPath"
        with "newValue".
        """
        logger.info("GenericDICOMTools.editDICOMTag called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                SaveDICOM_Image.overwriteDicomFileTag(inputPath, dicomTag, newValue)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                for path in inputPath:
                    SaveDICOM_Image.overwriteDicomFileTag(path, dicomTag, newValue)
        except Exception as e:
            print('Error in GenericDICOMTools.editDICOMTag: ' + str(e))
            logger.exception('Error in GenericDICOMTools.editDICOMTag: ' + str(e))
        

class PixelArrayDICOMTools:

    def __repr__(self):
       return '{}'.format(self.__class__.__name__)
    
    @staticmethod
    def getPixelArrayFromDICOM(inputPath):
        """
        Returns the PixelArray of the DICOM file(s) in "inputPath".
        """
        logger.info("PixelArrayDICOMTools.getPixelArrayFromDICOM called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                pixelArray = ReadDICOM_Image.returnPixelArray(inputPath)
                return np.squeeze(pixelArray)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                pixelArray = ReadDICOM_Image.returnSeriesPixelArray(inputPath)
                return np.squeeze(pixelArray)
            else:
                return None
        except Exception as e:
            print('Error in PixelArrayDICOMTools.getPixelArrayFromDICOM: ' + str(e))
            logger.exception('Error in PixelArrayDICOMTools.getPixelArrayFromDICOM: ' + str(e))

    @staticmethod
    def getDICOMobject(inputPath):
        """
        Returns the DICOM object (or list of DICOM objects) of the file(s) in "inputPath".
        """
        logger.info("PixelArrayDICOMTools.getDICOMobject called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                dataset = ReadDICOM_Image.getDicomDataset(inputPath)
                return dataset
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                dataset = ReadDICOM_Image.getSeriesDicomDataset(inputPath)
                return dataset
            else:
                return None
        except Exception as e:
            print('Error in PixelArrayDICOMTools.getDICOMobject: ' + str(e))
            logger.exception('Error in PixelArrayDICOMTools.getDICOMobject: ' + str(e))

    def writeNewPixelArray(self, pixelArray, inputPath, suffix, series_id=None, series_uid=None, series_name=None, parametric_map=None, colourmap=None, output_dir=None):
        """
        Saves the "pixelArray" into new DICOM files with a new series, based
        on the "inputPath" and on the "suffix".
        """
        logger.info("PixelArrayDICOMTools.writeNewPixelArray called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                numImages = 1
                derivedImageList = [pixelArray]
                derivedImageFilePath = SaveDICOM_Image.returnFilePath(inputPath, suffix, output_folder=output_dir)
                derivedImagePathList = [derivedImageFilePath]

            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                if hasattr(ReadDICOM_Image.getDicomDataset(inputPath[0]), 'PerFrameFunctionalGroupsSequence'):
                    # If it's Enhanced MRI
                    numImages = 1
                    derivedImageList = [pixelArray]
                    derivedImageFilePath = SaveDICOM_Image.returnFilePath(inputPath[0], suffix, output_folder=output_dir)
                    derivedImagePathList = [derivedImageFilePath]
                else:
                    # Iterate through list of images (slices) and save the resulting Map for each DICOM image
                    numImages = (1 if len(np.shape(pixelArray)) < 3 else np.shape(pixelArray)[0])
                    derivedImagePathList = []
                    derivedImageList = []
                    for index in range(numImages):
                        derivedImageFilePath = SaveDICOM_Image.returnFilePath(inputPath[index], suffix, output_folder=output_dir)
                        derivedImagePathList.append(derivedImageFilePath)
                        if numImages==1:
                            derivedImageList.append(pixelArray)
                        else:
                            derivedImageList.append(pixelArray[index, ...])
                    if len(inputPath) > len(derivedImagePathList):
                        inputPath = inputPath[:len(derivedImagePathList)]

            if numImages == 1:
                if isinstance(inputPath, list):
                    inputPath = inputPath[0]
                SaveDICOM_Image.saveNewSingleDicomImage(derivedImagePathList[0], (''.join(inputPath)), derivedImageList[0], suffix, series_id=series_id, series_uid=series_uid, series_name=series_name, list_refs_path=[(''.join(inputPath))], parametric_map=parametric_map, colourmap=colourmap)
                # Record derived image in XML file
                interfaceDICOMXMLFile.insertNewImageInXMLFile(self, (''.join(inputPath)), derivedImagePathList[0], suffix, newSeriesName=series_name)
            else:
                SaveDICOM_Image.saveDicomNewSeries(derivedImagePathList, inputPath, derivedImageList, suffix, series_id=series_id, series_uid=series_uid, series_name=series_name, list_refs_path=[inputPath], parametric_map=parametric_map, colourmap=colourmap)
                # Insert new series into the DICOM XML file
                interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self, inputPath, derivedImagePathList, suffix, newSeriesName=series_name)            
                
            return derivedImagePathList

        except Exception as e:
            print('Error in PixelArrayDICOMTools.writeNewPixelArray: ' + str(e))
            logger.exception('Error in PixelArrayDICOMTools.writeNewPixelArray: ' + str(e))

    @staticmethod
    def overwritePixelArray(pixelArray, inputPath):
        """
        Overwrites the DICOM files in the "pixelArray" into new DICOM files with a new series, based
        on the "inputPath" and on the "suffix".
        """
        logger.info("PixelArrayDICOMTools.overwritePixelArray called")
        try:
            if isinstance(inputPath, list) and len(inputPath) > 1:
                datasetList = ReadDICOM_Image.getSeriesDicomDataset(inputPath)
                for index, dataset in enumerate(datasetList):
                    modifiedDataset = SaveDICOM_Image.createNewPixelArray(pixelArray[index], dataset)
                    SaveDICOM_Image.saveDicomToFile(modifiedDataset, output_path=inputPath[index])
            else:
                dataset = ReadDICOM_Image.getDicomDataset(inputPath)
                modifiedDataset = SaveDICOM_Image.createNewPixelArray(pixelArray, dataset)
                SaveDICOM_Image.saveDicomToFile(modifiedDataset, output_path=inputPath)
        except Exception as e:
            print('Error in PixelArrayDICOMTools.overwritePixelArray: ' + str(e))
            logger.exception('Error in PixelArrayDICOMTools.overwritePixelArray: ' + str(e))


class Project:
    def __init__(self, objWeasel):
        self.objWeasel = objWeasel
    
    def __repr__(self):
       return '{}'.format(self.__class__.__name__)

    @property
    def children(self):
        logger.info("Project.children called")
        try:
            children = []
            rootXML = self.objWeasel.objXMLReader.getXMLRoot()
            for subjectXML in rootXML:
                subjectID = subjectXML.attrib['id']
                subject = Subject(self.objWeasel, subjectID)
                children.append(subject)
            return SubjectList(children)
        except Exception as e:
            print('Error in Project.children: ' + str(e))
            logger.exception('Error in Project.children: ' + str(e))
    
    @property
    def number_children(self):
        return len(self.children)


class Subject:
    __slots__ = ('objWeasel', 'subjectID', 'suffix')
    def __init__(self, objWeasel, subjectID, suffix=None):
        self.objWeasel = objWeasel
        self.subjectID = subjectID
        self.suffix = '' if suffix is None else suffix

    def __repr__(self):
       return '{}'.format(self.__class__.__name__)
    
    @property
    def children(self):
        logger.info("Subject.children called")
        try:
            children = []
            subjectXML = self.objWeasel.objXMLReader.getSubject(self.subjectID)
            if subjectXML:
                for studyXML in subjectXML:
                    studyID = studyXML.attrib['id']
                    study = Study(self.objWeasel, self.subjectID, studyID)
                    children.append(study)
            return StudyList(children)
        except Exception as e:
            print('Error in Subject.children: ' + str(e))
            logger.exception('Error in Subject.children: ' + str(e))

    @property
    def parent(self):
        logger.info("Subject.parent called")
        try:
            return Project(self.objWeasel)
        except Exception as e:
            print('Error in Subject.parent: ' + str(e))
            logger.exception('Error in Subject.parent: ' + str(e))

    @property
    def number_children(self):
        return len(self.children)
    
    @property
    def label(self):
        logger.info("Subject.label called")
        try:
            return self.subjectID
        except Exception as e:
            print('Error in Subject.label: ' + str(e))
            logger.exception('Error in Subject.label: ' + str(e))
    
    @property
    def all_images(self):
        logger.info("Subject.all_images called")
        try:
            listImages = []
            for study in self.children:
                listImages.extend(study.all_images)
            return ImagesList(listImages)
        except Exception as e:
            print('Error in Subject.all_images: ' + str(e))
            logger.exception('Error in Subject.all_images: ' + str(e))

    @classmethod
    def fromTreeView(cls, objWeasel, subjectItem):
        subjectID = subjectItem.text(1).replace('Subject -', '').strip()
        return cls(objWeasel, subjectID)
    
    def new(self, suffix="_Copy", subjectID=None):
        logger.info("Subject.new called")
        try:
            if subjectID is None:
                subjectID = self.subjectID + suffix
            return Subject(self.objWeasel, subjectID)
        except Exception as e:
            print('Error in Subject.new: ' + str(e))
            logger.exception('Error in Subject.new: ' + str(e))

    def copy(self, suffix="_Copy", output_dir=None):
        logger.info("Subject.copy called")
        try:
            newSubjectID = self.subjectID + suffix
            for study in self.children:
                study.copy(suffix='', newSubjectID=newSubjectID, output_dir=output_dir)
            return Subject(self.objWeasel, newSubjectID)
        except Exception as e:
            print('Error in Subject.copy: ' + str(e))
            logger.exception('Error in Subject.copy: ' + str(e))

    def delete(self):
        logger.info("Subject.delete called")
        try:
            for study in self.children:
                study.delete()
            self.subjectID = ''
            #interfaceDICOMXMLFile.removeSubjectinXMLFile(self.objWeasel, self.subjectID)
        except Exception as e:
            print('Error in Subject.delete: ' + str(e))
            logger.exception('Error in Subject.delete: ' + str(e))

    def add(self, study):
        logger.info("Subject.add called")
        try:
            study.subjectID = self.subjectID
            study["PatientID"] = study.subjectID
            #interfaceDICOMXMLFile.insertNewStudyInXMLFile(self, study.subjectID, study.studyID, study.suffix)
        except Exception as e:
            print('Error in Subject.add: ' + str(e))
            logger.exception('Error in Subject.add: ' + str(e))

    @staticmethod
    def merge(listSubjects, newSubjectName=None, suffix='_Merged', overwrite=False, progress_bar=False, output_dir=None):
        logger.info("Subject.merge called")
        try:
            if newSubjectName:
                outputSubject = Subject(listSubjects[0].objWeasel, newSubjectName)
            else:
                outputSubject = listSubjects[0].new(suffix=suffix)
            # Setup Progress Bar
            progressBarTitle = "Progress Bar - Merging " + str(len(listSubjects)) + " Subjects"
            if progress_bar == True: 
                messageWindow.displayMessageSubWindow(listSubjects[0].objWeasel, ("<H4>Merging {} Subjects</H4>").format(len(listSubjects)), progressBarTitle)
                messageWindow.setMsgWindowProgBarMaxValue(listSubjects[0].objWeasel, len(listSubjects))
            # Add new subject (outputSubject) to XML
            for index, subject in enumerate(listSubjects):
                # Increment progress bar
                subjMsg = "Merging subject " + subject.subjectID
                if progress_bar == True: 
                    messageWindow.displayMessageSubWindow(listSubjects[0].objWeasel, ("<H4>" + subjMsg + "</H4>"), progressBarTitle)
                    messageWindow.setMsgWindowProgBarMaxValue(listSubjects[0].objWeasel, len(listSubjects))
                    messageWindow.setMsgWindowProgBarValue(listSubjects[0].objWeasel, index+1)
                # Overwrite or not?
                if overwrite == False:
                    for study in subject.children:
                        # Create a copy of the study into the new subject
                        studyMsg = ", study " + study.studyID
                        if progress_bar == True: 
                            messageWindow.displayMessageSubWindow(listSubjects[0].objWeasel, ("<H4>" + subjMsg + studyMsg + "</H4>"), progressBarTitle)
                            messageWindow.setMsgWindowProgBarMaxValue(listSubjects[0].objWeasel, len(listSubjects))
                            messageWindow.setMsgWindowProgBarValue(listSubjects[0].objWeasel, index+1)
                        study.copy(suffix=suffix, newSubjectID=outputSubject.subjectID, output_dir=output_dir)
                else:
                    for study in subject.children:
                        studyMsg = ", study " + study.studyID
                        if progress_bar == True: 
                            messageWindow.displayMessageSubWindow(listSubjects[0].objWeasel, ("<H4>" + subjMsg + studyMsg + "</H4>"), progressBarTitle)
                            messageWindow.setMsgWindowProgBarMaxValue(listSubjects[0].objWeasel, len(listSubjects))
                            messageWindow.setMsgWindowProgBarValue(listSubjects[0].objWeasel, index+1)
                        seriesPathsList = []
                        for series in study.children:
                            series.Item('PatientID', outputSubject.subjectID)
                            seriesPathsList.append(series.images)
                        interfaceDICOMXMLFile.insertNewStudyInXMLFile(outputSubject.objWeasel, outputSubject.subjectID, study.studyID, suffix, seriesList=seriesPathsList) # Need new Study name situation
                        # Add study to new subject in the XML
                    interfaceDICOMXMLFile.removeSubjectinXMLFile(subject.objWeasel, subject.subjectID)
            return outputSubject
        except Exception as e:
            print('Error in Subject.merge: ' + str(e))
            logger.exception('Error in Subject.merge: ' + str(e))

    def get_value(self, tag):
        logger.info("Subject.get_value called")
        try:
            if len(self.children) > 0:
                studyOutputValuesList = []
                for study in self.children:
                    studyOutputValuesList.append(study.get_value(tag)) # extend will allow long single list, while append creates list of lists
                return studyOutputValuesList
            else:
                return []
        except Exception as e:
            print('Error in Subject.get_value: ' + str(e))
            logger.exception('Error in Subject.get_value: ' + str(e))

    def set_value(self, tag, newValue):
        logger.info("Subject.set_value called")
        try:
            if len(self.children) > 0:
                for study in self.children:
                    study.set_value(tag, newValue)
        except Exception as e:
            print('Error in Subject.set_value: ' + str(e))
            logger.exception('Error in Subject.set_value: ' + str(e))
    
    def __getitem__(self, tag):
        return self.get_value(tag)

    def __setitem__(self, tag, value):
        self.set_value(tag, value)


class Study:
    __slots__ = ('objWeasel', 'subjectID', 'studyID', 'studyUID', 'suffix')
    def __init__(self, objWeasel, subjectID, studyID, studyUID=None, suffix=None):
        self.objWeasel = objWeasel
        self.subjectID = subjectID
        self.studyID = studyID
        self.studyUID = self.StudyUID if studyUID is None else studyUID
        self.suffix = '' if suffix is None else suffix
    
    def __repr__(self):
       return '{}'.format(self.__class__.__name__)

    @property
    def children(self):
        logger.info("Study.children called")
        try:
            children = []
            studyXML = self.objWeasel.objXMLReader.getStudy(self.subjectID, self.studyID)
            if studyXML:
                for seriesXML in studyXML:
                    seriesID = seriesXML.attrib['id']
                    images = []
                    for imageXML in seriesXML:
                        images.append(imageXML.find('name').text)
                    series = Series(self.objWeasel, self.subjectID, self.studyID, seriesID, listPaths=images)
                    children.append(series)
            return SeriesList(children)
        except Exception as e:
            print('Error in Study.children: ' + str(e))
            logger.exception('Error in Study.children: ' + str(e))
    
    @property
    def parent(self):
        logger.info("Study.parent called")
        try:
            return Subject(self.objWeasel, self.subjectID)
        except Exception as e:
            print('Error in Study.parent: ' + str(e))
            logger.exception('Error in Study.parent: ' + str(e))

    @property
    def number_children(self):
        return len(self.children)

    @property
    def label(self):
        logger.info("Study.label called")
        try:
            return self.studyID
        except Exception as e:
            print('Error in Study.label: ' + str(e))
            logger.exception('Error in Study.label: ' + str(e))

    @property
    def all_images(self):
        logger.info("Study.all_images called")
        try:
            listImages = []
            for series in self.children:
                listImages.extend(series.children)
            return ImagesList(listImages)
        except Exception as e:
            print('Error in Study.all_images: ' + str(e))
            logger.exception('Error in Study.all_images: ' + str(e))
    
    @classmethod
    def fromTreeView(cls, objWeasel, studyItem):
        subjectID = studyItem.parent().text(1).replace('Subject -', '').strip()
        studyID = studyItem.text(1).replace('Study -', '').strip()
        return cls(objWeasel, subjectID, studyID)

    def new(self, suffix="_Copy", studyID=None):
        logger.info("Study.new called")
        try:
            if studyID is None:
                studyID = self.studyID + suffix
            else:
                dt = datetime.datetime.now()
                time = dt.strftime('%H%M%S')
                date = dt.strftime('%Y%m%d')
                studyID = date + "_" + time + "_" + studyID + suffix
            prefixUID = '.'.join(self.studyUID.split(".", maxsplit=6)[:5]) + "." + str(random.randint(0, 9999)) + "."
            study_uid = pydicom.uid.generate_uid(prefix=prefixUID)
            return Study(self.objWeasel, self.subjectID, studyID, studyUID=study_uid, suffix=suffix)
        except Exception as e:
            print('Error in Study.new: ' + str(e))
            logger.exception('Error in Study.new: ' + str(e))

    def copy(self, suffix="_Copy", newSubjectID=None, output_dir=None):
        logger.info("Study.copy called")
        try:
            if newSubjectID:
                prefixUID = '.'.join(self.studyUID.split(".", maxsplit=6)[:5]) + "." + str(random.randint(0, 9999)) + "."
                study_uid = pydicom.uid.generate_uid(prefix=prefixUID)
                newStudyInstance = Study(self.objWeasel, newSubjectID, self.studyID + suffix, studyUID=study_uid, suffix=suffix)
            else:
                newStudyInstance = self.new(suffix=suffix)
            seriesPathsList = []
            for series in self.children:
                copiedSeries = series.copy(suffix=suffix, series_id=series.seriesID.split('_', 1)[0], series_name=series.seriesID.split('_', 1)[1], study_uid=newStudyInstance.studyUID,
                                           study_name=newStudyInstance.studyID.split('_', 1)[1].split('_', 1)[1], patient_id=newSubjectID, output_dir=output_dir)
                seriesPathsList.append(copiedSeries.images)
            #interfaceDICOMXMLFile.insertNewStudyInXMLFile(newStudyInstance.objWeasel, newStudyInstance.subjectID, newStudyInstance.studyID, suffix, seriesList=seriesPathsList)
            return newStudyInstance
        except Exception as e:
            print('Error in Study.copy: ' + str(e))
            logger.exception('Error in Study.copy: ' + str(e))

    def delete(self):
        logger.info("Study.delete called")
        try:
            for series in self.children:
                series.delete()
            #interfaceDICOMXMLFile.removeOneStudyFromSubject(self.objWeasel, self.subjectID, self.studyID)
            self.subjectID = self.studyID = ''
        except Exception as e:
            print('Error in Study.delete: ' + str(e))
            logger.exception('Error in Study.delete: ' + str(e))
    
    def add(self, series):
        logger.info("Study.add called")
        try:
            series["PatientID"] = self.subjectID
            series["StudyDate"] = self.studyID.split("_")[0]
            series["StudyTime"] = self.studyID.split("_")[1]
            series["StudyDescription"] = "".join(self.studyID.split("_")[2:])
            series["StudyInstanceUID"] = self.studyUID
            # Need to adapt the series to the new Study
            seriesNewID, seriesNewUID = GenericDICOMTools.generateSeriesIDs(self.objWeasel, series.images, studyUID=self.studyUID)
            series["SeriesNumber"] = seriesNewID
            series["SeriesInstanceUID"] = seriesNewUID
        except Exception as e:
            print('Error in Study.add: ' + str(e))
            logger.exception('Error in Study.add: ' + str(e))

    @staticmethod
    def merge(listStudies, newStudyName=None, suffix='_Merged', overwrite=False, output_dir=None, progress_bar=True):
        logger.info("Study.merge called")
        try:
            if newStudyName:
                prefixUID = '.'.join(listStudies[0].studyUID.split(".", maxsplit=6)[:5]) + "." + str(random.randint(0, 9999)) + "."
                study_uid = pydicom.uid.generate_uid(prefix=prefixUID)
                newStudyID = listStudies[0].studyID.split('_')[0] + "_" + listStudies[0].studyID.split('_')[1] + "_" + newStudyName
                outputStudy = Study(listStudies[0].objWeasel, listStudies[0].subjectID, newStudyID, studyUID=study_uid)
            else:
                outputStudy = listStudies[0].new(suffix=suffix)
            # Set up Progress Bar
            progressBarTitle = "Progress Bar - Merging " + str(len(listStudies)) + " Studies"
            if progress_bar == True: 
                messageWindow.displayMessageSubWindow(listStudies[0].objWeasel, ("<H4>Merging {} Studies</H4>").format(len(listStudies)), progressBarTitle)
                messageWindow.setMsgWindowProgBarMaxValue(listStudies[0].objWeasel, len(listStudies))
            # Add new study (outputStudy) to XML
            seriesPathsList = []
            if overwrite == False:
                for index, study in enumerate(listStudies):
                    if progress_bar == True: 
                        messageWindow.displayMessageSubWindow(listStudies[0].objWeasel, ("<H4>Merging study " + study.studyID + "</H4>"), progressBarTitle)
                        messageWindow.setMsgWindowProgBarMaxValue(listStudies[0].objWeasel, len(listStudies))
                        messageWindow.setMsgWindowProgBarValue(listStudies[0].objWeasel, index+1)
                    seriesNumber = 1
                    for series in study.children:
                        copiedSeries = series.copy(suffix=suffix, series_id=seriesNumber, series_name=series.seriesID.split('_', 1)[1], study_uid=outputStudy.studyUID,
                                                   study_name=outputStudy.studyID.split('_', 1)[1].split('_', 1)[1], patient_id=outputStudy.subjectID, output_dir=output_dir)
                        seriesPathsList.append(copiedSeries.images)
                        seriesNumber =+ 1
            else:
                seriesNumber = 1
                for index, study in enumerate(listStudies):
                    if progress_bar == True: 
                        messageWindow.displayMessageSubWindow(listStudies[0].objWeasel, ("<H4>Merging study " + study.studyID + "</H4>"), progressBarTitle)
                        messageWindow.setMsgWindowProgBarMaxValue(listStudies[0].objWeasel, len(listStudies))
                        messageWindow.setMsgWindowProgBarValue(listStudies[0].objWeasel, index+1)
                    for series in study.children:
                        series.Item('PatientID', outputStudy.subjectID)
                        series.Item('StudyInstanceUID', outputStudy.studyUID)
                        series.Item('StudyDescription', outputStudy.studyID.split('_', 1)[1].split('_', 1)[1])
                        series.Item('SeriesNumber', seriesNumber)
                        # Generate new series uid based on outputStudy.studyUID
                        _, new_series_uid = GenericDICOMTools.generateSeriesIDs(series.objWeasel, series.images, seriesNumber=seriesNumber, studyUID=outputStudy.studyUID)
                        series.Item('SeriesInstanceUID', new_series_uid)
                        seriesPathsList.append(series.images)
                        seriesNumber += 1
                    interfaceDICOMXMLFile.removeOneStudyFromSubject(study.objWeasel, study.subjectID, study.studyID)
            interfaceDICOMXMLFile.insertNewStudyInXMLFile(outputStudy.objWeasel, outputStudy.subjectID, outputStudy.studyID, suffix, seriesList=seriesPathsList)
            return outputStudy
        except Exception as e:
            print('Error in Study.merge: ' + str(e))
            logger.exception('Error in Study.merge: ' + str(e))

    @property
    def StudyUID(self):
        if len(self.children) > 0:
            return self.children[0].studyUID
        else:
            return pydicom.uid.generate_uid(prefix=None)
    
    def get_value(self, tag):
        logger.info("Study.get_value called")
        try:
            if len(self.children) > 0:
                seriesOutputValuesList = []
                for series in self.children:
                    seriesOutputValuesList.append(series.get_value(tag)) # extend will allow long single list, while append creates list of lists.
                return seriesOutputValuesList
            else:
                return []
        except Exception as e:
            print('Error in Study.get_value: ' + str(e))
            logger.exception('Error in Study.get_value: ' + str(e))

    def set_value(self, tag, newValue):
        logger.info("Study.set_value called")
        try:
            if len(self.children) > 0:
                for series in self.children:
                    series.set_value(tag, newValue)
        except Exception as e:
            print('Error in Study.set_value: ' + str(e))
            logger.exception('Error in Study.set_value: ' + str(e))

    
    def __getitem__(self, tag):
        return self.get_value(tag)

    def __setitem__(self, tag, value):
        self.set_value(tag, value)


class Series:
    __slots__ = ('objWeasel', 'subjectID', 'studyID', 'seriesID', 'studyUID', 'seriesUID', 
                 'images', 'suffix', 'referencePathsList')
    def __init__(self, objWeasel, subjectID, studyID, seriesID, listPaths=None, studyUID=None, seriesUID=None, suffix=None):
        self.objWeasel = objWeasel
        self.subjectID = subjectID
        self.studyID = studyID
        self.seriesID = seriesID
        self.images = [] if listPaths is None else listPaths
        self.studyUID = self.StudyUID if studyUID is None else studyUID
        self.seriesUID = self.SeriesUID if seriesUID is None else seriesUID
        self.suffix = '' if suffix is None else suffix
        self.referencePathsList = []
        # This is to deal with Enhanced MRI
        #if self.PydicomList and len(self.images) == 1:
        #    self.indices = list(np.arange(len(self.PydicomList[0].PerFrameFunctionalGroupsSequence))) if hasattr(self.PydicomList[0], 'PerFrameFunctionalGroupsSequence') else []
        #else:
        #    self.indices = []
    
    def __repr__(self):
       return '{}'.format(self.__class__.__name__)

    @property
    def children(self):
        logger.info("Series.children called")
        try:
            children = []
            seriesXML = self.objWeasel.objXMLReader.getSeries(self.subjectID, self.studyID, self.seriesID)
            for imageXML in seriesXML:
                image = Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, imageXML.find('name').text)
                children.append(image)
            return ImagesList(children)
        except Exception as e:
            print('Error in Series.children: ' + str(e))
            logger.exception('Error in Series.children: ' + str(e))
    
    @property
    def parent(self):
        logger.info("Series.parent called")
        try:
            return Study(self.objWeasel, self.subjectID, self.studyID, studyUID=self.studyUID)
        except Exception as e:
            print('Error in Series.parent: ' + str(e))
            logger.exception('Error in Series.parent: ' + str(e))

    @property
    def number_children(self):
        return len(self.children)

    @property
    def label(self):
        logger.info("Series.label called")
        try:
            return self.seriesID
        except Exception as e:
            print('Error in Series.label: ' + str(e))
            logger.exception('Error in Series.label: ' + str(e))

    @classmethod
    def fromTreeView(cls, objWeasel, seriesItem):
        subjectID = seriesItem.parent().parent().text(1).replace('Subject -', '').strip()
        studyID = seriesItem.parent().text(1).replace('Study -', '').strip()
        seriesID = seriesItem.text(1).replace('Series -', '').strip()
        images = objWeasel.objXMLReader.getImagePathList(subjectID, studyID, seriesID)
        return cls(objWeasel, subjectID, studyID, seriesID, listPaths=images)
    
    def new(self, suffix="_Copy", series_id=None, series_name=None, series_uid=None):
        logger.info("Series.new called")
        try:
            if series_id is None:
                series_id, _ = GenericDICOMTools.generateSeriesIDs(self.objWeasel, self.images)
            if series_name is None:
                series_name = self.seriesID.split('_', 1)[1] + suffix
            if series_uid is None:
                _, series_uid = GenericDICOMTools.generateSeriesIDs(self.objWeasel, self.images, seriesNumber=series_id)
            seriesID = str(series_id) + '_' + series_name
            newSeries = Series(self.objWeasel, self.subjectID, self.studyID, seriesID, seriesUID=series_uid, suffix=suffix)
            newSeries.referencePathsList = self.images
            return newSeries
        except Exception as e:
            print('Error in Series.new: ' + str(e))
            logger.exception('Error in Series.new: ' + str(e))
    
    def copy(self, suffix="_Copy", newSeries=True, series_id=None, series_name=None, series_uid=None, study_uid=None, study_name=None, patient_id=None, output_dir=None):
        logger.info("Series.copy called")
        try:
            if newSeries == True:
                newPathsList, newSeriesID = GenericDICOMTools.copyDICOM(self.objWeasel, self.images, series_id=series_id, series_uid=series_uid, series_name=series_name,
                                                                        study_uid=study_uid, study_name=study_name, patient_id=patient_id, suffix=suffix, output_dir=output_dir)
                return Series(self.objWeasel, self.subjectID, self.studyID, newSeriesID, listPaths=newPathsList, suffix=suffix)
            else:
                series_id = self.seriesID.split('_', 1)[0]
                series_name = self.seriesID.split('_', 1)[1]
                series_uid = self.seriesUID
                suffix = self.suffix
                newPathsList, _ = GenericDICOMTools.copyDICOM(self.objWeasel, self.images, series_id=series_id, series_uid=series_uid, series_name=series_name, study_uid=study_uid,
                                                              study_name=study_name, patient_id=patient_id,suffix=suffix, output_dir=output_dir) # StudyID in InterfaceXML
                for newCopiedImagePath in newPathsList:
                    newImage = Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, newCopiedImagePath)
                    self.add(newImage)
        except Exception as e:
            print('Error in Series.copy: ' + str(e))
            logger.exception('Error in Series.copy: ' + str(e))

    def delete(self):
        logger.info("Series.delete called")
        try:
            GenericDICOMTools.deleteDICOM(self.objWeasel, self.images)
            self.images = self.referencePathsList = []
            #self.children = self.indices = []
            #self.number_children = 0
            self.subjectID = self.studyID = self.seriesID = self.seriesUID = ''
        except Exception as e:
            print('Error in Series.delete: ' + str(e))
            logger.exception('Error in Series.delete: ' + str(e))

    def add(self, Image):
        logger.info("Series.add called")
        try:
            self.images.append(Image.path)
            # Might need XML functions
            #self.children.append(Image)
            #self.number_children = len(self.children)
        except Exception as e:
            print('Error in Series.add: ' + str(e))
            logger.exception('Error in Series.add: ' + str(e))

    def remove(self, all_images=False, Image=None):
        logger.info("Series.remove called")
        try:
            if all_images == True:
                self.images = []
                # Might need XML functions
                #self.children = []
                #self.number_children = 0
            elif Image is not None:
                self.images.remove(Image.path)
                # Might need XML functions
                #self.children.remove(Image)
                #self.number_children = len(self.children)
        except Exception as e:
            print('Error in Series.remove: ' + str(e))
            logger.exception('Error in Series.remove: ' + str(e))

    def write(self, pixelArray, output_dir=None, value_range=None, parametric_map=None, colourmap=None):
        logger.info("Series.write called")
        try:
            if isinstance(value_range, list):
                pixelArray = np.clip(pixelArray, value_range[0], value_range[1])
            else:
                list_values = np.unique(pixelArray).flatten()
                list_values = [x for x in list_values if np.isnan(x) == False]
                if np.isposinf(list_values[-1]) or np.isinf(list_values[-1]):
                    upper_value = list_values[-2]
                else:
                    upper_value = None
                if np.isneginf(list_values[0]) or np.isinf(list_values[0]):
                    lower_value = list_values[1]
                else:
                    lower_value = None
                pixelArray = np.nan_to_num(pixelArray, posinf=upper_value, neginf=lower_value)
            if self.images:
                PixelArrayDICOMTools.overwritePixelArray(pixelArray, self.images)
            else:
                series_id = self.seriesID.split('_', 1)[0]
                series_name = self.seriesID.split('_', 1)[1]
                inputReference = self.referencePathsList[0] if len(self.referencePathsList)==1 else self.referencePathsList
                outputPath = PixelArrayDICOMTools.writeNewPixelArray(self.objWeasel, pixelArray, inputReference, self.suffix, series_id=series_id, series_name=series_name, series_uid=self.seriesUID, output_dir=output_dir, parametric_map=parametric_map, colourmap=colourmap)
                self.images = outputPath
        except Exception as e:
            print('Error in Series.write: ' + str(e))
            logger.exception('Error in Series.write: ' + str(e))
    
    def read(self):
        return self.PydicomList

    def save(self, PydicomList):
        newSubjectID = self.subjectID
        newStudyID = self.studyID
        newSeriesID = self.seriesID
        for index, dataset in enumerate(PydicomList):
            changeXML = False
            if dataset.SeriesDescription != self.PydicomList[index].SeriesDescription or dataset.SeriesNumber != self.PydicomList[index].SeriesNumber:
                changeXML = True
                newSeriesID = str(dataset.SeriesNumber) + "_" + str(dataset.SeriesDescription)
            if dataset.StudyDate != self.PydicomList[index].StudyDate or dataset.StudyTime != self.PydicomList[index].StudyTime or dataset.StudyDescription != self.PydicomList[index].StudyDescription:
                changeXML = True
                newStudyID = str(dataset.StudyDate) + "_" + str(dataset.StudyTime).split(".")[0] + "_" + str(dataset.StudyDescription)
            if dataset.PatientID != self.PydicomList[index].PatientID:
                changeXML = True
                newSubjectID = str(dataset.PatientID)
            SaveDICOM_Image.saveDicomToFile(dataset, output_path=self.images[index])
            if changeXML == True:
                interfaceDICOMXMLFile.moveImageInXMLFile(self.objWeasel, self.subjectID, self.studyID, self.seriesID, newSubjectID, newStudyID, newSeriesID, self.images[index], '')
        # Only after updating the Element Tree (XML), we can change the instance values and save the DICOM file
        self.subjectID = newSubjectID
        self.studyID = newStudyID
        self.seriesID = newSeriesID

    @staticmethod
    def merge(listSeries, series_id=None, series_name='NewSeries', series_uid=None, study_name=None, study_uid=None, patient_id=None, suffix='_Merged', overwrite=False, progress_bar=False):
        logger.info("Series.merge called")
        try:
            outputSeries = listSeries[0].new(suffix=suffix, series_id=series_id, series_name=series_name, series_uid=series_uid)
            pathsList = [image for series in listSeries for image in series.images]
            outputPathList = GenericDICOMTools.mergeDicomIntoOneSeries(outputSeries.objWeasel, pathsList, series_uid=series_uid, series_id=series_id, series_name=series_name, study_name=study_name, study_uid=study_uid, patient_id=patient_id, suffix=suffix, overwrite=overwrite, progress_bar=progress_bar)
            outputSeries.images = outputPathList
            outputSeries.referencePathsList = outputPathList
            return outputSeries
        except Exception as e:
            print('Error in Series.merge: ' + str(e))
            logger.exception('Error in Series.merge: ' + str(e))
    
    # Deprecated but might be useful in the future
    #def sort(self, tagDescription, *argv):
    #    if self.Item(tagDescription) or self.Tag(tagDescription):
    #        imagePathList, _, _, indicesSorted = ReadDICOM_Image.sortSequenceByTag(self.images, tagDescription)
    #        self.images = imagePathList
    #        #if self.Multiframe: self.indices = sorted(set(indicesSorted) & set(self.indices), key=indicesSorted.index)
    #    for tag in argv:
    #        if self.Item(tag) or self.Tag(tag):
    #            imagePathList, _, _, indicesSorted = ReadDICOM_Image.sortSequenceByTag(self.images, tag)
    #            self.images = imagePathList
    #            #if self.Multiframe: self.indices = sorted(set(indicesSorted) & set(self.indices), key=indicesSorted.index)
    
    def sort(self, *argv, reverse=False):
        logger.info("Series.sort called")
        try:
            tuple_to_sort = []
            list_to_sort = [self.images]
            for tag in argv:
                if len(self.get_value(tag)) > 0:
                    list_to_sort.append(self.get_value(tag))
            for index in range(len(self.images)):
                individual_tuple = [individual_list[index] for individual_list in list_to_sort]
                tuple_to_sort.append(tuple(individual_tuple))
            tuple_sorted = sorted(tuple_to_sort, key=lambda x: x[1:], reverse=reverse)
            list_sorted_images = [individual[0] for individual in tuple_sorted]
            self.images = list_sorted_images
            return self
        except Exception as e:
            print('Error in Series.sort: ' + str(e))
            logger.exception('Error in Series.sort: ' + str(e))
    
    def where(self, tag, condition, target):
        logger.info("Series.where called")
        try:
            list_images = []
            list_paths = []
            for image in self.children:
                value = image[tag]
                statement = repr(value) + ' ' + repr(condition) + ' ' + repr(target)
                if eval(literal_eval(statement)) == True:
                    list_images.append(image)
                    list_paths.append(image.path)
            self.images = list_paths
            return self
        except Exception as e:
            print('Error in Series.where: ' + str(e))
            logger.exception('Error in Series.where: ' + str(e))

    def display(self):
        logger.info("Series.display called")
        try:
            UserInterfaceTools(self.objWeasel).displayImages(self.images, self.subjectID, self.studyID, self.seriesID)
        except Exception as e:
            print('Error in Series.display: ' + str(e))
            logger.exception('Error in Series.display: ' + str(e))

    def plot(self, xlabel="X axis", ylabel="Y axis"):
        logger.info("Series.plot called")
        try:
            for imagePath in self.images:
                image = Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, imagePath)
                image.plot(xlabel, ylabel)
        except Exception as e:
            print('Error in Series.plot: ' + str(e))
            logger.exception('Error in Series.plot: ' + str(e))

    def Metadata(self):
        logger.info("Series.Metadata called")
        try:
            UserInterfaceTools(self.objWeasel).displayMetadata(self.images)
        except Exception as e:
            print('Error in Series.Metadata: ' + str(e))
            logger.exception('Error in Series.Metadata: ' + str(e))

    @property
    def SeriesUID(self):
        if not self.images:
            self.seriesUID = None
        elif os.path.exists(self.images[0]):
            self.seriesUID = ReadDICOM_Image.getImageTagValue(self.images[0], 'SeriesInstanceUID')
        else:
            self.seriesUID = None
        return self.seriesUID

    @property
    def StudyUID(self):
        if not self.images:
            self.studyUID = None
        elif os.path.exists(self.images[0]):
            self.studyUID = ReadDICOM_Image.getImageTagValue(self.images[0], 'StudyInstanceUID')
        else:
            self.studyUID = None
        return self.studyUID

    @property
    def Magnitude(self):
        logger.info("Series.Magnitude called")
        try:
            dicomList = self.PydicomList
            magnitudeSeries = Series(self.objWeasel, self.subjectID, self.studyID, self.seriesID, listPaths=self.images)
            magnitudeSeries.remove(all_images=True)
            magnitudeSeries.referencePathsList = self.images
            for index in range(len(self.images)):
                flagMagnitude, _, _, _, _ = ReadDICOM_Image.checkImageType(dicomList[index])
                #if isinstance(flagMagnitude, list) and flagMagnitude:
                #    if len(flagMagnitude) > 1 and len(self.images) == 1:
                #        magnitudeSeries.indices = flagMagnitude
                #    magnitudeSeries.add(Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.images[index]))
                if flagMagnitude == True:
                    magnitudeSeries.add(Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.images[index]))
            return magnitudeSeries
        except Exception as e:
            print('Error in Series.Magnitude: ' + str(e))
            logger.exception('Error in Series.Magnitude: ' + str(e))

    @property
    def Phase(self):
        logger.info("Series.Phase called")
        try:
            dicomList = self.PydicomList
            phaseSeries = Series(self.objWeasel, self.subjectID, self.studyID, self.seriesID, listPaths=self.images)
            phaseSeries.remove(all_images=True)
            phaseSeries.referencePathsList = self.images
            for index in range(len(self.images)):
                _, flagPhase, _, _, _ = ReadDICOM_Image.checkImageType(dicomList[index])
                #if isinstance(flagPhase, list) and flagPhase:
                #    if len(flagPhase) > 1 and len(self.images) == 1:
                #        phaseSeries.indices = flagPhase
                #    phaseSeries.add(Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.images[index]))
                if flagPhase == True:
                    phaseSeries.add(Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.images[index]))
            return phaseSeries
        except Exception as e:
            print('Error in Series.Phase: ' + str(e))
            logger.exception('Error in Series.Phase: ' + str(e))

    @property
    def Real(self):
        logger.info("Series.Real called")
        try:
            dicomList = self.PydicomList
            realSeries = Series(self.objWeasel, self.subjectID, self.studyID, self.seriesID, listPaths=self.images)
            realSeries.remove(all_images=True)
            realSeries.referencePathsList = self.images
            for index in range(len(self.images)):
                _, _, flagReal, _, _ = ReadDICOM_Image.checkImageType(dicomList[index])
                #if isinstance(flagReal, list) and flagReal:
                #    if len(flagReal) > 1 and len(self.images) == 1:
                #        realSeries.indices = flagReal
                #    realSeries.add(Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.images[index]))
                if flagReal:
                    realSeries.add(Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.images[index]))
            return realSeries
        except Exception as e:
            print('Error in Series.Real: ' + str(e))
            logger.exception('Error in Series.Real: ' + str(e))

    @property
    def Imaginary(self):
        logger.info("Series.Imaginary called")
        try:
            dicomList = self.PydicomList
            imaginarySeries = Series(self.objWeasel, self.subjectID, self.studyID, self.seriesID, listPaths=self.images)
            imaginarySeries.remove(all_images=True)
            imaginarySeries.referencePathsList = self.images
            for index in range(len(self.images)):
                _, _, _, flagImaginary, _ = ReadDICOM_Image.checkImageType(dicomList[index])
                #if isinstance(flagImaginary, list) and flagImaginary:
                #    if len(flagImaginary) > 1 and len(self.images) == 1:
                #        imaginarySeries.indices = flagImaginary
                #    imaginarySeries.add(Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.images[index]))
                if flagImaginary:
                    imaginarySeries.add(Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.images[index]))
            return imaginarySeries
        except Exception as e:
            print('Error in Series.Imaginary: ' + str(e))
            logger.exception('Error in Series.Imaginary: ' + str(e))

    @property
    def PixelArray(self):
        logger.info("Series.PixelArray called")
        try:
            pixelArray = PixelArrayDICOMTools.getPixelArrayFromDICOM(self.images)
            return pixelArray
        except Exception as e:
            print('Error in Series.PixelArray: ' + str(e))
            logger.exception('Error in Series.PixelArray: ' + str(e))
        
    def Mask(self, maskInstance):
        """Returns the PixelArray masked."""
        logger.info("Series.Mask called")
        try:
            dataset = maskInstance.PydicomList
            mask_array = maskInstance.PixelArray
            mask_array[mask_array != 0] = 1
            mask_output = []
            if isinstance(maskInstance, Image):
                for dicomFile in self.images:
                    dataset_original = ReadDICOM_Image.getDicomDataset(dicomFile)
                    tempArray = np.zeros(np.shape(ReadDICOM_Image.getPixelArray(dataset_original)))
                    affine_results = ReadDICOM_Image.mapMaskToImage(mask_array, dataset, dataset_original)
                    if affine_results:
                        coords = zip(*affine_results)
                        tempArray[tuple(coords)] = list(np.ones(len(affine_results)).flatten())
                    mask_output.append(np.transpose(tempArray) * ReadDICOM_Image.getPixelArray(dataset_original))
                return mask_output
            elif isinstance(maskInstance, Series):
                listImages = self.images
                listMaskImages = maskInstance.images
                for dicomFile in listImages:
                    dataset_original = ReadDICOM_Image.getDicomDataset(dicomFile)
                    tempArray = np.zeros(np.shape(ReadDICOM_Image.getPixelArray(dataset_original)))
                    for maskFile in listMaskImages:
                        dataset = ReadDICOM_Image.getDicomDataset(maskFile)
                        mask_array = ReadDICOM_Image.getPixelArray(dataset)
                        mask_array[mask_array != 0] = 1
                        affine_results = ReadDICOM_Image.mapMaskToImage(mask_array, dataset, dataset_original)
                        if affine_results:
                            coords = zip(*affine_results)
                            tempArray[tuple(coords)] = list(np.ones(len(affine_results)).flatten())
                    mask_output.append(np.transpose(tempArray) * ReadDICOM_Image.getPixelArray(dataset_original))
                return mask_output
        except Exception as e:
            print('Error in Series.Mask: ' + str(e))
            logger.exception('Error in Series.Mask: ' + str(e))

    #@PixelArray.setter
    #def PixelArray(self, ROI=None):
    #    logger.info("Series.PixelArray called")
    #    try:
    #        pixelArray = PixelArrayDICOMTools.getPixelArrayFromDICOM(self.images)
    #        #if self.Multiframe:    
    #        #    tempArray = []
    #        #    for index in self.indices:
    #        #        tempArray.append(pixelArray[index, ...])
    #        #    pixelArray = np.array(tempArray)
    #        #    del tempArray
    #        if isinstance(ROI, Series):
    #            mask = np.zeros(np.shape(pixelArray))
    #            coords = ROI.ROIindices
    #            mask[tuple(zip(*coords))] = list(np.ones(len(coords)).flatten())
    #            #pixelArray = pixelArray * mask
    #            pixelArray = np.extract(mask.astype(bool), pixelArray)
    #        elif ROI == None:
    #            pass
    #        else:
    #            warnings.warn("The input argument ROI should be a Series instance.") 
    #        return pixelArray
    #    except Exception as e:
    #        print('Error in Series.PixelArray: ' + str(e))
    #        logger.exception('Error in Series.PixelArray: ' + str(e))

    @property
    def Affine(self):
        logger.info("Series.Affine called")
        try:
            return ReadDICOM_Image.returnAffineArray(self.images[0])
        except Exception as e:
            print('Error in Series.Affine: ' + str(e))
            logger.exception('Error in Series.Affine: ' + str(e))

    @property
    def ListAffines(self):
        logger.info("Series.ListAffines called")
        try:
            return [ReadDICOM_Image.returnAffineArray(image) for image in self.images]
        except Exception as e:
            print('Error in Series.ListAffines: ' + str(e))
            logger.exception('Error in Series.ListAffines: ' + str(e))
    
    @property
    def ROIindices(self):
        logger.info("Series.ROIindices called")
        try:
            tempImage = self.PixelArray
            tempImage[tempImage != 0] = 1
            return np.transpose(np.where(tempImage == 1))
        except Exception as e:
            print('Error in Series.ROIindices: ' + str(e))
            logger.exception('Error in Series.ROIindices: ' + str(e))
    
    def get_value(self, tag):
        logger.info("Series.get_value called")
        try:
            if self.images:
                if isinstance(tag, list):
                    outputValuesList = []
                    for ind_tag in tag:
                        outputValuesList.append(ReadDICOM_Image.getSeriesTagValues(self.images, ind_tag)[0])
                    return outputValuesList
                else:
                    return ReadDICOM_Image.getSeriesTagValues(self.images, tag)[0]
            else:
                return []
        except Exception as e:
            print('Error in Series.get_value: ' + str(e))
            logger.exception('Error in Series.get_value: ' + str(e))

    def set_value(self, tag, newValue):
        logger.info("Series.set_value called")
        try:
            if self.images:
                comparisonDicom = self.PydicomList
                oldSubjectID = self.subjectID
                oldStudyID = self.studyID
                oldSeriesID = self.seriesID
                if isinstance(tag, list) and isinstance(newValue, list):
                    for index, ind_tag in enumerate(tag):
                        GenericDICOMTools.editDICOMTag(self.images, ind_tag, newValue[index])
                else:
                    GenericDICOMTools.editDICOMTag(self.images, tag, newValue)
                newDicomList = self.PydicomList
                # Consider the case where other XML fields are changed
                for index, dataset in enumerate(comparisonDicom):
                    changeXML = False
                    if dataset.SeriesDescription != newDicomList[index].SeriesDescription or dataset.SeriesNumber != newDicomList[index].SeriesNumber:
                        changeXML = True
                        newSeriesID = str(newDicomList[index].SeriesNumber) + "_" + str(newDicomList[index].SeriesDescription)
                        self.seriesID = newSeriesID
                    else:
                        newSeriesID = oldSeriesID
                    if dataset.StudyDate != newDicomList[index].StudyDate or dataset.StudyTime != newDicomList[index].StudyTime or dataset.StudyDescription != newDicomList[index].StudyDescription:
                        changeXML = True
                        newStudyID = str(newDicomList[index].StudyDate) + "_" + str(newDicomList[index].StudyTime).split(".")[0] + "_" + str(newDicomList[index].StudyDescription)
                        self.studyID = newStudyID
                    else:
                        newStudyID = oldStudyID
                    if dataset.PatientID != newDicomList[index].PatientID:
                        changeXML = True
                        newSubjectID = str(newDicomList[index].PatientID)
                        self.subjectID = newSubjectID
                    else:
                        newSubjectID = oldSubjectID
                    if changeXML == True:
                        interfaceDICOMXMLFile.moveImageInXMLFile(self.objWeasel, oldSubjectID, oldStudyID, oldSeriesID, newSubjectID, newStudyID, newSeriesID, self.images[index], '')
        except Exception as e:
            print('Error in Series.set_value: ' + str(e))
            logger.exception('Error in Series.set_value: ' + str(e))

    def __getitem__(self, tag):
        return self.get_value(tag)

    def __setitem__(self, tag, value):
        self.set_value(tag, value)

    # Remove this function in the future - Careful with Subject.merge and Study.merge implications!
    def Item(self, tagDescription, newValue=None):
        if self.images:
            if newValue:
                GenericDICOMTools.editDICOMTag(self.images, tagDescription, newValue)
                if (tagDescription == 'SeriesDescription') or (tagDescription == 'SequenceName') or (tagDescription == 'ProtocolName'):
                    interfaceDICOMXMLFile.renameSeriesinXMLFile(self.objWeasel, self.images, series_name=newValue)
                elif tagDescription == 'SeriesNumber':
                    interfaceDICOMXMLFile.renameSeriesinXMLFile(self.objWeasel, self.images, series_id=newValue)
            itemList, _ = ReadDICOM_Image.getSeriesTagValues(self.images, tagDescription)
            #if self.Multiframe: 
            #    tempList = [itemList[index] for index in self.indices]
            #    itemList = tempList
            #    del tempList
        else:
            itemList = []
        return itemList
    
    @property
    def PydicomList(self):
        if self.images:
            return PixelArrayDICOMTools.getDICOMobject(self.images)
        else:
            return []
    
    #@property
    #def Multiframe(self):
    #    if self.indices:
    #        return True
    #    else:
    #        return False

    def export_as_nifti(self, directory=None, filename=None):
        logger.info("Series.export_as_nifti called")
        try:
            if directory is None: directory=os.path.dirname(self.images[0])
            if filename is None: filename=self.seriesID
            dicomHeader = nib.nifti1.Nifti1DicomExtension(2, self.PydicomList[0])
            niftiObj = nib.Nifti1Image(np.rot90(np.transpose(self.PixelArray)), self.Affine)
            # The transpose is necessary in this case to be in line with the rest of WEASEL. The rot90() can be a bit questionable, so this should be tested in as much data as possible.
            niftiObj.header.extensions.append(dicomHeader)
            nib.save(niftiObj, directory + '/' + filename + '.nii.gz')
        except Exception as e:
            print('Error in Series.export_as_nifti: ' + str(e))
            logger.exception('Error in Series.export_as_nifti: ' + str(e))


class Image:
    __slots__ = ('objWeasel', 'subjectID', 'studyID', 'seriesID', 'path', 'seriesUID',
                 'studyUID', 'suffix', 'referencePath')
    def __init__(self, objWeasel, subjectID, studyID, seriesID, path, suffix=None):
        self.objWeasel = objWeasel
        self.subjectID = subjectID
        self.studyID = studyID
        self.seriesID = seriesID
        self.path = path
        self.seriesUID = self.SeriesUID
        self.studyUID = self.StudyUID
        self.suffix = '' if suffix is None else suffix
        self.referencePath = ''

    def __repr__(self):
       return '{}'.format(self.__class__.__name__)

    @property
    def parent(self):
        logger.info("Image.parent called")
        try:
            temp_series = Series(self.objWeasel, self.subjectID, self.studyID, self.seriesID, studyUID=self.studyUID, seriesUID=self.seriesUID)
            paths = []
            images_of_series = temp_series.children
            for image in images_of_series:
                paths.append(image.path)
            del temp_series, images_of_series
            return Series(self.objWeasel, self.subjectID, self.studyID, self.seriesID, listPaths=paths, studyUID=self.studyUID, seriesUID=self.seriesUID)
        except Exception as e:
            print('Error in Image.parent: ' + str(e))
            logger.exception('Error in Image.parent: ' + str(e))

    @classmethod
    def fromTreeView(cls, objWeasel, imageItem):
        subjectID = imageItem.parent().parent().parent().text(1).replace('Subject -', '').strip()
        studyID = imageItem.parent().parent().text(1).replace('Study -', '').strip()
        seriesID = imageItem.parent().text(1).replace('Series -', '').strip()
        path = imageItem.text(4)
        return cls(objWeasel, subjectID, studyID, seriesID, path)
    
    @staticmethod
    def newSeriesFrom(listImages, suffix='_Copy', series_id=None, series_name=None, series_uid=None):
        logger.info("Image.newSeriesFrom called")
        try:
            pathsList = [image.path for image in listImages]
            if series_id is None:
                series_id, _ = GenericDICOMTools.generateSeriesIDs(listImages[0].objWeasel, pathsList)
            if series_name is None:
                series_name = listImages[0].seriesID.split('_', 1)[1] + suffix
            if series_uid is None:
                _, series_uid = GenericDICOMTools.generateSeriesIDs(listImages[0].objWeasel, pathsList, seriesNumber=series_id)
            seriesID = str(series_id) + '_' + series_name
            newSeries = Series(listImages[0].objWeasel, listImages[0].subjectID, listImages[0].studyID, seriesID, seriesUID=series_uid, suffix=suffix)
            newSeries.referencePathsList = pathsList
            return newSeries
        except Exception as e:
            print('Error in Image.newSeriesFrom: ' + str(e))
            logger.exception('Error in Image.newSeriesFrom: ' + str(e))
        
    @property
    def label(self):
        logger.info("Image.label called")
        try:
            return treeView.returnImageName(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.path)
        except Exception as e:
            print('Error in Image.label: ' + str(e))
            logger.exception('Error in Image.label: ' + str(e))

    def new(self, suffix='_Copy', series=None):
        logger.info("Image.new called")
        try:
            if series is None:
                newImage = Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, '', suffix=suffix)
            else:
                newImage = Image(series.objWeasel, series.subjectID, series.studyID, series.seriesID, '', suffix=suffix)
            newImage.referencePath = self.path
            return newImage
        except Exception as e:
            print('Error in Image.new: ' + str(e))
            logger.exception('Error in Image.new: ' + str(e))

    def copy(self, suffix='_Copy', series=None, output_dir=None):
        logger.info("Image.copy called")
        try:
            if series is None:
                series_id = self.seriesID.split('_', 1)[0]
                series_name = self.seriesID.split('_', 1)[1]
                series_uid = self.seriesUID
                #suffix = self.suffix
            else:
                series_id = series.seriesID.split('_', 1)[0]
                series_name = series.seriesID.split('_', 1)[1]
                series_uid = series.seriesUID
                suffix = series.suffix
            newPath, newSeriesID = GenericDICOMTools.copyDICOM(self.objWeasel, self.path, series_id=series_id, series_uid=series_uid, series_name=series_name, suffix=suffix, output_dir=output_dir)
            copiedImage = Image(self.objWeasel, self.subjectID, self.studyID, newSeriesID, newPath, suffix=suffix)
            if series: series.add(copiedImage)
            return copiedImage
        except Exception as e:
            print('Error in Image.copy: ' + str(e))
            logger.exception('Error in Image.copy: ' + str(e))

    def delete(self):
        logger.info("Image.delete called")
        try:
            GenericDICOMTools.deleteDICOM(self.objWeasel, self.path)
            self.path = []
            self.referencePath = []
            self.subjectID = self.studyID = self.seriesID = ''
            # Delete the instance, such as del self???
        except Exception as e:
            print('Error in Image.delete: ' + str(e))
            logger.exception('Error in Image.delete: ' + str(e))

    def write(self, pixelArray, series=None, output_dir=None, value_range=None, parametric_map=None, colourmap=None):
        logger.info("Image.write called")
        try:
            if isinstance(value_range, list):
                pixelArray = np.clip(pixelArray, value_range[0], value_range[1])
            else:
                list_values = np.unique(pixelArray).flatten()
                list_values = [x for x in list_values if np.isnan(x) == False]
                if np.isposinf(list_values[-1]) or np.isinf(list_values[-1]):
                    upper_value = list_values[-2]
                else:
                    upper_value = None
                if np.isneginf(list_values[0]) or np.isinf(list_values[0]):
                    lower_value = list_values[1]
                else:
                    lower_value = None
                pixelArray = np.nan_to_num(pixelArray, posinf=upper_value, neginf=lower_value)
            if os.path.exists(self.path):
                PixelArrayDICOMTools.overwritePixelArray(pixelArray, self.path) # Include Colourmap and Parametric Map
            else:
                if series is None:
                    series_id = self.seriesID.split('_', 1)[0]
                    series_name = self.seriesID.split('_', 1)[1]
                    series_uid = self.seriesUID
                else:
                    series_id = series.seriesID.split('_', 1)[0]
                    series_name = series.seriesID.split('_', 1)[1]
                    series_uid = series.seriesUID
                outputPath = PixelArrayDICOMTools.writeNewPixelArray(self.objWeasel, pixelArray, self.referencePath, self.suffix, series_id=series_id, series_name=series_name, series_uid=series_uid, parametric_map=parametric_map, output_dir=output_dir, colourmap=colourmap)
                self.path = outputPath[0]
                if series: series.add(self)
        except Exception as e:
            print('Error in Image.write: ' + str(e))
            logger.exception('Error in Image.write: ' + str(e))
        
    def read(self):
        return self.PydicomObject

    def save(self, PydicomObject):
        changeXML = False
        newSubjectID = self.subjectID
        newStudyID = self.studyID
        newSeriesID = self.seriesID
        if PydicomObject.SeriesDescription != self.PydicomObject.SeriesDescription or PydicomObject.SeriesNumber != self.PydicomObject.SeriesNumber:
            changeXML = True
            newSeriesID = str(PydicomObject.SeriesNumber) + "_" + str(PydicomObject.SeriesDescription)
        if PydicomObject.StudyDate != self.PydicomObject.StudyDate or PydicomObject.StudyTime != self.PydicomObject.StudyTime or PydicomObject.StudyDescription != self.PydicomObject.StudyDescription:
            changeXML = True
            newStudyID = str(PydicomObject.StudyDate) + "_" + str(PydicomObject.StudyTime).split(".")[0] + "_" + str(PydicomObject.StudyDescription)
        if PydicomObject.PatientID != self.PydicomObject.PatientID:
            changeXML = True
            newSubjectID = str(PydicomObject.PatientID)
        SaveDICOM_Image.saveDicomToFile(PydicomObject, output_path=self.path)
        if changeXML == True:
            interfaceDICOMXMLFile.moveImageInXMLFile(self.objWeasel, self.subjectID, self.studyID, self.seriesID, newSubjectID, newStudyID, newSeriesID, self.path, '')
        # Only after updating the Element Tree (XML), we can change the instance values and save the DICOM file
        self.subjectID = newSubjectID
        self.studyID = newStudyID
        self.seriesID = newSeriesID

    @staticmethod
    def merge(listImages, series_id=None, series_name='NewSeries', series_uid=None, study_name=None, study_uid=None, patient_id=None, suffix='_Merged', overwrite=False, progress_bar=False):
        logger.info("Image.merge called")
        try:
            outputSeries = Image.newSeriesFrom(listImages, suffix=suffix, series_id=series_id, series_name=series_name, series_uid=series_uid)    
            outputPathList = GenericDICOMTools.mergeDicomIntoOneSeries(outputSeries.objWeasel, outputSeries.referencePathsList, series_uid=series_uid, series_id=series_id, series_name=series_name, study_name=study_name, study_uid=study_uid, patient_id=patient_id, suffix=suffix, overwrite=overwrite, progress_bar=progress_bar)
            outputSeries.images = outputPathList
            return outputSeries
        except Exception as e:
            print('Error in Image.merge: ' + str(e))
            logger.exception('Error in Image.merge: ' + str(e))
    
    def display(self):
        logger.info("Image.display called")
        try:
            UserInterfaceTools(self.objWeasel).displayImages(self.path, self.subjectID, self.studyID, self.seriesID)
        except Exception as e:
            print('Error in Image.display: ' + str(e))
            logger.exception('Error in Image.display: ' + str(e))

    @staticmethod
    def displayListImages(listImages):
        logger.info("Image.displayListImages called")
        try:
            pathsList = [image.path for image in listImages]
            UserInterfaceTools(listImages[0].objWeasel).displayImages(pathsList, listImages[0].subjectID, listImages[0].studyID, listImages[0].seriesID)
        except Exception as e:
            print('Error in Image.displayListImages: ' + str(e))
            logger.exception('Error in Image.displayListImages: ' + str(e))

    def plot(self, xlabel="X axis", ylabel="Y axis"):
        logger.info("Image.plot called")
        try:
            self.objWeasel.plot(self.path, self.seriesID, self.PixelArray[0], self.PixelArray[1], xlabel, ylabel)
        except Exception as e:
            print('Error in Image.plot: ' + str(e))
            logger.exception('Error in Image.plot: ' + str(e))

    @property
    def SeriesUID(self):
        if not self.path:
            self.seriesUID = None
        elif os.path.exists(self.path):
            self.seriesUID = ReadDICOM_Image.getImageTagValue(self.path, 'SeriesInstanceUID')
        else:
            self.seriesUID = None
        return self.seriesUID
    
    @property
    def StudyUID(self):
        if not self.path:
            self.studyUID = None
        elif os.path.exists(self.path):
            self.studyUID = ReadDICOM_Image.getImageTagValue(self.path, 'StudyInstanceUID')
        else:
            self.studyUID = None
        return self.studyUID
    
    def Metadata(self):
        logger.info("Image.Metadata called")
        try:
            UserInterfaceTools(self.objWeasel).displayMetadata(self.path)
        except Exception as e:
            print('Error in Image.Metadata: ' + str(e))
            logger.exception('Error in Image.Metadata: ' + str(e))

    @property
    def PixelArray(self):
        logger.info("Image.PixelArray called")
        try:
            pixelArray = PixelArrayDICOMTools.getPixelArrayFromDICOM(self.path)
            return pixelArray
        except Exception as e:
            print('Error in Image.PixelArray: ' + str(e))
            logger.exception('Error in Image.PixelArray: ' + str(e))

    def Mask(self, maskInstance):
        """Returns the PixelArray masked."""
        logger.info("Image.Mask called")
        try:
            if isinstance(maskInstance, Image):
                #for index, dicomFile in enumerate(targetPath):
                tempArray = np.zeros(np.shape(self.PixelArray))
                dataset_original = self.PydicomObject
                dataset = maskInstance.PydicomObject
                mask_array = maskInstance.PixelArray
                mask_array[mask_array != 0] = 1
                affine_results = ReadDICOM_Image.mapMaskToImage(mask_array, dataset, dataset_original)
                if affine_results:
                    coords = zip(*affine_results)
                    tempArray[tuple(coords)] = list(np.ones(len(affine_results)).flatten())
                return np.transpose(tempArray) * self.PixelArray
            elif isinstance(maskInstance, Series):
                tempArray = np.zeros(np.shape(self.PixelArray))
                for maskFile in maskInstance.images:
                    dataset_original = self.PydicomObject
                    dataset = ReadDICOM_Image.getDicomDataset(maskFile)
                    mask_array = ReadDICOM_Image.getPixelArray(dataset)
                    mask_array[mask_array != 0] = 1
                    affine_results = ReadDICOM_Image.mapMaskToImage(mask_array, dataset, dataset_original)
                    if affine_results:
                        coords = zip(*affine_results)
                        tempArray[tuple(coords)] = list(np.ones(len(affine_results)).flatten())
                return np.transpose(tempArray) * self.PixelArray
        except Exception as e:
            print('Error in Image.Mask: ' + str(e))
            logger.exception('Error in Image.Mask: ' + str(e))
    
    #@property
    #def PixelArray(self, ROI=None):
    #    logger.info("Image.PixelArray called")
    #    try:
    #        pixelArray = PixelArrayDICOMTools.getPixelArrayFromDICOM(self.path)
    #        if isinstance(ROI, Image):
    #            mask = np.zeros(np.shape(pixelArray))
    #            coords = ROI.ROIindices
    #            mask[tuple(zip(*coords))] = list(np.ones(len(coords)).flatten())
    #            #pixelArray = pixelArray * mask
    #            pixelArray = np.extract(mask.astype(bool), pixelArray)
    #        elif ROI == None:
    #            pass
    #        else:
    #            warnings.warn("The input argument ROI should be an Image instance.") 
    #        return pixelArray
    #    except Exception as e:
    #        print('Error in Image.PixelArray: ' + str(e))
    #        logger.exception('Error in Image.PixelArray: ' + str(e))
    
    @property
    def ROIindices(self):
        logger.info("Image.ROIindices called")
        try:
            tempImage = self.PixelArray
            tempImage[tempImage != 0] = 1
            return np.transpose(np.where(tempImage == 1))
        except Exception as e:
            print('Error in Image.ROIindices: ' + str(e))
            logger.exception('Error in Image.ROIindices: ' + str(e))

    @property
    def Affine(self):
        logger.info("Image.Affine called")
        try:
            return ReadDICOM_Image.returnAffineArray(self.path)
        except Exception as e:
            print('Error in Image.Affine: ' + str(e))
            logger.exception('Error in Image.Affine: ' + str(e))
    
    def get_value(self, tag):
        logger.info("Image.get_value called")
        try:
            if isinstance(tag, list):
                outputValuesList = []
                for ind_tag in tag:
                    outputValuesList.append(ReadDICOM_Image.getImageTagValue(self.path, ind_tag))
                return outputValuesList
            else:
                return ReadDICOM_Image.getImageTagValue(self.path, tag)
        except Exception as e:
            print('Error in Image.get_value: ' + str(e))
            logger.exception('Error in Image.get_value: ' + str(e))

    def set_value(self, tag, newValue):
        logger.info("Image.set_value called")
        try:
            comparisonDicom = self.PydicomObject
            changeXML = False
            # Not necessary new IDs, but they may be new. The changeXML flag coordinates that.
            oldSubjectID = self.subjectID
            oldStudyID = self.studyID
            oldSeriesID = self.seriesID
            # Set tag commands
            if isinstance(tag, list) and isinstance(newValue, list):
                for index, ind_tag in enumerate(tag):
                    GenericDICOMTools.editDICOMTag(self.path, ind_tag, newValue[index])
            else:
                GenericDICOMTools.editDICOMTag(self.path, tag, newValue)
            # Consider the case where XML fields are changed
            if comparisonDicom.SeriesDescription != self.PydicomObject.SeriesDescription or comparisonDicom.SeriesNumber != self.PydicomObject.SeriesNumber:
                changeXML = True
                newSeriesID = str(self.PydicomObject.SeriesNumber) + "_" + str(self.PydicomObject.SeriesDescription)
                self.seriesID = newSeriesID
            else:
                newSeriesID = oldSeriesID
            if comparisonDicom.StudyDate != self.PydicomObject.StudyDate or comparisonDicom.StudyTime != self.PydicomObject.StudyTime or comparisonDicom.StudyDescription != self.PydicomObject.StudyDescription:
                changeXML = True
                newStudyID = str(self.PydicomObject.StudyDate) + "_" + str(self.PydicomObject.StudyTime).split(".")[0] + "_" + str(self.PydicomObject.StudyDescription)
                self.studyID = newStudyID
            else:
                newStudyID = oldStudyID
            if comparisonDicom.PatientID != self.PydicomObject.PatientID:
                changeXML = True
                newSubjectID = str(self.PydicomObject.PatientID)
                self.subjectID = newSubjectID
            else:
                newSubjectID = oldSubjectID
            if changeXML == True:
                interfaceDICOMXMLFile.moveImageInXMLFile(self.objWeasel, oldSubjectID, oldStudyID, oldSeriesID, newSubjectID, newStudyID, newSeriesID, self.path, '')
        except Exception as e:
            print('Error in Image.set_value: ' + str(e))
            logger.exception('Error in Image.set_value: ' + str(e))
        
    def __getitem__(self, tag):
        return self.get_value(tag)

    def __setitem__(self, tag, value):
        self.set_value(tag, value)

    @property
    def PydicomObject(self):
        if self.path:
            return PixelArrayDICOMTools.getDICOMobject(self.path)
        else:
            return []

    def export_as_nifti(self, directory=None, filename=None):
        logger.info("Image.export_as_nifti called")
        try:
            if directory is None: directory=os.path.dirname(self.path)
            if filename is None: filename=self.seriesID
            dicomHeader = nib.nifti1.Nifti1DicomExtension(2, self.PydicomObject)
            niftiObj = nib.Nifti1Image(np.rot90(np.transpose(self.PixelArray)), affine=self.Affine)
            # The transpose is necessary in this case to be in line with the rest of WEASEL.
            niftiObj.header.extensions.append(dicomHeader)
            nib.save(niftiObj, directory + '/' + filename + '.nii.gz')
        except Exception as e:
            print('Error in Image.export_as_nifti: ' + str(e))
            logger.exception('Error in Image.export_as_nifti: ' + str(e))

from Scripting.OriginalPipelines import ImagesList, SeriesList, StudyList, SubjectList