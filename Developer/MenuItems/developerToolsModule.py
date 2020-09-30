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


def NestedDictValues(dictionary):
  for value in dictionary.values():
    if isinstance(value, dict):
      yield from NestedDictValues(value)
    else:
      yield value


# GUI
# ===================================================================================================

def getStudyID(self):
    return self.selectedStudy


def getSeriesID(self):
    return self.selectedSeries


def getImagePath(self):
    return self.selectedImagePath


def getCheckedSeriesIDs(self):
    return treeView.returnSelectedSeries(self)


def getAllCheckedImages(self):
    imagesDict = treeView.returnSelectedImages(self)
    return list(itertools.chain(*NestedDictValues(imagesDict)))


def getImagePathList(self):
    studyID = self.selectedStudy
    seriesID = self.selectedSeries
    return self.objXMLReader.getImagePathList(studyID, seriesID)


def setNewFilePath(inputPath, suffix):
    return saveDICOM_Image.returnFilePath(inputPath, suffix)


def setupMessageBox(self, numImages):
    messageWindow.displayMessageSubWindow(self,
        "<H4>Processing {} DICOM files</H4>".format(numImages),
        "Processing DICOM images")
    messageWindow.setMsgWindowProgBarMaxValue(self, numImages)


def showSavingResultsMessageBox(self, numImages):
    #messageWindow.hideProgressBar(self)
    messageWindow.displayMessageSubWindow(self,
        "<H4>Saving results into {} DICOM files</H4>".format(numImages),
        "Saving DICOM images")


def showProcessingMessageBox(self):
    #messageWindow.hideProgressBar(self)
    messageWindow.displayMessageSubWindow(self,
        "<H4>Running the selected algorithm...</H4>",
        "Processing algorithm")


def inputWindow(paramDict, title="Input Parameters", helpText="", lists=None):
    """Eg. of paramDict (this will need more documentation):
        paramDict = {"Tag":"string", "Value":"string"}
        The variable types are int, float and string.
        The user may add extra validation of the parameters. Read the file
        thresholdDICOM_Image.py as it contains a good example of validation.
    """
    try:
        inputDlg = inputDialog.ParameterInputDialog(paramDict, title=title, helpText=helpText, lists=lists)
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

# DICOM Management
# ===================================================================================================

def copyDICOM(self, inputPath, series_id=None, series_uid=None, suffix="_Copy"):
    try:
        if isinstance(inputPath, str) and os.path.exists(inputPath):
            if series_id is None:
                series_id = int(str(readDICOM_Image.getDicomDataset(inputPath).SeriesNumber) + str(random.randint(0, 9999)))
            if series_uid is None:
                series_uid = pydicom.uid.generate_uid()
            newDataset = readDICOM_Image.getDicomDataset(inputPath)
            derivedPath = setNewFilePath(inputPath, suffix)
            saveDICOM_Image.saveDicomToFile(newDataset, output_path=derivedPath)
            # The next lines perform an overwrite operation over the copied images
            saveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesInstanceUID", series_uid)
            saveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesNumber", series_id)
            saveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesDescription", str(newDataset.SeriesDescription + suffix))
            newSeriesID = interfaceDICOMXMLFile.insertNewImageInXMLFile(self,
                                         derivedPath, suffix)
        elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
            derivedPath = []
            if series_id is None:
                series_id = int(str(readDICOM_Image.getDicomDataset(inputPath[0]).SeriesNumber) + str(random.randint(0, 9999)))
            if series_uid is None:
                series_uid = pydicom.uid.generate_uid()
            for path in inputPath:
                newDataset = readDICOM_Image.getDicomDataset(path)
                newFilePath = setNewFilePath(path, suffix)
                saveDICOM_Image.saveDicomToFile(newDataset, output_path=newFilePath)
                derivedPath.append(newFilePath)
                # The next lines perform an overwrite operation over the copied images
                saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesInstanceUID", series_uid)
                saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesNumber", series_id)
                saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", str(newDataset.SeriesDescription + suffix))
            newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self,
                            inputPath, derivedPath, suffix)
        treeView.refreshDICOMStudiesTreeView(self, newSeriesID) 
        return derivedPath
    except Exception as e:
        print('Error in function #.copyDICOM: ' + str(e))


