import os
import numpy as np
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image
import CoreModules.WEASEL.saveDICOM_Image as saveDICOM_Image
import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.DisplayImageColour as displayImageColour
import CoreModules.WEASEL.MessageWindow as messageWindow
import CoreModules.WEASEL.InterfaceDICOMXMLFile as interfaceDICOMXMLFile

#***************************************************************************
#Added by third party developer to the template module. 
#The function containing the image processing algorithm must be given the 
#generic name, funcAlgorithm
#uncomment and edit the following line of code to import the function 
#containing your image processing algorith. 
#from CoreModules.WEASEL.someModule import someFunction as funcAlgorithm
FILE_SUFFIX = '_SomeSuffix'
#***************************************************************************

def getStudyID(objWeasel):
    return objWeasel.selectedStudy


def getSeriesID(objWeasel):
    return objWeasel.selectedSeries


def getImagePath(objWeasel):
    return objWeasel.selectedImagePath


def getImagePathList(objWeasel):
    studyID = objWeasel.selectedStudy
    seriesID = objWeasel.selectedSeries
    return objWeasel.objXMLReader.getImagePathList(studyID, seriesID)


def setNewFilePath(inputPath, suffix):
    return saveDICOM_Image.returnFilePath(inputPath, suffix)


def setupMessageBox(objWeasel, numImages):
    messageWindow.displayMessageSubWindow(objWeasel,
        "<H4>Processing {} DICOM files</H4>".format(numImages),
        "Processing DICOM images")
    messageWindow.setMsgWindowProgBarMaxValue(objWeasel, numImages)


def showSavingResultsMessageBox(objWeasel):
    messageWindow.hideProgressBar(objWeasel)
    messageWindow.displayMessageSubWindow(objWeasel,
        "<H4>Saving results into a new DICOM Series</H4>",
        "Processing DICOM images")


def showProcessingMessageBox(objWeasel):
    messageWindow.hideProgressBar(objWeasel)
    messageWindow.displayMessageSubWindow(objWeasel,
        "<H4>Running the selected algorithm...</H4>",
        "Processing algorithm")


def openPixelArrayFromDICOM(inputPath):
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
        print('Error in function #.openPixelArrayFromDICOM: ' + str(e))


def applyProcessInOneImage(pixelArray, func):
    try:
        derivedImage = func(pixelArray)
        return derivedImage
    except Exception as e:
        print('Error in function #.applyProcessInOneImage: ' + str(e))


def applyProcessIterativelyInSeries(objWeasel, inputPathList, suffix, func):
    try:
        numImages = len(inputPathList)
        setupMessageBox(objWeasel, numImages)
        #Iterate through list of images and apply the algorithm
        imageCounter = 0
        derivedImagePathList = []
        derivedImageList = []
        for imagePath in inputPathList:
            derivedImagePath = setNewFilePath(imagePath, suffix)
            inputImage = openPixelArrayFromDICOM(imagePath)
            derivedImage = applyProcessInOneImage(inputImage, func)
            derivedImagePathList.append(derivedImagePath)
            derivedImageList.append(derivedImage)
            imageCounter += 1
            messageWindow.setMsgWindowProgBarValue(objWeasel, imageCounter)
        return derivedImagePathList, derivedImageList
    except Exception as e:
        print('Error in function #.applyProcessIterativelyInSeries: ' + str(e))


def prepareBulkSeriesSave(objWeasel, inputPathList, derivedImage):
    try:
        if hasattr(readDICOM_Image.getDicomDataset(inputPathList[0]), 'PerFrameFunctionalGroupsSequence'):
            # If it's Enhanced MRI
            numImages = 1
            derivedImageList = [derivedImage]
            derivedImageFilePath = setNewFilePath(inputPathList[0], FILE_SUFFIX)
            derivedImagePathList = [derivedImageFilePath]
        else:
            # Iterate through list of images (slices) and save the resulting Map for each DICOM image
            derivedImagePathList = []
            derivedImageList = []
            numImages = (1 if len(np.shape(derivedImage)) < 3 else np.shape(derivedImage)[0])
            for index in range(numImages):
                derivedImageFilePath = setNewFilePath(inputPathList[index], FILE_SUFFIX)
                derivedImagePathList.append(derivedImageFilePath)
                if numImages==1:
                    derivedImageList.append(derivedImage)
                else:
                    derivedImageList.append(derivedImage[index, ...])
        return derivedImagePathList, derivedImageList
    except Exception as e:
        print('Error in function #.prepareBulkSeriesSave: ' + str(e))


def saveAndDisplayResult(objWeasel, inputPath, derivedPath, derivedImage, suffix):
    try:
        showSavingResultsMessageBox(objWeasel)
        if treeView.isAnImageSelected(objWeasel):
            # Save new DICOM file locally                                    
            saveDICOM_Image.saveDicomOutputResult(derivedPath, inputPath, derivedImage, suffix)
            # Record derived image in XML file
            newSeriesID = interfaceDICOMXMLFile.insertNewImageInXMLFile(objWeasel,
                                         derivedImageFileName, suffix)
            # Display image in a new subwindow
            displayImageColour.displayImageSubWindow(objWeasel, derivedImageFileName)
        elif treeView.isASeriesSelected(objWeasel):
            # Save new DICOM series locally
            saveDICOM_Image.saveDicomNewSeries(derivedPath, inputPath, derivedImage, suffix)
            # Insert new series into the DICOM XML file
            newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(objWeasel,
                            inputPath, derivedPath, suffix)
            #Display series of images in a subwindow
            studyID = getStudyID(objWeasel)
            displayImageColour.displayMultiImageSubWindow(objWeasel,
                derivedPath, studyID, newSeriesID)
        #Refresh the tree view so to include the new series
        treeView.refreshDICOMStudiesTreeView(objWeasel, newSeriesID)
        messageWindow.closeMessageSubWindow(objWeasel)
    except Exception as e:
        print('Error in function #.saveAndDisplayResult: ' + str(e))


