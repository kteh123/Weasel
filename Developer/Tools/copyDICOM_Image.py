import os
import numpy as np
import readDICOM_Image
import saveDICOM_Image
from Weasel import Weasel as weasel

FILE_SUFFIX = '_copy'

def returnCopiedFile(imagePath):
    """Inverts an image. Bits that are 0 become 1, and those that are 1 become 0"""
    try:
        if os.path.exists(imagePath):
            dataset = readDICOM_Image.getDicomDataset(imagePath)
            pixelArray = readDICOM_Image.getPixelArray(dataset)
            newFileName = saveDICOM_Image.save_automatically_and_returnFilePath(
                 imagePath, pixelArray, FILE_SUFFIX)
            return  newFileName
        else:
            return None
    except Exception as e:
            print('Error in function copyDICOM_Image.returnPixelArray: ' + str(e))


def copySeries(objWeasel):
        try:
            #imageList, studyID, _ = weasel.getImagePathList_Copy()  
            studyID = objWeasel.selectedStudy 
            seriesID = objWeasel.selectedSeries
            imageList = \
                    objWeasel.getImagePathList(studyID, seriesID)
            #Iterate through list of images and make a copy of each image
            copiedImageList = []
            for imagePath in imageList:
                copiedImageFilePath = returnCopiedFile(imagePath)
                copiedImageList.append(copiedImageFilePath)
         
            newSeriesID= objWeasel.insertNewSeriesInXMLFile(imageList, \
                copiedImageList, FILE_SUFFIX)
            objWeasel.displayMultiImageSubWindow(copiedImageList, 
                                              studyID, newSeriesID)
            objWeasel.refreshDICOMStudiesTreeView(newSeriesID)
        except Exception as e:
            print('Error in copyDICOM_Image.copySeries: ' + str(e))