def deleteDICOM(self, inputPath):
    try:
        if isinstance(inputPath, str) and os.path.exists(inputPath):
            inputDict = {"Confirmation":"string"}
            paramList = inputWindow(inputDict, title="Are you sure you want to delete this image?", helpText="Type YES to delete selected images")
            reply = paramList[0]
            if reply=="YES":
                os.remove(inputPath)
                interfaceDICOMXMLFile.removeImageFromXMLFile(self, inputPath)
        elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
            inputDict = {"Confirmation":"string"}
            paramList = inputWindow(inputDict, title="Are you sure you want to delete these images?", helpText="Type YES to delete selected images")
            reply = paramList[0]
            if reply=="YES":
                for path in inputPath:
                    os.remove(path)
                    interfaceDICOMXMLFile.removeMultipleImagesFromXMLFile(self, inputPath)   
        treeView.refreshDICOMStudiesTreeView(self) 
    except Exception as e:
        print('Error in function #.deleteDICOM: ' + str(e))


def mergeDicomIntoOneSeries(self, imagePathList, series_description="New Series", series_uid=None, series_id=None, suffix="_Merged", overwrite=False):
    try:
        if os.path.exists(imagePathList[0]):
            if series_id is None:
                series_id = int(str(readDICOM_Image.getDicomDataset(imagePathList[0]).SeriesNumber) + str(random.randint(0, 9999)))
            if series_uid is None:
                series_uid = pydicom.uid.generate_uid()
        newImagePathList = []
        if overwrite:
            for path in imagePathList:
                saveDICOM_Image.overwriteDicomFileTag(path, "SeriesInstanceUID", series_uid)
                saveDICOM_Image.overwriteDicomFileTag(path, "SeriesNumber", series_id)
                saveDICOM_Image.overwriteDicomFileTag(path, "SeriesDescription", series_description + suffix)
            newImagePathList = imagePathList
            newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self,
                            imagePathList, newImagePathList, suffix)
            interfaceDICOMXMLFile.removeMultipleImagesFromXMLFile(self, imagePathList)     
        else:
            for path in imagePathList:
                newDataset = readDICOM_Image.getDicomDataset(path)
                newFilePath = setNewFilePath(path, suffix)
                saveDICOM_Image.saveDicomToFile(newDataset, output_path=newFilePath)
                # The next lines perform an overwrite operation over the copied images
                saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesInstanceUID", series_uid)
                saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesNumber", series_id)
                saveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", series_description + suffix)
                newImagePathList.append(newFilePath)
            # CAN WE UPDATE THE XML FILE WITHOUT THE SUFFIX AND IMAGE PATH LIST???
            newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self,
                            imagePathList, newImagePathList, suffix)
        treeView.refreshDICOMStudiesTreeView(self, newSeriesID)
        return newImagePathList
    except Exception as e:
        print('Error in #.mergeDicomIntoOneSeries: ' + str(e))


def editDICOMTag(inputPath, dicomTag, newValue):
    # CONSIDER THE CASES WHERE SERIES NUMBER, NAME AND UID ARE CHANGED - UPDATE XML
    try:
        saveDICOM_Image.overwriteDicomFileTag(inputPath, dicomTag, newValue)
    except Exception as e:
        print('Error in function #.editDICOMTag: ' + str(e))


# PixelArray Processing
# ===================================================================================================

def getPixelArrayFromDICOM(inputPath):
    """Open the DICOM file(s) the PixelArray of the file(s)"""
    try:
        if isinstance(inputPath, str) and os.path.exists(inputPath):
            pixelArray = readDICOM_Image.returnPixelArray(inputPath)
            return pixelArray
        elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
            pixelArray = readDICOM_Image.returnSeriesPixelArray(inputPath)
            return pixelArray
        else:
            return None
    except Exception as e:
        print('Error in function #.getPixelArrayFromDICOM: ' + str(e))


