import os
import numpy as np
import random
import pydicom
import itertools
from ast import literal_eval # Convert strings to their actual content. Eg. "[a, b]" becomes the actual list [a, b]
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image
import CoreModules.WEASEL.saveDICOM_Image as saveDICOM_Image
import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.DisplayImageColour as displayImageColour
import CoreModules.WEASEL.MessageWindow as messageWindow
import CoreModules.WEASEL.InterfaceDICOMXMLFile as interfaceDICOMXMLFile
import CoreModules.WEASEL.InputDialog as inputDialog
from Developer.MenuItems.ViewMetaData import displayMetaDataSubWindow


def NestedDictValues(dictionary):
    """
    This function gets a list of all the values inside a python dictionary,
    regardless of the number of levels present in the dictionary.
    """
    for value in dictionary.values():
        if isinstance(value, dict):
            yield from NestedDictValues(value)
        else:
            yield value


class UserInterfaceTools:
    """
    This class contains functions that read the items selected in the User Interface
    and return variables that are used in processing pipelines. It also contains functions
    that allow the user to insert inputs and give an update of the pipeline steps through
    message windows. 
    """
    @staticmethod 
    def getCurrentStudy(self):
        """
        Returns the Study ID of the latest item selected in the Treeview.
        """
        return self.selectedStudy
    

    @staticmethod 
    def getCurrentSeries(self):
        """
        Returns the Series ID of the latest item selected in the Treeview.
        """
        return self.selectedSeries
    

    @staticmethod 
    def getCurrentImage(self):
        """
        Returns a string with the path of the latest selected image.
        """
        return self.selectedImagePath


    def getSelectedStudies(self):
        """
        Returns a list with objects of class Study of the items selected in the Treeview.
        """
        studyList = []
        studiesTreeViewList = treeView.returnSelectedStudies(self)
        if studiesTreeViewList == []:
            UserInterfaceTools.showMessageWindow(self, msg="Script didn't run successfully because"
                              " no studies were selected in the Treeview.",
                              title="No Studies Selected")
        else:
            for study in studiesTreeViewList:
                studyList.append(Study.fromTreeView(self, study))
        return studyList


    def getSelectedSeries(self):
        """
        Returns a list with objects of class Series of the items selected in the Treeview.
        """
        seriesList = []
        seriesTreeViewList = treeView.returnSelectedSeries(self)
        if seriesTreeViewList == []:
            UserInterfaceTools.showMessageWindow(self, msg="Script didn't run successfully because"
                              " no series were selected in the Treeview.",
                              title="No Series Selected")
        else:
            for series in seriesTreeViewList:
                seriesList.append(Series.fromTreeView(self, series))
        return seriesList


    def getSelectedImages(self):
        """
        Returns a list with objects of class Image of the items selected in the Treeview.
        """
        imagesList = []
        imagesTreeViewList = treeView.returnSelectedImages(self)
        if imagesTreeViewList == []:
            UserInterfaceTools.showMessageWindow(self, msg="Script didn't run successfully because"
                              " no images were selected in the Treeview.",
                              title="No Images Selected")
        else:
            for images in imagesTreeViewList:
                imagesList.append(Image.fromTreeView(self, images))
        return imagesList
    

    def getCheckedStudies(self):
        """
        Returns a list with objects of class Study of the items checked in the Treeview.
        """
        studyList = []
        studiesTreeViewList = treeView.returnCheckedStudies(self)
        if studiesTreeViewList == []:
            UserInterfaceTools.showMessageWindow(self, msg="Script didn't run successfully because"
                              " no studies were checked in the Treeview.",
                              title="No Studies Checked")
        else:
            for study in studiesTreeViewList:
                studyList.append(Study.fromTreeView(self, study))
        return studyList
    

    def getCheckedSeries(self):
        """
        Returns a list with objects of class Series of the items checked in the Treeview.
        """
        seriesList = []
        seriesTreeViewList = treeView.returnCheckedSeries(self)
        if seriesTreeViewList == []:
            UserInterfaceTools.showMessageWindow(self, msg="Script didn't run successfully because"
                              " no series were checked in the Treeview.",
                              title="No Series Checked")
        else:
            for series in seriesTreeViewList:
                seriesList.append(Series.fromTreeView(self, series))

        return seriesList
    

    def getCheckedImages(self):
        """
        Returns a list with objects of class Image of the items checked in the Treeview.
        """
        imagesList = []
        imagesTreeViewList = treeView.returnCheckedImages(self)
        if imagesTreeViewList == []:
            UserInterfaceTools.showMessageWindow(self, msg="Script didn't run successfully because"
                              " no images were checked in the Treeview.",
                              title="No Images Checked")
        else:
            for images in imagesTreeViewList:
                imagesList.append(Image.fromTreeView(self, images))
        return imagesList


    @staticmethod 
    def getImagesFromSeries(self, studyID=None, seriesID=None):
        """
        Returns a list of strings with the paths of all images in (studyID, seriesID).
        """
        if (studyID is None) or (seriesID is None):
            studyID = UserInterfaceTools.getCurrentStudy(self)
            seriesID = UserInterfaceTools.getCurrentSeries(self)
        return self.objXMLReader.getImagePathList(studyID, seriesID)


    @staticmethod 
    def getSeriesFromImages(self, inputPath):
        """
        Returns a list of strings with the paths of all images in (studyID, seriesID).
        """
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                (subjectID, studyID, seriesID) = treeView.getPathParentNode(self, inputPath)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                (subjectID, studyID, seriesID) = treeView.getPathParentNode(self, inputPath[0])
            return seriesID
        except Exception as e:
            print('Error in function #.getSeriesFromImages: ' + str(e))

    
    def showMessageWindow(self, msg="Please insert message in the function call", title="Message Window Title"):
        """
        Displays a window in the User Interface with the title in "title" and
        with the message in "msg". The 2 strings in the arguments are the input by default.
        """
        messageWindow.displayMessageSubWindow(self, "<H4>" + msg + "</H4>", title)


    def closeMessageWindow(self):
        """
        Closes any message window present in the User Interface.
        """
        messageWindow.hideProgressBar(self)
        messageWindow.closeMessageSubWindow(self)


    def progressBar(self, maxNumber=1, index=0, msg="Iteration Number {}", title="Progress Bar"):
        """
        Updates the ProgressBar to the unit set in "index".
        """
        index += 1
        messageWindow.displayMessageSubWindow(self, ("<H4>" + msg + "</H4>").format(index), title)
        messageWindow.setMsgWindowProgBarMaxValue(self, maxNumber)
        messageWindow.setMsgWindowProgBarValue(self, index)
        return index
    
    
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
                displayMetaDataSubWindow(self, "Metadata for image {}".format(inputPath), dataset)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                dataset = PixelArrayDICOMTools.getDICOMobject(inputPath[0])
                displayMetaDataSubWindow(self, "Metadata for image {}".format(inputPath[0]), dataset)
        except Exception as e:
            print('Error in function #.displayMetadata: ' + str(e))


    def displaySeries(self, seriesTuple):
        try:
            studyID = seriesTuple[1]
            seriesID = seriesTuple[2]
            inputPath = UserInterfaceTools.getImagesFromSeries(self, studyID, seriesID)
            displayImageColour.displayMultiImageSubWindow(self, inputPath, studyID, seriesID)
        except Exception as e:
            print('Error in function #.displaySeries: ' + str(e))


    def displayImage(self, inputPath):
        """
        Display the PixelArray in "inputPath" in the User Interface.
        """
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                (subjectID, studyID, seriesID) = treeView.getPathParentNode(self, inputPath)
                displayImageColour.displayImageSubWindow(self, studyID, seriesID, derivedImagePath=inputPath)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                (subjectID, studyID, seriesID) = treeView.getPathParentNode(self, inputPath[0])
                displayImageColour.displayMultiImageSubWindow(self, inputPath, studyID, seriesID)
            return
        except Exception as e:
            print('Error in function #.displayImage: ' + str(e))
        
    
    def refreshWeasel(self, newSeriesName=None):
        """
        Refresh the user interface screen.
        """
        try:
            if newSeriesName:
                treeView.refreshDICOMStudiesTreeView(self, newSeriesName=newSeriesName)
            else:
                treeView.refreshDICOMStudiesTreeView(self)
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
                    series_id, series_uid = GenericDICOMTools.generateSeriesIDs(inputPath)
                elif (series_id is not None) and (series_uid is None):
                    _, series_uid = GenericDICOMTools.generateSeriesIDs(inputPath, seriesNumber=series_id)
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
                    saveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesDescription", str(newDataset.SeriesDescription + suffix))
                newSeriesID = interfaceDICOMXMLFile.insertNewImageInXMLFile(self, inputPath,
                                             derivedPath, suffix)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                if (series_id is None) and (series_uid is None):
                    series_id, series_uid = GenericDICOMTools.generateSeriesIDs(inputPath)
                elif (series_id is not None) and (series_uid is None):
                    _, series_uid = GenericDICOMTools.generateSeriesIDs(inputPath, seriesNumber=series_id)
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
                        saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", str(newDataset.SeriesDescription + suffix))
                newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self,
                                inputPath, derivedPath, suffix)
            return derivedPath
        except Exception as e:
            print('Error in function #.copyDICOM: ' + str(e))


    def deleteDICOM(self, inputPath):
        """
        A window is prompted asking the user if it wishes to delete all images in "inputPath".
        It performs the file removal upon affirmative answer.
        """
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                os.remove(inputPath)
                interfaceDICOMXMLFile.removeImageFromXMLFile(self, inputPath)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                for path in inputPath:
                    os.remove(path)
                    interfaceDICOMXMLFile.removeMultipleImagesFromXMLFile(self, inputPath)   
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
                    series_id, series_uid = GenericDICOMTools.generateSeriesIDs(imagePathList)
                elif (series_id is not None) and (series_uid is None):
                    _, series_uid = GenericDICOMTools.generateSeriesIDs(imagePathList, seriesNumber=series_id)
                elif (series_id is None) and (series_uid is not None):
                    series_id = int(str(readDICOM_Image.getDicomDataset(imagePathList[0]).SeriesNumber) + str(random.randint(0, 9999)))
            newImagePathList = []
            if overwrite:
                for path in imagePathList:
                    saveDICOM_Image.overwriteDicomFileTag(path, "SeriesInstanceUID", series_uid)
                    saveDICOM_Image.overwriteDicomFileTag(path, "SeriesNumber", series_id)
                    saveDICOM_Image.overwriteDicomFileTag(path, "SeriesDescription", series_name + suffix)
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
                    saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", series_name + suffix)
                    newImagePathList.append(newFilePath)
                # CAN WE UPDATE THE XML FILE WITHOUT THE SUFFIX AND IMAGE PATH LIST???
                newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self,
                                imagePathList, newImagePathList, suffix)
            return newImagePathList
        except Exception as e:
            print('Error in #.mergeDicomIntoOneSeries: ' + str(e))


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
    def generateSeriesIDs(inputPath, seriesNumber=None):
        """
        This function generates and returns a SeriesUID and an InstanceUID.
        The SeriesUID is generated based on the StudyUID and on seriesNumber (if provided)
        The InstanceUID is generated based on SeriesUID.
        """
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                dataset = PixelArrayDICOMTools.getDICOMobject(inputPath)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                dataset = PixelArrayDICOMTools.getDICOMobject(inputPath[0])
            ids = saveDICOM_Image.generateUIDs(dataset, seriesNumber=seriesNumber)
            seriesID = ids[0]
            seriesUID = ids[1]
            return seriesID, seriesUID
        except Exception as e:
            print('Error in function #.generateUIDs: ' + str(e))


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
        

    # @staticmethod
    # def sortByInversionTime(inputPath):


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
                saveDICOM_Image.saveNewSingleDicomImage(derivedImagePathList[0], (''.join(inputPath)), derivedImageList[0], suffix, series_id=series_id, series_uid=series_uid, series_name=series_name, list_refs_path=[(''.join(inputPath))])
                # Record derived image in XML file
                interfaceDICOMXMLFile.insertNewImageInXMLFile(self, inputPath, derivedImagePathList[0], suffix, newSeriesName=series_name)
                # Can return the seriesTuple probably
            else:
                saveDICOM_Image.saveDicomNewSeries(derivedImagePathList, inputPath, derivedImageList, suffix, series_id=series_id, series_uid=series_uid, series_name=series_name, list_refs_path=[inputPath])
                # Insert new series into the DICOM XML file
                # if series_id AND series_name not None
                # DOES IT NEED TO RETURN THE NEW SERIES_ID?
                interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self, inputPath, derivedImagePathList, suffix, newSeriesName=series_name)            
                
            return derivedImagePathList # ALSO RETURN TUPLE SERIES ID HERE??? 

        except Exception as e:
            print('Error in function #.writePixelArrayToDicom: ' + str(e))


    @staticmethod
    def overwritePixelArray(pixelArray, inputPath):
        """
        Overwrites the DICOM files in the "pixelArray" into new DICOM files with a new series, based
        on the "inputPath" and on the "suffix".
        """
        try:
            if isinstance(inputPath, list):
                datasetList = readDICOM_Image.getSeriesDicomDataset(inputPath)
                for index, dataset in enumerate(datasetList):
                    modifiedDataset = saveDICOM_Image.createNewPixelArray(pixelArray, dataset)
                    saveDICOM_Image.saveDicomToFile(modifiedDataset, output_path=inputPath[index])
            else:
                dataset = readDICOM_Image.getDicomDataset(inputPath)
                modifiedDataset = saveDICOM_Image.createNewPixelArray(pixelArray, dataset)
                saveDICOM_Image.saveDicomToFile(modifiedDataset, output_path=inputPath)
            return
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
        self.subjectID = subjectID
        if children is None:
            root = objWeasel.treeView.invisibleRootItem()
            children = []
            for i in range(root.childCount()):
                if root.child(i).text(0) == 'Subject -' + str(self.subjectID):
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
        subjectID = subjectItem.text(0).replace('Subject -', '').strip()
        children = []
        for i in range(subjectItem.childCount()):
            studyItem = subjectItem.child(i)
            children.append(Study.fromTreeView(objWeasel, studyItem))
        return cls(objWeasel, subjectID, children=children)


