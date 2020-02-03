import os
import numpy as np
import CoreModules.readDICOM_Image as readDICOM_Image
import CoreModules.saveDICOM_Image as saveDICOM_Image
#from Weasel import Weasel as weasel
from CoreModules.weaselToolsXMLReader import WeaselToolsXMLReader

FILE_SUFFIX = '_Copy'

def returnCopiedFile(imagePath):
    """Inverts an image. Bits that are 0 become 1, and those that are 1 become 0"""
    try:
        if os.path.exists(imagePath):
            newFileName = saveDICOM_Image.returnFilePath(imagePath, FILE_SUFFIX)
            return  newFileName
        else:
            return None
    except Exception as e:
            print('Error in function copyDICOM_Image.returnPixelArray: ' + str(e))


def copySeries(objWeasel):
        try:
            #imagePathList, studyID, _ = weasel.getImagePathList_Copy()  
            studyID = objWeasel.selectedStudy 
            seriesID = objWeasel.selectedSeries
            imagePathList = \
                    objWeasel.getImagePathList(studyID, seriesID)
            #Iterate through list of images and make a copy of each image
            copiedImagePathList = []
            copiedImageList = []
            numImages = len(imagePathList)
            objWeasel.displayMessageSubWindow(
              "<H4>Copying {} DICOM files</H4>".format(numImages),
              "Copying DICOM images")
            objWeasel.setMsgWindowProgBarMaxValue(numImages)
            imageCounter = 0
            for imagePath in imagePathList:
                copiedImageFilePath = returnCopiedFile(imagePath)
                copiedImage = readDICOM_Image.returnPixelArray(imagePath)
                copiedImagePathList.append(copiedImageFilePath)
                copiedImageList.append(copiedImage)
                imageCounter += 1
                objWeasel.setMsgWindowProgBarValue(imageCounter)

            objWeasel.closeMessageSubWindow()
            newSeriesID= objWeasel.insertNewSeriesInXMLFile(imagePathList, \
                copiedImagePathList, FILE_SUFFIX)
            # Save new DICOM series locally
            saveDICOM_Image.save_dicom_newSeries(copiedImagePathList, imagePathList, copiedImageList, FILE_SUFFIX)
            objWeasel.displayMultiImageSubWindow(copiedImagePathList, 
                                              studyID, newSeriesID)
            objWeasel.refreshDICOMStudiesTreeView(newSeriesID)
        except Exception as e:
            print('Error in copyDICOM_Image.copySeries: ' + str(e))