def writeNewPixelArray(self, pixelArray, inputPath, suffix):
    try:
        if isinstance(inputPath, str) and os.path.exists(inputPath):
            numImages = 1
            if hasattr(readDICOM_Image.getDicomDataset(inputPath), 'PerFrameFunctionalGroupsSequence'):
                # If it's Enhanced MRI
                derivedImageList = [pixelArray]
                derivedImageFilePath = setNewFilePath(inputPath, suffix)
                derivedImagePathList = [derivedImageFilePath]

        elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
            if hasattr(readDICOM_Image.getDicomDataset(inputPath[0]), 'PerFrameFunctionalGroupsSequence'):
                # If it's Enhanced MRI
                numImages = 1
                derivedImageList = [pixelArray]
                derivedImageFilePath = setNewFilePath(inputPath[0], suffix)
                derivedImagePathList = [derivedImageFilePath]
            else:
                # Iterate through list of images (slices) and save the resulting Map for each DICOM image
                numImages = (1 if len(np.shape(pixelArray)) < 3 else np.shape(pixelArray)[0])
                derivedImagePathList = []
                derivedImageList = []
                for index in range(numImages):
                    derivedImageFilePath = setNewFilePath(inputPath[index], suffix)
                    derivedImagePathList.append(derivedImageFilePath)
                    if numImages==1:
                        derivedImageList.append(pixelArray)
                    else:
                        derivedImageList.append(pixelArray[index, ...])
                if len(inputPath) > len(derivedImagePathList):
                    inputPath = inputPath[:len(derivedImagePathList)]

        if numImages == 1:    
            saveDICOM_Image.saveDicomOutputResult(derivedImagePathList[0], inputPath, derivedImageList, suffix)
            # Record derived image in XML file
            newSeriesID = interfaceDICOMXMLFile.insertNewImageInXMLFile(self,
                            derivedImagePathList[0], suffix)
        else:
            saveDICOM_Image.saveDicomNewSeries(derivedImagePathList, inputPath, derivedImageList, suffix)
            # Insert new series into the DICOM XML file
            newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self,
                            inputPath, derivedImagePathList, suffix)
        treeView.refreshDICOMStudiesTreeView(self, newSeriesID)
        return derivedImagePathList

    except Exception as e:
        print('Error in function #.writePixelArrayToDicom: ' + str(e))

#def overwritePixelArray()

def displayImage(self, inputPath):
    try:
        if isinstance(inputPath, str) and os.path.exists(inputPath):
            _, studyID, seriesID = treeView.getPathParentNode(self, inputPath)
            displayImageColour.displayImageSubWindow(self, studyID, seriesID, derivedImagePath=inputPath)
        elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
            _, studyID, seriesID = treeView.getPathParentNode(self, inputPath[0])
            displayImageColour.displayMultiImageSubWindow(self, inputPath, studyID, seriesID)
    except Exception as e:
        print('Error in function #.displayImage: ' + str(e))


def applyProcessInOneImage(func, *args):
    try:
        derivedImage = func(*args)
        return np.squeeze(derivedImage) # results have always 1st dimension = 1
    except Exception as e:
        print('Error in function #.applyProcessInOneImage: ' + str(e))


def applyProcessIterativelyInSeries(self, inputPathList, suffix, func, *args, progress_bar=True):
    try: 
        if progress_bar:
            numImages = len(inputPathList)
            setupMessageBox(self, numImages)
            imageCounter = 0
        #Iterate through list of images and apply the algorithm
        derivedImagePathList = []
        derivedImageList = []
        for imagePath in inputPathList:
            derivedImagePath = setNewFilePath(imagePath, suffix)
            inputImage = getPixelArrayFromDICOM(imagePath)
            if inputImage is None:
                continue
            if args:
                derivedImage = applyProcessInOneImage(func, inputImage, *args)
            else:
                derivedImage = applyProcessInOneImage(func, inputImage)
            derivedImagePathList.append(derivedImagePath)
            derivedImageList.append(derivedImage)
            if progress_bar:
                imageCounter += 1
                messageWindow.setMsgWindowProgBarValue(self, imageCounter)
        if progress_bar:
            messageWindow.closeMessageSubWindow(self)
        return derivedImagePathList, derivedImageList
    except Exception as e:
        print('Error in function #.applyProcessIterativelyInSeries: ' + str(e))


