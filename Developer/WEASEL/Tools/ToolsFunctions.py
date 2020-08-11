
import os
import numpy as np
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image
import CoreModules.WEASEL.saveDICOM_Image as saveDICOM_Image
import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.WEASEL.DisplayImageColour  as displayImageColour
import CoreModules.WEASEL.MessageWindow  as messageWindow
import CoreModules.WEASEL.InterfaceDICOMXMLFile  as interfaceDICOMXMLFile


#This function name must not be changed
def returnPixelArray(imagePath, func):
    """Applies the algorithm in the function, func to
   an image and returns the resulting PixelArray"""
    try:
        if os.path.exists(imagePath):
            dataset = readDICOM_Image.getDicomDataset(imagePath)
            pixelArray = readDICOM_Image.returnPixelArray(imagePath)
            derivedImage = func(pixelArray, dataset)
            return derivedImage
        else:
            return None
    except Exception as e:
            print('Error in function #.returnPixelArray: ' + str(e))


#This function name must not be changed
def saveImage(objWeasel, fileSuffix, funcAlgorithm):
    """Creates a subwindow that displays either a DICOM image or series of DICOM images
    processed using the algorithm in funcAlgorithm."""
    try:
        if treeView.isAnImageSelected(objWeasel):
            imagePath = objWeasel.selectedImagePath

            pixelArray = returnPixelArray(imagePath, funcAlgorithm)
            
            derivedImageFileName = saveDICOM_Image.returnFilePath(imagePath, fileSuffix)
           
            # Save the DICOM file in the new file path                                        
            saveDICOM_Image.saveDicomOutputResult(derivedImageFileName, imagePath, pixelArray, fileSuffix)
            #Record squared image in XML file
            seriesID = interfaceDICOMXMLFile.insertNewImageInXMLFile(objWeasel,
                                         derivedImageFileName, fileSuffix)

            #Display the derived image in a subwindow
            displayImageColour.displayImageSubWindow(objWeasel, derivedImageFileName)

            #Update tree view with xml file modified above
            treeView.refreshDICOMStudiesTreeView(objWeasel, seriesID)

        elif treeView.isASeriesSelected(objWeasel):
            imagePathList, studyID = returnImagePathList(objWeasel)
            setupMessageBox(objWeasel, len(imagePathList))

            #Iterate through list of images and apply the algorithm
            imageCounter = 0
            derivedImagePathList = []
            derivedImageList = []
            for imagePath in imagePathList:
                derivedImagePath = saveDICOM_Image.returnFilePath(imagePath, fileSuffix)
                derivedImage = returnPixelArray(imagePath, funcAlgorithm)
                derivedImagePathList.append(derivedImagePath)
                derivedImageList.append(derivedImage)
                imageCounter += 1
                messageWindow.setMsgWindowProgBarValue(objWeasel, imageCounter)
            
            
            # Save new DICOM series locally
            showSavingResultsMessageBox(objWeasel)
            saveDICOM_Image.saveDicomNewSeries(derivedImagePathList, imagePathList, derivedImageList, fileSuffix)
            #Insert new series into the DICOM XML file
            newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(objWeasel,
                            imagePathList,
                            derivedImagePathList, fileSuffix)
            messageWindow.closeMessageSubWindow(objWeasel)

            #Display series of images in a subwindow
            displayImageColour.displayMultiImageSubWindow(objWeasel,
                derivedImagePathList, studyID, newSeriesID)

            #Refresh the tree view so to include the new series
            treeView.refreshDICOMStudiesTreeView(objWeasel, newSeriesID)
    except Exception as e:
        print('Error in #.saveImage: ' + str(e))


def returnImagePathList(objWeasel):
    studyID = objWeasel.selectedStudy
    seriesID = objWeasel.selectedSeries
    return objWeasel.objXMLReader.getImagePathList(studyID, seriesID), studyID


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
    
####################################################################################
# Steve, please have a look at the functions below and ask me any questions you have
# None of this was tested yet, still need some time to perfect this.

