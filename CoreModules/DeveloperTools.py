import os
import time
import numpy as np
import random
import pydicom
import nibabel as nib
import copy
import itertools
import warnings
from PyQt5.QtWidgets import (QMessageBox, QFileDialog)
from ast import literal_eval # Convert strings to their actual content. Eg. "[a, b]" becomes the actual list [a, b]
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image
import CoreModules.WEASEL.saveDICOM_Image as saveDICOM_Image
import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.DisplayImageColour as displayImageColour
import CoreModules.WEASEL.MessageWindow as messageWindow
import CoreModules.WEASEL.InterfaceDICOMXMLFile as interfaceDICOMXMLFile
import CoreModules.WEASEL.InputDialog as inputDialog
from Pipelines.ViewMetaData import displayMetaDataSubWindow


class UserInterfaceTools:
    """
    This class contains functions that read the items selected in the User Interface
    and return variables that are used in processing pipelines. It also contains functions
    that allow the user to insert inputs and give an update of the pipeline steps through
    message windows. 
    """

    def __init__(self, objWeasel):
        self.objWeasel = objWeasel
    

    def getCurrentStudy(self):
        """
        Returns the Study ID of the latest item selected in the Treeview.
        """
        return self.objWeasel.selectedStudy
    

    def getCurrentSeries(self):
        """
        Returns the Series ID of the latest item selected in the Treeview.
        """
        return self.objWeasel.selectedSeries
    

    def getCurrentImage(self):
        """
        Returns a string with the path of the latest selected image.
        """
        return self.objWeasel.selectedImagePath


    def getSelectedStudies(self):
        """
        Returns a list with objects of class Study of the items selected in the Treeview.
        """
        studyList = []
        studiesTreeViewList = treeView.returnSelectedStudies(self.objWeasel)
        if studiesTreeViewList == []:
            self.showMessageWindow(msg="Script didn't run successfully because"
                              " no studies were selected in the Treeview.",
                              title="No Studies Selected")
            return
        else:
            for study in studiesTreeViewList:
                studyList.append(Study.fromTreeView(self.objWeasel, study))
        return studyList


    def getSelectedSeries(self):
        """
        Returns a list with objects of class Series of the items selected in the Treeview.
        """
        seriesList = []
        seriesTreeViewList = treeView.returnSelectedSeries(self.objWeasel)
        if seriesTreeViewList == []:
            self.showMessageWindow(msg="Script didn't run successfully because"
                              " no series were selected in the Treeview.",
                              title="No Series Selected")
            return
        else:
            for series in seriesTreeViewList:
                seriesList.append(Series.fromTreeView(self.objWeasel, series))
        return seriesList


    def getSelectedImages(self):
        """
        Returns a list with objects of class Image of the items selected in the Treeview.
        """
        imagesList = []
        imagesTreeViewList = treeView.returnSelectedImages(self.objWeasel)
        if imagesTreeViewList == []:
            self.showMessageWindow(msg="Script didn't run successfully because"
                              " no images were selected in the Treeview.",
                              title="No Images Selected")
            return
        else:
            for images in imagesTreeViewList:
                imagesList.append(Image.fromTreeView(self.objWeasel, images))
        return imagesList
    

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


    def getImagesFromSeries(self, studyID=None, seriesID=None):
        """
        Returns a list of strings with the paths of all images in (studyID, seriesID).
        """
        if (studyID is None) or (seriesID is None):
            studyID = self.getCurrentStudy()
            seriesID = self.getCurrentSeries()
        return self.objWeasel.objXMLReader.getImagePathList(studyID, seriesID)


    def getSeriesFromImages(self, inputPath):
        """
        Returns a list of strings with the paths of all images in (studyID, seriesID).
        """
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                (subjectID, studyID, seriesID) = treeView.getPathParentNode(self.objWeasel, inputPath)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                (subjectID, studyID, seriesID) = treeView.getPathParentNode(self.objWeasel, inputPath[0])
            return seriesID
        except Exception as e:
            print('Error in function #.getSeriesFromImages: ' + str(e))

    
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
        Display a window and prompts the user to insert inputs. The input variables
        and respective types are defined in "paramDict". See below for examples.
        Variable "title" is the title of the window and "helpText" is the text
        displayed inside the window. It should be used to give important notes or 
        tips regarding the input process.

        Eg. of paramDict:
            paramDict = {"Tag":"string", "Value":"string"}
            The variable types are int, float and string.
            The user may add extra validation of the parameters. Read the file
            thresholdDICOM_Image.py as it contains a good example of validation.
        Other eg. of paramDict:
            inputDict = {"Algorithm":"dropdownlist", "Nature":"listview"}
            algorithmList = ["B0", "T2*", "T1 Molli"]
            natureList = ["Animals", "Plants", "Trees"]
            inputWindow(paramDict, ..., lists=[algorithmList, natureList])
        """
        try:
            inputDlg = inputDialog.ParameterInputDialog(paramDict, title=title, helpText=helpText, lists=lists)
            # Return None if the user hits the Cancel button
            if inputDlg.closeInputDialog() == True:
                return None
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
            print('Error in function #.inputWindow: ' + str(e))


    def displayMetadata(self, inputPath):
        """
        Display the metadata in "inputPath" in the User Interface.
        If "inputPath" is a list, then it displays the metadata of the first image.
        """
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                dataset = PixelArrayDICOMTools.getDICOMobject(inputPath)
                displayMetaDataSubWindow(self.objWeasel, "Metadata for image {}".format(inputPath), dataset)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                dataset = PixelArrayDICOMTools.getDICOMobject(inputPath[0])
                displayMetaDataSubWindow(self.objWeasel, "Metadata for image {}".format(inputPath[0]), dataset)
        except Exception as e:
            print('Error in function #.displayMetadata: ' + str(e))


    def displayImages(self, inputPath, studyID, seriesID):
        """
        Display the PixelArray in "inputPath" in the User Interface.
        """
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                displayImageColour.displayImageSubWindow(self.objWeasel, inputPath, seriesID, studyID)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                if len(inputPath) == 1:
                    displayImageColour.displayImageSubWindow(self.objWeasel, inputPath[0], seriesID, studyID)
                else:
                    displayImageColour.displayMultiImageSubWindow(self.objWeasel, inputPath, studyID, seriesID)
            return
        except Exception as e:
            print('Error in function #.displayImages: ' + str(e))
        
    
    def refreshWeasel(self, new_series_name=None):
        """
        Refresh the user interface screen.
        """
        try:
            if new_series_name:
                treeView.refreshDICOMStudiesTreeView(self.objWeasel, newSeriesName=new_series_name)
            else:
                treeView.refreshDICOMStudiesTreeView(self.objWeasel)
        except Exception as e:
            print('Error in function #.refreshWeasel: ' + str(e))


class GenericDICOMTools:

    def copyDICOM(self, inputPath, series_id=None, series_uid=None, series_name=None, suffix="_Copy"):
        """
        Creates a DICOM copy of all files in "inputPath" (1 or more) into a new series.
        """
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                if (series_id is None) and (series_uid is None):
                    series_id, series_uid = GenericDICOMTools.generateSeriesIDs(self, inputPath)
                elif (series_id is not None) and (series_uid is None):
                    _, series_uid = GenericDICOMTools.generateSeriesIDs(self, inputPath, seriesNumber=series_id)
                elif (series_id is None) and (series_uid is not None):
                    series_id = int(str(readDICOM_Image.getDicomDataset(inputPath).SeriesNumber) + str(random.randint(0, 9999)))
                newDataset = readDICOM_Image.getDicomDataset(inputPath)
                derivedPath = saveDICOM_Image.returnFilePath(inputPath, suffix)
                saveDICOM_Image.saveDicomToFile(newDataset, output_path=derivedPath)
                # The next lines perform an overwrite operation over the copied images
                instance_uid = saveDICOM_Image.generateUIDs(newDataset, seriesNumber=series_id)[2]
                saveDICOM_Image.overwriteDicomFileTag(derivedPath, "SOPInstanceUID", instance_uid)
                saveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesInstanceUID", series_uid)
                saveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesNumber", series_id)
                if series_name:
                    saveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesDescription", series_name)
                else:
                    if hasattr(newDataset, "SeriesDescription"):
                        saveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesDescription", str(newDataset.SeriesDescription + suffix))
                    elif hasattr(newDataset, "SequenceName"):
                        saveDICOM_Image.overwriteDicomFileTag(derivedPath, "SequenceName", str(newDataset.SequenceName + suffix))
                    elif hasattr(newDataset, "ProtocolName"):
                        saveDICOM_Image.overwriteDicomFileTag(derivedPath, "ProtocolName", str(newDataset.ProtocolName + suffix))
                newSeriesID = interfaceDICOMXMLFile.insertNewImageInXMLFile(self, inputPath,
                                             derivedPath, suffix)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                if (series_id is None) and (series_uid is None):
                    series_id, series_uid = GenericDICOMTools.generateSeriesIDs(self, inputPath)
                elif (series_id is not None) and (series_uid is None):
                    _, series_uid = GenericDICOMTools.generateSeriesIDs(self, inputPath, seriesNumber=series_id)
                elif (series_id is None) and (series_uid is not None):
                    series_id = int(str(readDICOM_Image.getDicomDataset(inputPath[0]).SeriesNumber) + str(random.randint(0, 9999)))
                derivedPath = []
                for path in inputPath:
                    newDataset = readDICOM_Image.getDicomDataset(path)
                    newFilePath = saveDICOM_Image.returnFilePath(path, suffix)
                    saveDICOM_Image.saveDicomToFile(newDataset, output_path=newFilePath)
                    derivedPath.append(newFilePath)
                    # The next lines perform an overwrite operation over the copied images
                    instance_uid = saveDICOM_Image.generateUIDs(newDataset, seriesNumber=series_id)[2]
                    saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SOPInstanceUID", instance_uid)
                    saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesInstanceUID", series_uid)
                    saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesNumber", series_id)
                    if series_name:
                        saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", series_name)
                    else:
                        if hasattr(newDataset, "SeriesDescription"):
                            saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", str(newDataset.SeriesDescription + suffix))
                        elif hasattr(newDataset, "SequenceName"):
                            saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SequenceName", str(newDataset.SequenceName + suffix))
                        elif hasattr(newDataset, "ProtocolName"):
                            saveDICOM_Image.overwriteDicomFileTag(newFilePath, "ProtocolName", str(newDataset.ProtocolName + suffix))
                newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self,
                                inputPath, derivedPath, suffix)
            return derivedPath, newSeriesID
        except Exception as e:
            print('Error in function #.copyDICOM: ' + str(e))


    def deleteDICOM(self, inputPath):
        """
        This functions remove all files in inputhPath and updates the XML file accordingly.
        """
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
                    if displayWindow.windowTitle().split(" - ")[-1] in map(os.path.basename, inputPath):
                        displayWindow.close()
        except Exception as e:
            print('Error in function #.deleteDICOM: ' + str(e))


    def mergeDicomIntoOneSeries(self, imagePathList, series_uid=None, series_id=None, series_name="New Series", suffix="_Merged", overwrite=False):
        """
        Merges all DICOM files in "imagePathList" into 1 series.
        It creates a copy if "overwrite=False" (default).
        """
        try:
            if os.path.exists(imagePathList[0]):
                if (series_id is None) and (series_uid is None):
                    series_id, series_uid = GenericDICOMTools.generateSeriesIDs(self, imagePathList)
                elif (series_id is not None) and (series_uid is None):
                    _, series_uid = GenericDICOMTools.generateSeriesIDs(self, imagePathList, seriesNumber=series_id)
                elif (series_id is None) and (series_uid is not None):
                    series_id = int(str(readDICOM_Image.getDicomDataset(imagePathList[0]).SeriesNumber) + str(random.randint(0, 9999)))
            newImagePathList = []
            if overwrite:
                for path in imagePathList:
                    saveDICOM_Image.overwriteDicomFileTag(path, "SeriesInstanceUID", series_uid)
                    saveDICOM_Image.overwriteDicomFileTag(path, "SeriesNumber", series_id)
                    dataset = readDICOM_Image.getDicomDataset(path)
                    if hasattr(dataset, "SeriesDescription"):
                        saveDICOM_Image.overwriteDicomFileTag(path, "SeriesDescription", series_name + suffix)
                    elif hasattr(dataset, "SequenceName"):
                        saveDICOM_Image.overwriteDicomFileTag(path, "SequenceName", series_name + suffix)
                    elif hasattr(dataset, "ProtocolName"):
                        saveDICOM_Image.overwriteDicomFileTag(path, "ProtocolName", series_name + suffix)
                newImagePathList = imagePathList
                newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self,
                                imagePathList, newImagePathList, suffix)
                interfaceDICOMXMLFile.removeMultipleImagesFromXMLFile(self, imagePathList)     
            else:
                for path in imagePathList:
                    newDataset = readDICOM_Image.getDicomDataset(path)
                    newFilePath = saveDICOM_Image.returnFilePath(path, suffix)
                    saveDICOM_Image.saveDicomToFile(newDataset, output_path=newFilePath)
                    # The next lines perform an overwrite operation over the copied images
                    instance_uid = saveDICOM_Image.generateUIDs(newDataset, seriesNumber=series_id)[2]
                    saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SOPInstanceUID", instance_uid)
                    saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesInstanceUID", series_uid)
                    saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesNumber", series_id)
                    if hasattr(newDataset, "SeriesDescription"):
                        saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", series_name + suffix)
                    elif hasattr(newDataset, "SequenceName"):
                        saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SequenceName", series_name + suffix)
                    elif hasattr(newDataset, "ProtocolName"):
                        saveDICOM_Image.overwriteDicomFileTag(newFilePath, "ProtocolName", series_name + suffix)
                    newImagePathList.append(newFilePath)
                newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self,
                                imagePathList, newImagePathList, suffix)
            return newImagePathList
        except Exception as e:
            print('Error in #.mergeDicomIntoOneSeries: ' + str(e))


    def generateSeriesIDs(self, inputPath, seriesNumber=None):
        """
        This function generates and returns a SeriesUID and an InstanceUID.
        The SeriesUID is generated based on the StudyUID and on seriesNumber (if provided)
        The InstanceUID is generated based on SeriesUID.
        """
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                dataset = PixelArrayDICOMTools.getDICOMobject(inputPath)
                if seriesNumber is None:
                    #seriesNumber = treeView.getSeriesNumberAfterLast(self, inputPath)
                    (subjectID, studyID, seriesID) = treeView.getPathParentNode(self, inputPath)
                    seriesNumber = str(int(self.objXMLReader.getStudy(studyID)[-1].attrib['id'].split('_')[0]) + 1)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                dataset = PixelArrayDICOMTools.getDICOMobject(inputPath[0])
                if seriesNumber is None:
                    #seriesNumber = treeView.getSeriesNumberAfterLast(self, inputPath[0])
                    (subjectID, studyID, seriesID) = treeView.getPathParentNode(self, inputPath[0])
                    seriesNumber = str(int(self.objXMLReader.getStudy(studyID)[-1].attrib['id'].split('_')[0]) + 1)
            ids = saveDICOM_Image.generateUIDs(dataset, seriesNumber=seriesNumber)
            seriesID = ids[0]
            seriesUID = ids[1]
            return seriesID, seriesUID
        except Exception as e:
            print('Error in function #.generateUIDs: ' + str(e))


    @staticmethod
    def editDICOMTag(inputPath, dicomTag, newValue):
        """
        Overwrites all "dicomTag" of the DICOM files in "inputPath"
        with "newValue".
        """
        # CONSIDER THE CASES WHERE SERIES NUMBER, NAME AND UID ARE CHANGED - UPDATE XML
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                saveDICOM_Image.overwriteDicomFileTag(inputPath, dicomTag, newValue)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                for path in inputPath:
                    saveDICOM_Image.overwriteDicomFileTag(path, dicomTag, newValue)
        except Exception as e:
            print('Error in function #.editDICOMTag: ' + str(e))


    @staticmethod
    def sortBySliceLocation(inputPath):
        """
        Sorts list of paths by SliceLocation and returns the sorted list of paths
        and the list of slice locations per file path.
        """
        try:
            imagePathListSorted, sliceListSorted, numberSlices, indecesSorted = readDICOM_Image.sortSequenceByTag(inputPath, "SliceLocation")
            return imagePathListSorted, sliceListSorted
        except Exception as e:
            print('Error in function #.sortBySliceLocation: ' + str(e))


    @staticmethod
    def sortByEchoTime(inputPath):
        """
        Sorts list of paths by EchoTime and returns the sorted list of paths
        and the list of echo times per file path.
        """
        try:
            imagePathListSorted, echoListSorted, numberEchoes, indicesSorted = readDICOM_Image.sortSequenceByTag(inputPath, "EchoTime")
            return imagePathListSorted, echoListSorted
        except Exception as e:
            print('Error in function #.sortByEchoTime: ' + str(e))


    @staticmethod
    def sortByTimePoint(inputPath):
        """
        Sorts list of paths by AcquisitionNumber and returns the sorted list of paths
        and the list of time points per file path.
        """
        try:
            imagePathListSorted, timePointsListSorted, numberTimePoints, indicesSorted = readDICOM_Image.sortSequenceByTag(inputPath, "AcquisitionNumber")
            return imagePathListSorted, timePointsListSorted
        except Exception as e:
            print('Error in function #.sortByEchoTime: ' + str(e))
        

class PixelArrayDICOMTools:
    
    @staticmethod
    def getPixelArrayFromDICOM(inputPath):
        """
        Returns the PixelArray of the DICOM file(s) in "inputPath".
        """
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                pixelArray = readDICOM_Image.returnPixelArray(inputPath)
                return np.squeeze(pixelArray)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                pixelArray = readDICOM_Image.returnSeriesPixelArray(inputPath)
                return np.squeeze(pixelArray)
            else:
                return None
        except Exception as e:
            print('Error in function #.getPixelArrayFromDICOM: ' + str(e))


    @staticmethod
    def getDICOMobject(inputPath):
        """
        Returns the DICOM object (or list of DICOM objects) of the file(s) in "inputPath".
        """
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                dataset = readDICOM_Image.getDicomDataset(inputPath)
                return dataset
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                dataset = readDICOM_Image.getSeriesDicomDataset(inputPath)
                return dataset
            else:
                return None
        except Exception as e:
            print('Error in function #.getDICOMobject: ' + str(e))


    def writeNewPixelArray(self, pixelArray, inputPath, suffix, series_id=None, series_uid=None, series_name=None):
        """
        Saves the "pixelArray" into new DICOM files with a new series, based
        on the "inputPath" and on the "suffix".
        """
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                numImages = 1
                derivedImageList = [pixelArray]
                derivedImageFilePath = saveDICOM_Image.returnFilePath(inputPath, suffix)
                derivedImagePathList = [derivedImageFilePath]

            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                if hasattr(readDICOM_Image.getDicomDataset(inputPath[0]), 'PerFrameFunctionalGroupsSequence'):
                    # If it's Enhanced MRI
                    numImages = 1
                    derivedImageList = [pixelArray]
                    derivedImageFilePath = saveDICOM_Image.returnFilePath(inputPath[0], suffix)
                    derivedImagePathList = [derivedImageFilePath]
                else:
                    # Iterate through list of images (slices) and save the resulting Map for each DICOM image
                    numImages = (1 if len(np.shape(pixelArray)) < 3 else np.shape(pixelArray)[0])
                    derivedImagePathList = []
                    derivedImageList = []
                    for index in range(numImages):
                        derivedImageFilePath = saveDICOM_Image.returnFilePath(inputPath[index], suffix)
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
                saveDICOM_Image.saveNewSingleDicomImage(derivedImagePathList[0], (''.join(inputPath)), derivedImageList[0], suffix, series_id=series_id, series_uid=series_uid, series_name=series_name, list_refs_path=[(''.join(inputPath))])
                # Record derived image in XML file
                interfaceDICOMXMLFile.insertNewImageInXMLFile(self, (''.join(inputPath)), derivedImagePathList[0], suffix, newSeriesName=series_name)
            else:
                saveDICOM_Image.saveDicomNewSeries(derivedImagePathList, inputPath, derivedImageList, suffix, series_id=series_id, series_uid=series_uid, series_name=series_name, list_refs_path=[inputPath])
                # Insert new series into the DICOM XML file
                interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self, inputPath, derivedImagePathList, suffix, newSeriesName=series_name)            
                
            return derivedImagePathList

        except Exception as e:
            print('Error in function #.writePixelArrayToDicom: ' + str(e))


    @staticmethod
    def overwritePixelArray(pixelArray, inputPath):
        """
        Overwrites the DICOM files in the "pixelArray" into new DICOM files with a new series, based
        on the "inputPath" and on the "suffix".
        """
        try:
            if isinstance(inputPath, list) and len(inputPath) > 1:
                datasetList = readDICOM_Image.getSeriesDicomDataset(inputPath)
                for index, dataset in enumerate(datasetList):
                    modifiedDataset = saveDICOM_Image.createNewPixelArray(pixelArray[index], dataset)
                    saveDICOM_Image.saveDicomToFile(modifiedDataset, output_path=inputPath[index])
            else:
                dataset = readDICOM_Image.getDicomDataset(inputPath)
                modifiedDataset = saveDICOM_Image.createNewPixelArray(pixelArray, dataset)
                saveDICOM_Image.saveDicomToFile(modifiedDataset, output_path=inputPath)
        except Exception as e:
            print('Error in #.overwritePixelArray: ' + str(e))


class Project:
    def __init__(self, objWeasel):
        root = objWeasel.treeView.invisibleRootItem()
        children = []
        for i in range(root.childCount()):
            subjectItem = root.child(i)
            children.append(Subject.fromTreeView(objWeasel, subjectItem))
        self.children = children
        self.numberChildren = len(self.children)


class Subject:
    def __init__(self, objWeasel, subjectID, children=None):
        self.objWeasel = objWeasel
        self.subjectID = subjectID
        if children is None:
            root = objWeasel.treeView.invisibleRootItem()
            children = []
            for i in range(root.childCount()):
                if root.child(i).text(1) == 'Subject -' + str(self.subjectID):
                    subjectItem = root.child(i)
                    for j in range(subjectItem.childCount()):
                        studyItem = subjectItem.child(j)
                        children.append(Study.fromTreeView(objWeasel, studyItem))
            self.children = children
        else:
            self.children = children
        self.numberChildren = len(self.children)
        
    @classmethod
    def fromTreeView(cls, objWeasel, subjectItem):
        subjectID = subjectItem.text(1).replace('Subject -', '').strip()
        children = []
        for i in range(subjectItem.childCount()):
            studyItem = subjectItem.child(i)
            children.append(Study.fromTreeView(objWeasel, studyItem))
        return cls(objWeasel, subjectID, children=children)
    
    def new(self, subjectID=None):
        if subjectID is None:
            subjectID = self.subjectID + "_Copy"
        return Subject(self.objWeasel, subjectID, children=[])

    #def copy():

    def delete(self):
        for studies in self.children:
            studies.delete()
        self.children = []
        self.numberChildren = 0
        self.subjectID = ''
        # Delete the instance, such as del self???

    def add(self, Study):
        self.children.append(Study)
        self.numberChildren = len(self.children)

    def remove(self, allStudies=False, Study=None):
        if allStudies == True:
            self.children = []
            self.numberChildren = 0
        elif Series is not None:
            self.children.remove(Study)
            self.numberChildren = len(self.children)


class Study:
    def __init__(self, objWeasel, subjectID, studyID, children=None):
        self.objWeasel = objWeasel
        self.subjectID = subjectID
        self.studyID = studyID
        if children is None:
            root = objWeasel.treeView.invisibleRootItem()
            children = []
            for i in range(root.childCount()):
                if root.child(i).text(1) == 'Subject -' + str(self.subjectID):
                    subjectItem = root.child(i)
                    for j in range(subjectItem.childCount()):
                        if subjectItem.child(j).text(1) == 'Study -' + str(self.studyID):
                            studyItem = subjectItem.child(j)
                            for k in range(studyItem.childCount()):
                                seriesItem = studyItem.child(k)
                                children.append(Series.fromTreeView(objWeasel, seriesItem))
            self.children = children
        else:
            self.children = children
        self.numberChildren = len(self.children)
        
    @classmethod
    def fromTreeView(cls, objWeasel, studyItem):
        subjectID = studyItem.parent().text(1).replace('Subject -', '').strip()
        studyID = studyItem.text(1).replace('Study -', '').strip()
        children = []
        for i in range(studyItem.childCount()):
            seriesItem = studyItem.child(i)
            children.append(Series.fromTreeView(objWeasel, seriesItem))
        return cls(objWeasel, subjectID, studyID, children=children)

    def new(self):
        studyID = time.strftime('%Y%m%d_%H%M%S')
        #studyID = self.studyID + "_Copy"
        return Study(self.objWeasel, self.subjectID, studyID, children=[])

    def copy(self, newStudy=False, newSeries=True):
        if newStudy == True:
            studyID = time.strftime('%Y%m%d_%H%M%S')
            #studyID = self.studyID + "_Copy"
            newStudyInstance = self.new(studyID=studyID)
            for series in self.children:
                copiedSeries = series.copy()
                newStudyInstance.add(copiedSeries)
                # This needs a function to add new study to XML
        # Second option will mantain the study and duplicate the series
        else:
            for series in self.children:
                copiedSeries = series.copy(newSeries=newSeries)

    def delete(self):
        for series in self.children:
            series.delete()
        self.children = []
        self.numberChildren = 0
        self.subjectID = self.studyID = ''
        # Delete the instance, such as del self???

    def add(self, Series):
        self.children.append(Series)
        self.numberChildren = len(self.children)
    
    def remove(self, allSeries=False, Series=None):
        if allSeries == True:
            self.children = []
            self.numberChildren = 0
        elif Series is not None:
            self.children.remove(Series)
            self.numberChildren = len(self.children)

    @property
    def Dimensions(self):
        return [np.shape(series.PixelArray) for series in self.children]


class Series:
    __slots__ = ('objWeasel', 'subjectID', 'studyID', 'seriesID', 'seriesUID', 'images', 'children',
                  'numberChildren', 'suffix', 'referencePathsList' ,'indices')
    def __init__(self, objWeasel, subjectID, studyID, seriesID, listPaths=None, children=None, seriesUID=None, suffix=None):
        self.objWeasel = objWeasel
        self.subjectID = subjectID
        self.studyID = studyID
        self.seriesID = seriesID
        self.images = [] if listPaths is None else listPaths
        if children is None:
            root = objWeasel.treeView.invisibleRootItem()
            children = []
            for i in range(root.childCount()):
                if root.child(i).text(1) == 'Subject -' + str(self.subjectID):
                    subjectItem = root.child(i)
                    for j in range(subjectItem.childCount()):
                        if subjectItem.child(j).text(1) == 'Study -' + str(self.studyID):
                            studyItem = subjectItem.child(j)
                            for k in range(studyItem.childCount()):
                                if studyItem.child(k).text(1) == 'Series -' + str(self.seriesID):
                                    seriesItem = studyItem.child(k)
                                    for n in range(seriesItem.childCount()):
                                        imageItem = seriesItem.child(n)
                                        children.append(Image.fromTreeView(objWeasel, imageItem))
            self.children = children
        else:
            self.children = children
        self.numberChildren = len(self.children)
        self.seriesUID = self.SeriesUID if seriesUID is None else seriesUID
        self.suffix = '' if suffix is None else suffix
        self.referencePathsList = []
        # This is to deal with Enhanced MRI
        if self.PydicomList and len(self.images) == 1:
            self.indices = list(np.arange(len(self.PydicomList[0].PerFrameFunctionalGroupsSequence))) if hasattr(self.PydicomList[0], 'PerFrameFunctionalGroupsSequence') else []
        else:
            self.indices = []

    @classmethod
    def fromTreeView(cls, objWeasel, seriesItem):
        subjectID = seriesItem.parent().parent().text(1).replace('Subject -', '').strip()
        studyID = seriesItem.parent().text(1).replace('Study -', '').strip()
        seriesID = seriesItem.text(1).replace('Series -', '').strip()
        images = []
        children = []
        for i in range(seriesItem.childCount()):
            imageItem = seriesItem.child(i)
            images.append(imageItem.text(4))
            children.append(Image.fromTreeView(objWeasel, imageItem))
        return cls(objWeasel, subjectID, studyID, seriesID, listPaths=images, children=children)
    
    def new(self, suffix=None, series_id=None, series_name=None, series_uid=None):
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
    
    def copy(self, newSeries=True, series_id=None, series_name=None, series_uid=None):
        if newSeries == True:
            #series_id = None
            #series_name = None
            #series_uid = None
            newPathsList, newSeriesID = GenericDICOMTools.copyDICOM(self.objWeasel, self.images, series_id=series_id, series_uid=series_uid, series_name=series_name, suffix="_Copy")
            return Series(self.objWeasel, self.subjectID, self.studyID, newSeriesID, listPaths=newPathsList, suffix="_Copy")
        else:
            series_id = self.seriesID.split('_', 1)[0]
            series_name = self.seriesID.split('_', 1)[1]
            series_uid = self.seriesUID
            suffix = self.suffix
            newPathsList, _ = GenericDICOMTools.copyDICOM(self.objWeasel, self.images, series_id=series_id, series_uid=series_uid, series_name=series_name, suffix=suffix)
            for newCopiedImagePath in newPathsList:
                newImage = Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, newCopiedImagePath)
                self.add(newImage)

    def delete(self):
        GenericDICOMTools.deleteDICOM(self.objWeasel, self.images)
        self.images = self.referencePathsList = []
        self.children = self.indices = []
        self.numberChildren = 0
        self.subjectID = self.studyID = self.seriesID = self.seriesUID = ''
        # Delete the instance, such as del self???

    def add(self, Image):
        self.images.append(Image.path)
        self.children.append(Image)
        self.numberChildren = len(self.children)

    def remove(self, allImages=False, Image=None):
        if allImages == True:
            self.images = []
            self.children = []
            self.numberChildren = 0
        elif Image is not None:
            self.images.remove(Image.path)
            self.children.remove(Image)
            self.numberChildren = len(self.children)

    def write(self, pixelArray):
        if self.images:
            PixelArrayDICOMTools.overwritePixelArray(pixelArray, self.images)
        else:
            series_id = self.seriesID.split('_', 1)[0]
            series_name = self.seriesID.split('_', 1)[1]
            inputReference = self.referencePathsList[0] if len(self.referencePathsList)==1 else self.referencePathsList
            outputPath = PixelArrayDICOMTools.writeNewPixelArray(self.objWeasel, pixelArray, inputReference, self.suffix, series_id=series_id, series_name=series_name, series_uid=self.seriesUID)
            self.images = outputPath
    
    def read(self):
        return self.PydicomList

    def save(self, PydicomList):
        for index, dataset in enumerate(PydicomList):
            saveDICOM_Image.saveDicomToFile(dataset, output_path=self.images[index])

    @staticmethod
    def merge(listSeries, series_id=None, series_name='NewSeries', series_uid=None, suffix='_Merged', overwrite=False):
        outputSeries = listSeries[0].new(suffix=suffix, series_id=series_id, series_name=series_name, series_uid=series_uid)
        pathsList = [image for series in listSeries for image in series.images]
        outputPathList = GenericDICOMTools.mergeDicomIntoOneSeries(outputSeries.objWeasel, pathsList, series_uid=series_uid, series_id=series_id, series_name=series_name, suffix=suffix, overwrite=overwrite)
        #UserInterfaceTools(listSeries[0].objWeasel).refreshWeasel(new_series_name=listSeries[0].seriesID)
        outputSeries.images = outputPathList
        outputSeries.referencePathsList = outputPathList
        return outputSeries
    
    def sort(self, tagDescription, *argv):
        if self.Item(tagDescription) or self.Tag(tagDescription):
            imagePathList, _, _, indicesSorted = readDICOM_Image.sortSequenceByTag(self.images, tagDescription)
            self.images = imagePathList
            if self.Multiframe: self.indices = sorted(set(indicesSorted) & set(self.indices), key=indicesSorted.index)
        for tag in argv:
            if self.Item(tag) or self.Tag(tag):
                imagePathList, _, _, indicesSorted = readDICOM_Image.sortSequenceByTag(self.images, tag)
                self.images = imagePathList
                if self.Multiframe: self.indices = sorted(set(indicesSorted) & set(self.indices), key=indicesSorted.index)

    def display(self):
        UserInterfaceTools(self.objWeasel).displayImages(self.images, self.studyID, self.seriesID)

    def Metadata(self):
        UserInterfaceTools(self.objWeasel).displayMetadata(self.images)

    @property
    def SeriesUID(self):
        if not self.images:
            self.seriesUID = None
        elif os.path.exists(self.images[0]):
            self.seriesUID = readDICOM_Image.getImageTagValue(self.images[0], 'SeriesInstanceUID')
        else:
            self.seriesUID = None
        return self.seriesUID

    @property
    def Magnitude(self):
        dicomList = self.PydicomList
        magnitudeSeries = Series(self.objWeasel, self.subjectID, self.studyID, self.seriesID, listPaths=self.images)
        magnitudeSeries.remove(allImages=True)
        magnitudeSeries.referencePathsList = self.images
        for index in range(len(self.images)):
            flagMagnitude, _, _, _, _ = readDICOM_Image.checkImageType(dicomList[index])
            if isinstance(flagMagnitude, list) and flagMagnitude:
                if len(flagMagnitude) > 1 and len(self.images) == 1:
                    magnitudeSeries.indices = flagMagnitude
                magnitudeSeries.add(Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.images[index]))
            elif flagMagnitude == True:
                magnitudeSeries.add(Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.images[index]))
        return magnitudeSeries

    @property
    def Phase(self):
        dicomList = self.PydicomList
        phaseSeries = Series(self.objWeasel, self.subjectID, self.studyID, self.seriesID, listPaths=self.images)
        phaseSeries.remove(allImages=True)
        phaseSeries.referencePathsList = self.images
        for index in range(len(self.images)):
            _, flagPhase, _, _, _ = readDICOM_Image.checkImageType(dicomList[index])
            if isinstance(flagPhase, list) and flagPhase:
                if len(flagPhase) > 1 and len(self.images) == 1:
                    phaseSeries.indices = flagPhase
                phaseSeries.add(Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.images[index]))
            elif flagPhase == True:
                phaseSeries.add(Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.images[index]))
        return phaseSeries

    @property
    def Real(self):
        dicomList = self.PydicomList
        realSeries = Series(self.objWeasel, self.subjectID, self.studyID, self.seriesID, listPaths=self.images)
        realSeries.remove(allImages=True)
        realSeries.referencePathsList = self.images
        for index in range(len(self.images)):
            _, _, flagReal, _, _ = readDICOM_Image.checkImageType(dicomList[index])
            if isinstance(flagReal, list) and flagReal:
                if len(flagReal) > 1 and len(self.images) == 1:
                    realSeries.indices = flagReal
                realSeries.add(Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.images[index]))
            elif flagReal:
                realSeries.add(Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.images[index]))
        return realSeries 

    @property
    def Imaginary(self):
        dicomList = self.PydicomList
        imaginarySeries = Series(self.objWeasel, self.subjectID, self.studyID, self.seriesID, listPaths=self.images)
        imaginarySeries.remove(allImages=True)
        imaginarySeries.referencePathsList = self.images
        for index in range(len(self.images)):
            _, _, _, flagImaginary, _ = readDICOM_Image.checkImageType(dicomList[index])
            if isinstance(flagImaginary, list) and flagImaginary:
                if len(flagImaginary) > 1 and len(self.images) == 1:
                    imaginarySeries.indices = flagImaginary
                imaginarySeries.add(Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.images[index]))
            elif flagImaginary:
                imaginarySeries.add(Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.images[index]))
        return imaginarySeries 

    @property
    def PixelArray(self, ROI=None):
        pixelArray = PixelArrayDICOMTools.getPixelArrayFromDICOM(self.images)
        if self.Multiframe:    
            tempArray = []
            for index in self.indices:
                tempArray.append(pixelArray[index, ...])
            pixelArray = np.array(tempArray)
            del tempArray
        if isinstance(ROI, Series):
            mask = np.zeros(np.shape(pixelArray))
            coords = ROI.ROIindices
            mask[tuple(zip(*coords))] = list(np.ones(len(coords)).flatten())
            #pixelArray = pixelArray * mask
            pixelArray = np.extract(mask.astype(bool), pixelArray)
        elif ROI == None:
            pass
        else:
            warnings.warn("The input argument ROI should be a Series instance.") 
        return pixelArray

    @property
    def ListAffines(self):
        return [readDICOM_Image.returnAffineArray(image) for image in self.images]
    
    @property
    def ROIindices(self):
        tempImage = self.PixelArray
        tempImage[tempImage != 0] = 1
        return np.transpose(np.where(tempImage == 1))

    @property
    def Dimensions(self):
        return np.shape(self.PixelArray)

    @property
    def Rows(self):
        return self.Item("Rows")

    @property
    def Columns(self):
        return self.Item("Columns")

    @property
    def NumberOfSlices(self):
        numSlices = 0
        if self.Multiframe:
            numSlices = int(self.Item("NumberOfFrames"))
        else:
            numSlices = len(np.unique(self.SliceLocations))
        return numSlices

    @property
    def SliceLocations(self):
        slices = []
        if self.Multiframe:
            #slices = self.indices
            slices = self.Item("PerFrameFunctionalGroupsSequence.FrameContentSequence.InStackPositionNumber")
        else:
            slices = self.Item("SliceLocation")
        return slices
    
    @property
    def EchoTimes(self):
        echoList = []
        #if not self.Multiframe:
            #echoList = self.Item("EchoTime")
        #else:
            #for dataset in self.PydicomList:
                #for index in self.indices:
                    #echoList.append(dataset.PerFrameFunctionalGroupsSequence[index].MREchoSequence[0].EffectiveEchoTime)
        if self.Item("PerFrameFunctionalGroupsSequence.MREchoSequence.EffectiveEchoTime"):
            echoList = self.Item("PerFrameFunctionalGroupsSequence.MREchoSequence.EffectiveEchoTime")
        elif self.Item("EchoTime"):
            echoList = self.Item("EchoTime")
        return echoList

    @property
    def InversionTimes(self):
        inversionList = []
        #if not self.Multiframe:
        if self.Item("InversionTime"):
            inversionList = self.Item("InversionTime")
        elif self.Item(0x20051572):
            inversionList = self.Item(0x20051572)
        else:
            inversionList = []
        #else:
            #inversionList = self.Item("InversionTime")
            #for dataset in self.PydicomList:
                #for index in self.indices:
                    #inversionList.append(dataset.PerFrameFunctionalGroupsSequence[index].MREchoSequence[0].EffectiveInversionTime) # InversionTime
        return inversionList

    def Item(self, tagDescription, newValue=None):
        if self.images:
            if newValue:
                GenericDICOMTools.editDICOMTag(self.images, tagDescription, newValue)
                if (tagDescription == 'SeriesDescription') or (tagDescription == 'SequenceName') or (tagDescription == 'ProtocolName'):
                    interfaceDICOMXMLFile.renameSeriesinXMLFile(self.objWeasel, self.images, series_name=newValue)
                elif tagDescription == 'SeriesNumber':
                    interfaceDICOMXMLFile.renameSeriesinXMLFile(self.objWeasel, self.images, series_id=newValue)
            itemList, _ = readDICOM_Image.getSeriesTagValues(self.images, tagDescription)
            if self.Multiframe: 
                tempList = [itemList[index] for index in self.indices]
                itemList = tempList
                del tempList
        else:
            itemList = []
        return itemList

    def Tag(self, tag, newValue=None):
        try:
            hexTag = '0x' + tag.split(',')[0] + tag.split(',')[1]
        except:
            # Print message about how to provide tag
            return []
        if self.images:
            if newValue:
                GenericDICOMTools.editDICOMTag(self.images, literal_eval(hexTag), newValue)
            itemList, _ = readDICOM_Image.getSeriesTagValues(self.images, literal_eval(hexTag))
            if self.Multiframe: 
                tempList = [itemList[index] for index in self.indices]
                itemList = tempList
                del tempList
        else:
            itemList = []
        return itemList
    
    @property
    def PydicomList(self):
        if self.images:
            return PixelArrayDICOMTools.getDICOMobject(self.images)
        else:
            return []
    
    @property
    def Multiframe(self):
        if self.indices:
            return True
        else:
            return False

    def export_as_nifti(self, directory=None, filename=None):
        if directory is None: directory=os.path.dirname(self.images[0])
        if filename is None: filename=self.seriesID
        dicomHeader = nib.nifti1.Nifti1DicomExtension(2, self.PydicomList[0])
        niftiObj = nib.Nifti1Image(np.transpose(self.PixelArray), affine=self.ListAffines[0])
        niftiObj.header.extensions.append(dicomHeader)
        nib.save(niftiObj, directory + '/' + filename + '.nii.gz')


class Image:
    __slots__ = ('objWeasel', 'subjectID', 'studyID', 'seriesID', 'path', 'seriesUID',
                 'suffix', 'referencePath')
    def __init__(self, objWeasel, subjectID, studyID, seriesID, path, suffix=None):
        self.objWeasel = objWeasel
        self.subjectID = subjectID
        self.studyID = studyID
        self.seriesID = seriesID
        self.path = path
        self.seriesUID = self.SeriesUID
        self.suffix = '' if suffix is None else suffix
        self.referencePath = ''

    @classmethod
    def fromTreeView(cls, objWeasel, imageItem):
        subjectID = imageItem.parent().parent().parent().text(1).replace('Subject -', '').strip()
        studyID = imageItem.parent().parent().text(1).replace('Study -', '').strip()
        seriesID = imageItem.parent().text(1).replace('Series -', '').strip()
        path = imageItem.text(4)
        return cls(objWeasel, subjectID, studyID, seriesID, path)
    
    @staticmethod
    def newSeriesFrom(listImages, suffix='_Copy', series_id=None, series_name=None, series_uid=None):
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

    def new(self, suffix='_Copy', series=None):
        if series is None:
            newImage = Image(self.objWeasel, self.subjectID, self.studyID, self.seriesID, '', suffix=suffix)
        else:
            newImage = Image(series.objWeasel, series.subjectID, series.studyID, series.seriesID, '', suffix=suffix)
        newImage.referencePath = self.path
        return newImage

    def copy(self, series=None):
        if series is None:
            series_id = self.seriesID.split('_', 1)[0]
            series_name = self.seriesID.split('_', 1)[1]
            series_uid = self.seriesUID
            suffix = self.suffix
        else:
            series_id = series.seriesID.split('_', 1)[0]
            series_name = series.seriesID.split('_', 1)[1]
            series_uid = series.seriesUID
            suffix = series.suffix
        newPath, newSeriesID = GenericDICOMTools.copyDICOM(self.objWeasel, self.path, series_id=series_id, series_uid=series_uid, series_name=series_name, suffix=suffix)
        copiedImage = Image(self.objWeasel, self.subjectID, self.studyID, newSeriesID, newPath)
        if series: series.add(copiedImage)
        return copiedImage

    def delete(self):
        GenericDICOMTools.deleteDICOM(self.objWeasel, self.path)
        self.path = []
        self.referencePath = []
        self.subjectID = self.studyID = self.seriesID = ''
        # Delete the instance, such as del self???

    def write(self, pixelArray, series=None):
        if os.path.exists(self.path):
            PixelArrayDICOMTools.overwritePixelArray(pixelArray, self.path)
        else:
            if series is None:
                series_id = self.seriesID.split('_', 1)[0]
                series_name = self.seriesID.split('_', 1)[1]
                series_uid = self.seriesUID
            else:
                series_id = series.seriesID.split('_', 1)[0]
                series_name = series.seriesID.split('_', 1)[1]
                series_uid = series.seriesUID
            outputPath = PixelArrayDICOMTools.writeNewPixelArray(self.objWeasel, pixelArray, self.referencePath, self.suffix, series_id=series_id, series_name=series_name, series_uid=series_uid)
            self.path = outputPath[0]
            if series: series.add(self)
        
    def read(self):
        return self.PydicomObject

    def save(self, PydicomObject):
        saveDICOM_Image.saveDicomToFile(PydicomObject, output_path=self.path)

    @staticmethod
    def merge(listImages, series_id=None, series_name='NewSeries', series_uid=None, suffix='_Merged', overwrite=False):
        outputSeries = Image.newSeriesFrom(listImages, suffix=suffix, series_id=series_id, series_name=series_name, series_uid=series_uid)    
        outputPathList = GenericDICOMTools.mergeDicomIntoOneSeries(outputSeries.objWeasel, outputSeries.referencePathsList, series_uid=series_uid, series_id=series_id, series_name=series_name, suffix=suffix, overwrite=overwrite)
        #UserInterfaceTools(listImages[0].objWeasel).refreshWeasel(new_series_name=listImages[0].seriesID)
        outputSeries.images = outputPathList
        return outputSeries
    
    def display(self):
        UserInterfaceTools(self.objWeasel).displayImages(self.path, self.studyID, self.seriesID)

    @staticmethod
    def displayListImages(listImages):
        pathsList = [image.path for image in listImages]
        UserInterfaceTools(listImages[0].objWeasel).displayImages(pathsList, listImages[0].studyID, listImages[0].seriesID)

    @property
    def Name(self):
        return treeView.returnImageName(self.objWeasel, self.subjectID, self.studyID, self.seriesID, self.path)

    @property
    def SeriesUID(self):
        if not self.path:
            self.seriesUID = None
        elif os.path.exists(self.path):
            self.seriesUID = readDICOM_Image.getImageTagValue(self.path, 'SeriesInstanceUID')
        else:
            self.seriesUID = None
        return self.seriesUID
    
    def Metadata(self):
        UserInterfaceTools(self.objWeasel).displayMetadata(self.path)

    @property
    def PixelArray(self, ROI=None):
        pixelArray = PixelArrayDICOMTools.getPixelArrayFromDICOM(self.path)
        if isinstance(ROI, Image):
            mask = np.zeros(np.shape(pixelArray))
            coords = ROI.ROIindices
            mask[tuple(zip(*coords))] = list(np.ones(len(coords)).flatten())
            #pixelArray = pixelArray * mask
            pixelArray = np.extract(mask.astype(bool), pixelArray)
        elif ROI == None:
            pass
        else:
            warnings.warn("The input argument ROI should be an Image instance.") 
        return pixelArray
    
    @property
    def ROIindices(self):
        tempImage = self.PixelArray
        tempImage[tempImage != 0] = 1
        return np.transpose(np.where(tempImage == 1))

    @property
    def Affine(self):
        return readDICOM_Image.returnAffineArray(self.path)
        
    @property
    def Dimensions(self):
        return np.shape(self.PixelArray)

    @property
    def Rows(self):
        return self.Item("Rows")

    @property
    def Columns(self):
        return self.Item("Columns")

    def Item(self, tagDescription, newValue=None):
        if self.path:
            if newValue:
                GenericDICOMTools.editDICOMTag(self.path, tagDescription, newValue)
            item = readDICOM_Image.getImageTagValue(self.path, tagDescription)
        else:
            item = []
        return item

    def Tag(self, tag, newValue=None):
        hexTag = '0x' + tag.split(',')[0] + tag.split(',')[1]
        if self.path:
            if newValue:
                GenericDICOMTools.editDICOMTag(self.path, literal_eval(hexTag), newValue)
            item = readDICOM_Image.getImageTagValue(self.path, literal_eval(hexTag))
        else:
            item = []
        return item

    @property
    def PydicomObject(self):
        if self.path:
            return PixelArrayDICOMTools.getDICOMobject(self.path)
        else:
            return []

    def export_as_nifti(self, directory=None, filename=None):
        if directory is None: directory=os.path.dirname(self.path)
        if filename is None: filename=self.seriesID
        dicomHeader = nib.nifti1.Nifti1DicomExtension(2, self.PydicomObject)
        niftiObj = nib.Nifti1Image(np.transpose(self.PixelArray), affine=self.Affine)
        niftiObj.header.extensions.append(dicomHeader)
        nib.save(niftiObj, directory + '/' + filename + '.nii.gz')