# Have to split the following into DICOM (saving features) and GUI (XML and Windows)
# ===================================================================================================

def prepareBulkSeriesSave(self, inputPathList, derivedImage, suffix):
    try:
        if hasattr(readDICOM_Image.getDicomDataset(inputPathList[0]), 'PerFrameFunctionalGroupsSequence'):
            # If it's Enhanced MRI
            numImages = 1
            derivedImageList = [derivedImage]
            derivedImageFilePath = setNewFilePath(inputPathList[0], suffix)
            derivedImagePathList = [derivedImageFilePath]
        else:
            # Iterate through list of images (slices) and save the resulting Map for each DICOM image
            derivedImagePathList = []
            derivedImageList = []
            numImages = (1 if len(np.shape(derivedImage)) < 3 else np.shape(derivedImage)[0])
            for index in range(numImages):
                derivedImageFilePath = setNewFilePath(inputPathList[index], suffix)
                derivedImagePathList.append(derivedImageFilePath)
                if numImages==1:
                    derivedImageList.append(derivedImage)
                else:
                    derivedImageList.append(derivedImage[index, ...])
        return derivedImagePathList, derivedImageList
    except Exception as e:
        print('Error in function #.prepareBulkSeriesSave: ' + str(e))


def saveNewDICOMAndDisplayResult(self, inputPath, derivedPath, derivedImage, suffix):
    try:
        if treeView.isAnImageSelected(self):
            showSavingResultsMessageBox(self, 1)
            # Save new DICOM file locally                                    
            saveDICOM_Image.saveDicomOutputResult(derivedPath, inputPath, derivedImage, suffix)
            messageWindow.closeMessageSubWindow(self)
            # Record derived image in XML file
            newSeriesID = interfaceDICOMXMLFile.insertNewImageInXMLFile(self,
                                         derivedPath, suffix)
            # Display image in a new subwindow
            displayImageColour.displayImageSubWindow(self, derivedPath)
        elif treeView.isASeriesSelected(self):
            showSavingResultsMessageBox(self, len(derivedPath))
            # Save new DICOM series locally
            if len(inputPath) > len(derivedPath):
                inputPath = inputPath[:len(derivedPath)]
            saveDICOM_Image.saveDicomNewSeries(derivedPath, inputPath, derivedImage, suffix)
            messageWindow.closeMessageSubWindow(self)
            # Insert new series into the DICOM XML file
            newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self,
                            inputPath, derivedPath, suffix)
            #Display series of images in a subwindow
            studyID = getStudyID(self)
            displayImageColour.displayMultiImageSubWindow(self,
                derivedPath, studyID, newSeriesID)
        #Refresh the tree view so to include the new series
        treeView.refreshDICOMStudiesTreeView(self, newSeriesID)
    except Exception as e:
        print('Error in function #.saveNewDICOMAndDisplayResult: ' + str(e))
    

def overwriteDICOMAndDisplayResult(self, inputPath, derivedImage):
    """MAYBE USE IMAGE INSTEAD OF DICOM IN FUNCTION TITLE
       ALSO NEED TO WRITE A FUNCTION TO OVERWRITE AN IMAGE ON CURRENT DICOM (IT INVOLVES SLOPE, INTERCEPT, ETC.)
    """
    try:
        if treeView.isAnImageSelected(self):
            showSavingResultsMessageBox(self, 1)
            # Overwrite image in DICOM file                                   
            # saveDICOM_Image.overwriteDicomFileTag(inputPath, "PixelData", derivedImage.tobytes())
            saveDICOM_Image.saveDicomOutputResult(inputPath, inputPath, derivedImage, '')
            # Display image in a new subwindow
            displayImageColour.displayImageSubWindow(self, inputPath)
        elif treeView.isASeriesSelected(self):
            showSavingResultsMessageBox(self, len(inputPath))
            # Overwrite image in  multiple DICOM file
            saveDICOM_Image.saveDicomNewSeries(inputPath, inputPath, derivedImage, '')
            studyID = getStudyID(self)
            seriesID = getSeriesID(self)
            #Display series of images in a subwindow
            displayImageColour.displayMultiImageSubWindow(self,
                inputPath, studyID, seriesID)
        messageWindow.closeMessageSubWindow(self)
    except Exception as e:
        print('Error in function #.overwriteDICOMAndDisplayResult: ' + str(e))
    

