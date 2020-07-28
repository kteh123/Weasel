import os
import numpy as np
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image
import CoreModules.WEASEL.saveDICOM_Image as saveDICOM_Image
from Developer.WEASEL.ScientificLibrary.imagingTools import thresholdPixelArray
import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.WEASEL.DisplayImageColour  as displayImageColour
import CoreModules.WEASEL.MessageWindow  as messageWindow
import CoreModules.WEASEL.InterfaceDICOMXMLFile  as interfaceDICOMXMLFile
FILE_SUFFIX = '_Thresholded'

def returnPixelArray(imagePath):
    """Applies a low and high threshold on an image and returns the resulting maskArray"""
    try:
        if os.path.exists(imagePath):
            pixelArray = readDICOM_Image.returnPixelArray(imagePath)
            lower_threshold = 40
            upper_threshold = 90
            derivedImage = thresholdPixelArray(pixelArray, lower_threshold, upper_threshold)
            return derivedImage
        else:
            return None
    except Exception as e:
            print('Error in function thresholdDICOM_Image.returnPixelArray: ' + str(e))


def saveImage(objWeasel):
    """Creates a subwindow that displays a binary DICOM image. Executed using the 
    'Threshold Image' Menu item in the Tools menu."""
    try:
        if treeView.isAnImageSelected(objWeasel):
            imagePath = objWeasel.selectedImagePath
            pixelArray = returnPixelArray(imagePath)
            derivedImageFileName = saveDICOM_Image.returnFilePath(imagePath, FILE_SUFFIX)
            displayImageColour.displayImageSubWindow(objWeasel, derivedImageFileName)
            # Save the DICOM file in the new file path                                        
            saveDICOM_Image.saveDicomOutputResult(derivedImageFileName, imagePath, pixelArray, FILE_SUFFIX, parametric_map="SEG")
            #Record squared image in XML file
            seriesID = interfaceDICOMXMLFile.insertNewImageInXMLFile(objWeasel,
                                                 derivedImageFileName, FILE_SUFFIX)
            #Update tree view with xml file modified above
            treeView.refreshDICOMStudiesTreeView(objWeasel,seriesID)
        elif treeView.isASeriesSelected(objWeasel):
            studyID = objWeasel.selectedStudy
            seriesID = objWeasel.selectedSeries
            imagePathList = \
                    objWeasel.objXMLReader.getImagePathList(studyID, seriesID)
            #Iterate through list of images and square each image
            derivedImagePathList = []
            derivedImageList = []
            numImages = len(imagePathList)
            messageWindow.displayMessageSubWindow(objWeasel,
              "<H4>Thresholding {} DICOM files</H4>".format(numImages),
              "Thresholding DICOM images")
            messageWindow.setMsgWindowProgBarMaxValue(objWeasel,numImages)
            imageCounter = 0
            for imagePath in imagePathList:
                derivedImagePath = saveDICOM_Image.returnFilePath(imagePath, FILE_SUFFIX)
                derivedImage = returnPixelArray(imagePath)
                derivedImagePathList.append(derivedImagePath)
                derivedImageList.append(derivedImage)
                imageCounter += 1
                messageWindow.setMsgWindowProgBarValue(objWeasel, imageCounter)
            messageWindow.displayMessageSubWindow(objWeasel,
              "<H4>Saving results into a new DICOM Series</H4>",
              "Thresholding DICOM images")
            messageWindow.setMsgWindowProgBarMaxValue(objWeasel,2)
            messageWindow.setMsgWindowProgBarValue(objWeasel,1)
            # Save new DICOM series locally
            saveDICOM_Image.saveDicomNewSeries(derivedImagePathList, imagePathList, derivedImageList, FILE_SUFFIX, parametric_map="SEG")
            newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(objWeasel,
                                                   imagePathList,
                                                   derivedImagePathList, FILE_SUFFIX)
            messageWindow.setMsgWindowProgBarValue(objWeasel,2)
            messageWindow.closeMessageSubWindow(objWeasel)
            displayImageColour.displayMultiImageSubWindow(objWeasel,
                derivedImagePathList, studyID, newSeriesID)
            treeView.refreshDICOMStudiesTreeView(objWeasel, newSeriesID)
    except Exception as e:
        print('Error in thresholdDICOM_Image.saveImage: ' + str(e))