####################################################################################


def pipelineImage(objWeasel):
    """Creates a subwindow that displays either a DICOM image or series of DICOM images
    processed using the algorithm(s) in func."""
    try:
        if treeView.isAnImageSelected(objWeasel):
            imagePath = getImagePath(objWeasel)
            derivedImageFileName = setNewFilePath(imagePath, FILE_SUFFIX)
            ############

            pixelArray = openPixelArrayFromDICOM(imagePath)
            getParameters
            derivedImage = applyProcessInOneImage(pixelArray, func)

            #####################
            saveAndDisplayResult(objWeasel, imagePath, derivedImageFileName, derivedImage, FILE_SUFFIX)

        elif treeView.isASeriesSelected(objWeasel):
            imagePathList = getImagePathList(objWeasel)
            derivedImagePathList, derivedImageList = applyProcessIterativelyInSeries(objWeasel, imagePathList, FILE_SUFFIX, func)        
            saveAndDisplayResult(objWeasel, imagePathList, derivedImagePathList, derivedImageList, FILE_SUFFIX)
            
    except Exception as e:
        print('Error in #.pipelineImage: ' + str(e))


def pipelineImageAndSeries(objWeasel):
    """Creates a subwindow that displays a series of DICOM images
    processed using the algorithm(s) in func."""
    try:
        imagePathList = getImagePathList(objWeasel)

        showProcessingMessageBox(objWeasel)
        # **************************************************************************************************
        # Here is where I can make things different - getParameters
        pixelArray = openPixelArrayFromDICOM(imagePathList)
        derivedImage = applyProcessInOneImage(pixelArray, func)
		
		# Get resulting array. Not tested yet, hence it's commented
		# pixelArray = returnPixelArray(imagePathList, funcAlgorithm)
		# Steve, in order to make it work you can use the line below for now
		
		# Suggestion for error management
		# For eg., the script could "conclude" that the algorithm is not applicable

		if isinstance(pixelArray, str):
            messageWindow.displayMessageSubWindow(objWeasel, pixelArray)
            raise Exception(pixelArray)
        # ***************************************************************************************************
		


		if hasattr(readDICOM_Image.getDicomDataset(imagePathList[0]), 'PerFrameFunctionalGroupsSequence'):
            # If it's Enhanced MRI
            numImages = 1
            derivedImageList = [pixelArray]
            derivedImageFilePath = saveDICOM_Image.returnFilePath(imagePathList[0], FILE_SUFFIX)
            derivedImagePathList = [derivedImageFilePath]
        else:
            # Iterate through list of images (slices) and save the resulting Map for each DICOM image
            derivedImagePathList = []
            derivedImageList = []
            numImages = (1 if len(np.shape(derivedImage)) < 3 else np.shape(derivedImage)[0])
            for index in range(numImages):
				#Joao Sousa needs to review the use of imagePathList in the following line
                derivedImageFilePath = saveDICOM_Image.returnFilePath(imagePathList[index], FILE_SUFFIX)
                derivedImagePathList.append(derivedImageFilePath)
                if numImages==1:
                    derivedImageList.append(derivedImage)
                else:
                    derivedImageList.append(derivedImage[index, ...])
            
        messageWindow.closeMessageSubWindow(objWeasel)

        # Replace with saveAndDisplayResult
        # Bear in mind the following: imagePathList[:len(derivedImagePathList)]

        messageWindow.displayMessageSubWindow(objWeasel, 
            "<H4>Saving {} DICOM files for <Insert message here></H4>".format(numImages),
            "Saving Template Parametric Map")
        messageWindow.setMsgWindowProgBarMaxValue(objWeasel,3)
        messageWindow.setMsgWindowProgBarValue(objWeasel,2)

        # Save new DICOM series locally
        saveDICOM_Image.saveDicomNewSeries(
            derivedImagePathList, imagePathList, derivedImageList, FILE_SUFFIX)
		#Joao Sousa needs to review the use of imagePathList in the following line
        newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(objWeasel,
                        imagePathList[:len(derivedImagePathList)],
                        derivedImagePathList, FILE_SUFFIX)
        messageWindow.setMsgWindowProgBarValue(objWeasel,3)                                              
        messageWindow.closeMessageSubWindow(objWeasel)
        displayImageColour.displayMultiImageSubWindow(objWeasel,
            derivedImagePathList, studyID, newSeriesID)
        treeView.refreshDICOMStudiesTreeView(objWeasel, newSeriesID)

    except Exception as e:
        print('Error in #.pipelineImageAndSeries: ' + str(e))