# This method is not going to be used yet, 
# but please notice the use of readDICOM_Image.returnSeriesPixelArray(imagePathList)
#
#Joao I had to comment out this section as it was causing an error - inconsistent white space & tabs
#
#def returnPixelArray(imagePathList, func):
#    """Applies the algorithm(s) in the function, func to
#    an image and returns the resulting PixelArray"""
#    try:
#        if os.path.exists(imagePathList[0]):
#            pixelArray = readDICOM_Image.returnSeriesPixelArray(imagePathList)
#            derivedImage = func(pixelArray)
#            return derivedImage
#        else:
#            return None
#    except Exception as e:
#            print('Error in function #.returnPixelArray: ' + str(e))


#def saveSeries(objWeasel):
#    """Creates a subwindow that displays either a series of DICOM images
#    processed using the algorithm(s) in funcAlgorithm."""
#    try:
#        imagePathList, studyID = returnImagePathList(objWeasel)
        
#		messageWindow.displayMessageSubWindow(objWeasel,
#            "<H4>Calculating <Insert message here></H4>",
#            "Calculating Template Parametric Map")
#        messageWindow.setMsgWindowProgBarMaxValue(objWeasel,3)
#        messageWindow.setMsgWindowProgBarValue(objWeasel,1)
		
#		# Get resulting array. Not tested yet, hence it's commented
#		# pixelArray = returnPixelArray(imagePathList, funcAlgorithm)
#		# Steve, in order to make it work you can use the line below for now
#		pixelArray = readDICOM_Image.returnSeriesPixelArray(imagePathList)
		
#		# Suggestion for error management
#		# For eg., the script could "conclude" that the algorithm is not applicable
#		if isinstance(pixelArray, str):
#			messageWindow.displayMessageSubWindow(objWeasel, pixelArray)
#            raise Exception(pixelArray)
		
#		if hasattr(readDICOM_Image.getDicomDataset(imagePathList[0]), 'PerFrameFunctionalGroupsSequence'):
#            # If it's Enhanced MRI
#            numImages = 1
#            derivedImageList = [pixelArray]
#            derivedImageFilePath = saveDICOM_Image.returnFilePath(imagePathList[0], fileSuffix)
#            derivedImagePathList = [derivedImageFilePath]
#        else:
#            # Iterate through list of images (slices) and save the resulting Map for each DICOM image
#            derivedImagePathList = []
#            derivedImageList = []
#            numImages = (1 if len(np.shape(derivedImage)) < 3 else np.shape(derivedImage)[0])
#            for index in range(numImages):
#				#Joao Sousa needs to review the use of imagePathList in the following line
#                derivedImageFilePath = saveDICOM_Image.returnFilePath([index], fileSuffix)
#                derivedImagePathList.append(derivedImageFilePath)
#                if numImages==1:
#                    derivedImageList.append(derivedImage)imagePathList
#                else:
#                    derivedImageList.append(derivedImage[index, ...])

#        messageWindow.displayMessageSubWindow(objWeasel, 
#            "<H4>Saving {} DICOM files for <Insert message here></H4>".format(numImages),
#            "Saving Template Parametric Map")
#        messageWindow.setMsgWindowProgBarMaxValue(objWeasel,3)
#        messageWindow.setMsgWindowProgBarValue(objWeasel,2)

#        # Save new DICOM series locally
#        saveDICOM_Image.saveDicomNewSeries(
#            derivedImagePathList, imagePathList, derivedImageList, fileSuffix)
#		#Joao Sousa needs to review the use of imagePathList in the following line
#        newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(objWeasel,
#                        imagePathList[:len(derivedImagePathList)],
#                        derivedImagePathList, fileSuffix)
#        messageWindow.setMsgWindowProgBarValue(objWeasel,3)                                              
#        messageWindow.closeMessageSubWindow(objWeasel)
#        displayImageColour.displayMultiImageSubWindow(objWeasel,
#            derivedImagePathList, studyID, newSeriesID)
#        treeView.refreshDICOMStudiesTreeView(objWeasel, newSeriesID)
			
#    except Exception as e:
#        print('Error in #.saveSeries: ' + str(e))