class Study:
    def __init__(self, objWeasel, subjectID, studyID, children=None):
        self.subjectID = subjectID
        self.studyID = studyID
        if children is None:
            root = objWeasel.treeView.invisibleRootItem()
            children = []
            for i in range(root.childCount()):
                if root.child(i).text(0) == 'Subject -' + str(self.subjectID):
                    subjectItem = root.child(i)
                    for j in range(subjectItem.childCount()):
                        if subjectItem.child(j).text(0) == 'Study -' + str(self.studyID):
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
        subjectID = studyItem.parent().text(0).replace('Subject -', '').strip()
        studyID = studyItem.text(0).replace('Study -', '').strip()
        children = []
        for i in range(studyItem.childCount()):
            seriesItem = studyItem.child(i)
            children.append(Series.fromTreeView(objWeasel, seriesItem))
        return cls(objWeasel, subjectID, studyID, children=children)

    @property
    def Dimensions(self):
        return [np.shape(series.PixelArray) for series in self.children]


class Series:
    def __init__(self, objWeasel, subjectID, studyID, seriesID, listPaths, children=None):
        self.subjectID = subjectID
        self.studyID = studyID
        self.seriesID = seriesID
        self.images = listPaths
        if children is None:
            root = objWeasel.treeView.invisibleRootItem()
            children = []
            for i in range(root.childCount()):
                if root.child(i).text(0) == 'Subject -' + str(self.subjectID):
                    subjectItem = root.child(i)
                    for j in range(subjectItem.childCount()):
                        if subjectItem.child(j).text(0) == 'Study -' + str(self.studyID):
                            studyItem = subjectItem.child(j)
                            for k in range(studyItem.childCount()):
                                if studyItem.child(k).text(0) == 'Series -' + str(self.seriesID):
                                    seriesItem = studyItem.child(k)
                                    for n in range(seriesItem.childCount()):
                                        imageItem = seriesItem.child(n)
                                        children.append(Image.fromTreeView(objWeasel, imageItem))
            self.children = children
        else:
            self.children = children
        self.numberChildren = len(self.children)

    @classmethod
    def fromTreeView(cls, objWeasel, seriesItem):
        subjectID = seriesItem.parent().parent().text(0).replace('Subject -', '').strip()
        studyID = seriesItem.parent().text(0).replace('Study -', '').strip()
        seriesID = seriesItem.text(0).replace('Series -', '').strip()
        images = []
        children = []
        for i in range(seriesItem.childCount()):
            imageItem = seriesItem.child(i)
            images.append(imageItem.text(3))
            children.append(Image.fromTreeView(objWeasel, imageItem))
        return cls(objWeasel, subjectID, studyID, seriesID, images, children=children)
    
    def DisplayImage(self, objWeasel):
        UserInterfaceTools.displayImage(objWeasel, self.images)

    def DisplayMetadata(self, objWeasel):
        UserInterfaceTools.displayMetadata(objWeasel, self.images)

    @property
    def PixelArray(self):
        return PixelArrayDICOMTools.getPixelArrayFromDICOM(self.images)

    @PixelArray.setter
    def PixelArray(self, array):
        self.PixelArray = array
    
    @property
    def Dimensions(self):
        return np.shape(self.PixelArray)

    def Item(self, tagDescription, newValue=None):
        if newValue:
            GenericDICOMTools.editDICOMTag(self.images, tagDescription, newValue)
        itemList, _ = readDICOM_Image.getSeriesTagValues(self.images, tagDescription)
        return itemList

    def Tag(self, tag, newValue=None):
        hexTag = '0x' + tag.split(',')[0] + tag.split(',')[1]
        if newValue:
            GenericDICOMTools.editDICOMTag(self.images, literal_eval(hexTag), newValue)
        itemList, _ = readDICOM_Image.getSeriesTagValues(self.images, literal_eval(hexTag))
        return itemList


