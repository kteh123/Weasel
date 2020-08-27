import os
import numpy as np
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image
import CoreModules.WEASEL.saveDICOM_Image as saveDICOM_Image
import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.WEASEL.DisplayImageColour  as displayImageColour
import CoreModules.WEASEL.MessageWindow  as messageWindow
import CoreModules.WEASEL.InterfaceDICOMXMLFile  as interfaceDICOMXMLFile
from PyQt5.QtWidgets import QMessageBox

FILE_SUFFIX = '_Copy'

def returnCopiedFile(imagePath):
    """Returns the filepath of the new copied file."""
    try:
        if os.path.exists(imagePath):
            newFileName = saveDICOM_Image.returnFilePath(imagePath, FILE_SUFFIX)
            return  newFileName
        else:
            return None
    except Exception as e:
            print('Error in function copyDICOM_Image.returnPixelArray: ' + str(e))


def copySeries(objWeasel):
    """This method duplicates/copies all DICOM files of the selected Series."""
    try:
        studyID = objWeasel.selectedStudy 
        seriesID = objWeasel.selectedSeries
        imagePathList = \
            objWeasel.objXMLReader.getImagePathList(studyID, seriesID)
        #Iterate through list of images and make a copy of each image
        copiedImagePathList = []
        copiedImageList = []
        numImages = len(imagePathList)
        messageWindow.displayMessageSubWindow(objWeasel,
            "<H4>Copying {} DICOM files</H4>".format(numImages),
            "Copying DICOM images")
        messageWindow.setMsgWindowProgBarMaxValue(objWeasel, numImages)
        imageCounter = 0
        for imagePath in imagePathList:
            copiedImageFilePath = returnCopiedFile(imagePath)
            copiedImage = readDICOM_Image.returnPixelArray(imagePath)
            copiedImagePathList.append(copiedImageFilePath)
            copiedImageList.append(copiedImage)
            imageCounter += 1
            messageWindow.setMsgWindowProgBarValue(objWeasel, imageCounter)
        messageWindow.displayMessageSubWindow(objWeasel,
            "<H4>Saving results into a new DICOM Series</H4>",
            "Copying DICOM images")
        messageWindow.setMsgWindowProgBarMaxValue(objWeasel, 2)
        messageWindow.setMsgWindowProgBarValue(objWeasel, 1)
        # Save new DICOM series locally
        saveDICOM_Image.saveDicomNewSeries(copiedImagePathList, imagePathList, copiedImageList, FILE_SUFFIX)
        newSeriesID= interfaceDICOMXMLFile.insertNewSeriesInXMLFile(objWeasel,
                                               imagePathList, 
                                               copiedImagePathList, 
                                               FILE_SUFFIX)
        messageWindow.setMsgWindowProgBarValue(objWeasel, 2)
        messageWindow.closeMessageSubWindow(objWeasel)
        displayImageColour.displayMultiImageSubWindow(objWeasel, copiedImagePathList, 
                                              studyID, newSeriesID)
        treeView.refreshDICOMStudiesTreeView(objWeasel, newSeriesID)

    except (IndexError, AttributeError):
                msgBox = QMessageBox()
                msgBox.setWindowTitle("Copy a DICOM series")
                msgBox.setText("Select either a series")
                msgBox.exec()
    except Exception as e:
        print('Error in copyDICOM_Image.copySeries: ' + str(e))


