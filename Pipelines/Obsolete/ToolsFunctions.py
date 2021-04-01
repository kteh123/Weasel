
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
def main(objWeasel, fileSuffix, funcAlgorithm):
    """Creates a subwindow that displays either a DICOM image or series of DICOM images
    processed using the algorithm in funcAlgorithm."""
    try:
        if objWeasel.isAnImageChecked:
            imagePath = objWeasel.selectedImagePath
            studyID = objWeasel.selectedStudy
            pixelArray = returnPixelArray(imagePath, funcAlgorithm)
            
            derivedImageFileName = saveDICOM_Image.returnFilePath(imagePath, fileSuffix)
           
            # Save the DICOM file in the new file path                                        
            saveDICOM_Image.saveNewSingleDicomImage(derivedImageFileName, imagePath, pixelArray, fileSuffix)#, parametric_map="ADC")
            #Record squared image in XML file
            seriesID = interfaceDICOMXMLFile.insertNewImageInXMLFile(objWeasel, imagePath,
                                         derivedImageFileName, fileSuffix)

            #Display the derived image in a subwindow
            displayImageColour.displayImageSubWindow(objWeasel, studyID, seriesID, derivedImageFileName)

            #Update tree view with xml file modified above
            treeView.refreshDICOMStudiesTreeView(objWeasel, seriesID)

        elif objWeasel.isASeriesChecked:
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
            saveDICOM_Image.saveDicomNewSeries(derivedImagePathList, imagePathList, derivedImageList, fileSuffix)#, parametric_map="ADC")
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
        print('Error in #.main: ' + str(e))


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
    