class Image:
    def __init__(self, objWeasel, subjectID, studyID, seriesID, listPaths, path):
        self.subjectID = subjectID
        self.studyID = studyID
        self.seriesID = seriesID
        self.images = listPaths
        self.path = path

    @classmethod
    def fromTreeView(cls, objWeasel, imageItem):
        subjectID = imageItem.parent().parent().parent().text(0).replace('Subject -', '').strip()
        studyID = imageItem.parent().parent().text(0).replace('Study -', '').strip()
        seriesID = imageItem.parent().text(0).replace('Series -', '').strip()
        images = [imageItem.parent().child(i).text(3) for i in range(imageItem.parent().childCount())]
        path = imageItem.text(3)
        return cls(objWeasel, subjectID, studyID, seriesID, images, path)
    
    # Same for Series
    #####################
    def createNewSeries(self, ):
    
    def saveToDICOM(self, ):
    ######################

    def DisplayImage(self, objWeasel):
        UserInterfaceTools.displayImage(objWeasel, self.path)

    def DisplayMetadata(self, objWeasel):
        UserInterfaceTools.displayMetadata(objWeasel, self.path)
    
    @property
    def PixelArray(self):
        return PixelArrayDICOMTools.getPixelArrayFromDICOM(self.path)

    @PixelArray.setter
    def PixelArray(self, array):
        self.PixelArray = array
        
    @property
    def Dimensions(self):
        return np.shape(self.PixelArray)

    def Item(self, tagDescription, newValue=None):
        if newValue:
            GenericDICOMTools.editDICOMTag(self.path, tagDescription, newValue)
        item= readDICOM_Image.getImageTagValue(self.path, tagDescription)
        return item

    def Tag(self, tag, newValue=None):
        hexTag = '0x' + tag.split(',')[0] + tag.split(',')[1]
        if newValue:
            GenericDICOMTools.editDICOMTag(self.path, literal_eval(hexTag), newValue)
        item = readDICOM_Image.getImageTagValue(self.path, literal_eval(hexTag))
        return item