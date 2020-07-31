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
    #messageWindow.hideProgressBar(objWeasel)
    messageWindow.displayMessageSubWindow(objWeasel,
        "<H4>Saving results into a new DICOM Series</H4>",
        "Processing DICOM images")


def showProcessingMessageBox(objWeasel):
    #messageWindow.hideProgressBar(objWeasel)
    messageWindow.displayMessageSubWindow(objWeasel,
        "<H4>Running the selected algorithm...</H4>",
        "Processing algorithm")


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


def applyProcessInOneImage(func, *args):
    try:
        derivedImage = func(*args)
        return np.squeeze(derivedImage) # results ave always 1st dimension = 1
    except Exception as e:
        print('Error in function #.applyProcessInOneImage: ' + str(e))


def applyProcessIterativelyInSeries(objWeasel, inputPathList, suffix, func, *args, progress_bar=True):
    try: 
        if progress_bar:
            numImages = len(inputPathList)
            setupMessageBox(objWeasel, numImages)
            imageCounter = 0
        #Iterate through list of images and apply the algorithm
        derivedImagePathList = []
        derivedImageList = []
        for imagePath in inputPathList:
            derivedImagePath = setNewFilePath(imagePath, suffix)
            inputImage = getPixelArrayFromDICOM(imagePath)
            if args:
                derivedImage = applyProcessInOneImage(func, inputImage, *args)
            else:
                derivedImage = applyProcessInOneImage(func, inputImage)
            derivedImagePathList.append(derivedImagePath)
            derivedImageList.append(derivedImage)
            if progress_bar:
                imageCounter += 1
                messageWindow.setMsgWindowProgBarValue(objWeasel, imageCounter)
        if progress_bar:
            messageWindow.closeMessageSubWindow(objWeasel)
        return derivedImagePathList, derivedImageList
    except Exception as e:
        print('Error in function #.applyProcessIterativelyInSeries: ' + str(e))


def prepareBulkSeriesSave(objWeasel, inputPathList, derivedImage, suffix):
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


def saveNewDICOMAndDisplayResult(objWeasel, inputPath, derivedPath, derivedImage, suffix):
    try:
        showSavingResultsMessageBox(objWeasel)
        if treeView.isAnImageSelected(objWeasel):
            # Save new DICOM file locally                                    
            saveDICOM_Image.saveDicomOutputResult(derivedPath, inputPath, derivedImage, suffix)
            messageWindow.closeMessageSubWindow(objWeasel)
            # Record derived image in XML file
            newSeriesID = interfaceDICOMXMLFile.insertNewImageInXMLFile(objWeasel,
                                         derivedPath, suffix)
            # Display image in a new subwindow
            displayImageColour.displayImageSubWindow(objWeasel, derivedPath)
        elif treeView.isASeriesSelected(objWeasel):
            # Save new DICOM series locally
            saveDICOM_Image.saveDicomNewSeries(derivedPath, inputPath, derivedImage, suffix)
            messageWindow.closeMessageSubWindow(objWeasel)
            # Insert new series into the DICOM XML file
            newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(objWeasel,
                            inputPath, derivedPath, suffix)
            #Display series of images in a subwindow
            studyID = getStudyID(objWeasel)
            displayImageColour.displayMultiImageSubWindow(objWeasel,
                derivedPath, studyID, newSeriesID)
        #Refresh the tree view so to include the new series
        treeView.refreshDICOMStudiesTreeView(objWeasel, newSeriesID)
    except Exception as e:
        print('Error in function #.saveNewDICOMAndDisplayResult: ' + str(e))
    

def overwriteDICOMAndDisplayResult(objWeasel, inputPath, derivedPath, derivedImage, suffix):
    try:
        showSavingResultsMessageBox(objWeasel)
        #if treeView.isAnImageSelected(objWeasel):
            # Save new DICOM file locally                                    
            # saveDICOM_Image.saveDicomOutputResult(derivedPath, inputPath, derivedImage, suffix)
            # Record derived image in XML file
            # newSeriesID = interfaceDICOMXMLFile.insertNewImageInXMLFile(objWeasel,
                                         #derivedPath, suffix)
            # Display image in a new subwindow
            #displayImageColour.displayImageSubWindow(objWeasel, derivedPath)
        #elif treeView.isASeriesSelected(objWeasel):
            # Save new DICOM series locally
            # saveDICOM_Image.saveDicomNewSeries(derivedPath, inputPath, derivedImage, suffix)
            # Insert new series into the DICOM XML file
            # newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(objWeasel,
                            #inputPath, derivedPath, suffix)
            #Display series of images in a subwindow
            # studyID = getStudyID(objWeasel)
            #displayImageColour.displayMultiImageSubWindow(objWeasel,
                #derivedPath, studyID, newSeriesID)
        #Refresh the tree view so to include the new series
        # treeView.refreshDICOMStudiesTreeView(objWeasel, newSeriesID)
        messageWindow.closeMessageSubWindow(objWeasel)
    except Exception as e:
        print('Error in function #.overwriteDICOMAndDisplayResult: ' + str(e))


####################################################################################


def pipelineImage(objWeasel, func, *args):
    """Creates a subwindow that displays either a DICOM image or series of DICOM images
    processed using the algorithm(s) in func."""
    try:
        if treeView.isAnImageSelected(objWeasel):
            imagePath = getImagePath(objWeasel)
            derivedImageFileName = setNewFilePath(imagePath, FILE_SUFFIX)
            #####################
            pixelArray = getPixelArrayFromDICOM(imagePath)
            derivedImage = applyProcessInOneImage(pixelArray, func, *args)
            #####################
            saveNewDICOMAndDisplayResult(objWeasel, imagePath, derivedImageFileName, derivedImage, FILE_SUFFIX)

        elif treeView.isASeriesSelected(objWeasel):
            imagePathList = getImagePathList(objWeasel)
            derivedImagePathList, derivedImageList = applyProcessIterativelyInSeries(objWeasel, imagePathList, FILE_SUFFIX, func, *args)        
            saveNewDICOMAndDisplayResult(objWeasel, imagePathList, derivedImagePathList, derivedImageList, FILE_SUFFIX) 
    except Exception as e:
        print('Error in #.pipelineImage: ' + str(e))


def pipelineImageAndSeries(objWeasel, func, *args):
    """Creates a subwindow that displays a series of DICOM images
    processed using the algorithm(s) in func."""
    try:
        imagePathList = getImagePathList(objWeasel)

        showProcessingMessageBox(objWeasel)
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
            #messageWindow.displayMessageSubWindow(objWeasel, pixelArray)
            #raise Exception(pixelArray)
        # ***************************************************************************************************

        derivedImagePathList, derivedImageList = prepareBulkSeriesSave(objWeasel, imagePathList, derivedImage, FILE_SUFFIX)

        imagePathList = imagePathList[:len(derivedImagePathList)]
        
        saveNewDICOMAndDisplayResult(objWeasel, imagePathList, derivedImagePathList, derivedImageList, FILE_SUFFIX)

    except Exception as e:
        print('Error in #.pipelineImageAndSeries: ' + str(e))