def updateXMLAndDisplayResult(self, inputPath, derivedPath, suffix):
    """
    """
    try:
        if len(inputPath) == 1:
            showSavingResultsMessageBox(self, 1)
            newSeriesID = interfaceDICOMXMLFile.insertNewImageInXMLFile(self,
                            derivedPath, suffix)
            displayImageColour.displayImageSubWindow(self, inputPath)
        else:
            studyID = getStudyID(self)
            newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self,
                            inputPath, derivedPath, suffix)
            #Display series of images in a subwindow
            displayImageColour.displayMultiImageSubWindow(self,
                derivedPath, studyID, newSeriesID)
        treeView.refreshDICOMStudiesTreeView(self, newSeriesID)
    except Exception as e:
        print('Error in function #.updateXMLAndDisplayResult: ' + str(e))


####################################################################################
FILE_SUFFIX = '_SomeSuffix'

def pipelineImage(self, func, *args):
    """Creates a subwindow that displays either a DICOM image or series of DICOM images
    processed using the algorithm(s) in func."""
    try:
        if treeView.isAnImageSelected(self):
            imagePath = getImagePath(self)
            derivedImageFileName = setNewFilePath(imagePath, FILE_SUFFIX)
            #####################
            pixelArray = getPixelArrayFromDICOM(imagePath)
            derivedImage = applyProcessInOneImage(pixelArray, func, *args)
            #####################
            saveNewDICOMAndDisplayResult(self, imagePath, derivedImageFileName, derivedImage, FILE_SUFFIX)

        elif treeView.isASeriesSelected(self):
            imagePathList = getImagePathList(self)
            derivedImagePathList, derivedImageList = applyProcessIterativelyInSeries(self, imagePathList, FILE_SUFFIX, func, *args)        
            saveNewDICOMAndDisplayResult(self, imagePathList, derivedImagePathList, derivedImageList, FILE_SUFFIX) 
    except Exception as e:
        print('Error in #.pipelineImage: ' + str(e))


def pipelineImageAndSeries(self, func, *args):
    """Creates a subwindow that displays a series of DICOM images
    processed using the algorithm(s) in func."""
    try:
        imagePathList = getImagePathList(self)

        showProcessingMessageBox(self)
        # **************************************************************************************************
        # Here is where I can make things different - getParameters
        pixelArray = getPixelArrayFromDICOM(imagePathList)
        derivedImage = applyProcessInOneImage(pixelArray, func, *args)
		
		# Get resulting array. Not tested yet, hence it's commented
		# pixelArray = returnPixelArray(imagePathList, funcAlgorithm)
		# Steve, in order to make it work you can use the line below for now
		
		# Suggestion for error management
		# For eg., the script could "conclude" that the algorithm is not applicable

		#if isinstance(pixelArray, str):
            #messageWindow.displayMessageSubWindow(self, pixelArray)
            #raise Exception(pixelArray)
        # ***************************************************************************************************

        derivedImagePathList, derivedImageList = prepareBulkSeriesSave(self, imagePathList, derivedImage, FILE_SUFFIX)

        imagePathList = imagePathList[:len(derivedImagePathList)]
        
        saveNewDICOMAndDisplayResult(self, imagePathList, derivedImagePathList, derivedImageList, FILE_SUFFIX)

    except Exception as e:
        print('Error in #.pipelineImageAndSeries: ' + str(e))