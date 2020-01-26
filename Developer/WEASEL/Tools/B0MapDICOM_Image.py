import os
import numpy as np
import math
import re
import readDICOM_Image
import saveDICOM_Image
from Weasel import Weasel as weasel
from weaselXMLReader import WeaselXMLReader

FILE_SUFFIX = '_B0Map'


def returnPixelArray(imagePathList, sliceList, echoList):
    """Returns the B0 Map Array"""
    try:
        if os.path.exists(imagePathList[0]):
            # Could make a generic method - need to take the Multiframe into account
            dicomList = readDICOM_Image.getSeriesDicomDataset(imagePathList)
            imageList = []
            for individualDicom in dicomList:
                imageList.append(readDICOM_Image.getPixelArray(individualDicom))
            imageArray = np.array(imageList)
            # Next step is to reshape to 3D or 4D - the squeeze makes it 3D if number of slices is =1
            np.squeeze(np.reshape(imageArray, len(echoList), len(sliceList), np.shape(imageArray)[1], np.shape(imageArray)[2]))
            for i in range(0, 2, np.shape(imageArray)[0]):
                print(i)

            # Algorithm
            #newFileName = saveDICOM_Image.returnFilePath(imagePathList[0], FILE_SUFFIX)
            # return  newFileName
            return None
        else:
            return None
    except Exception as e:
        print('Error in function B0MapDICOM_Image.returnPixelArray: ' + str(e))


def offsetB0Algorithm(pixelArray1, pixelArray2, echoList):
    try:
        phaseDiff = pixelArray1 - pixelArray2
        deltaTE = np.absolute(echoList[0] - echoList[1])
        derivedImage = phaseDiff / (np.ones(np.shape(phaseDiff))*(2*math.pi*deltaTE))
        return derivedImage
    except Exception as e:
        print('Error in function B0MapDICOM_Image.offsetB0Algorithm: ' + str(e))


def getParametersB0Map(imagePathList, seriesID):
    try:
        if os.path.exists(imagePathList[0]):
            sortedSequenceSlice, sliceList, numSlices = readDICOM_Image.sortSequenceByTag(imagePathList, "SliceLocation")
            sortedSequenceEcho, echoList, numberEchoes = readDICOM_Image.sortSequenceByTag(sortedSequenceSlice, "EchoTime")
            #phaseList = []
            phasePathList = []
            dicomList = readDICOM_Image.getSeriesDicomDataset(sortedSequenceEcho)
            for index, individualDicom in enumerate(dicomList):
                minValue = np.amin(readDICOM_Image.getPixelArray(individualDicom))
                maxValue = np.amax(readDICOM_Image.getPixelArray(individualDicom))
                if (numberEchoes == 2) and (minValue < 0) and (maxValue > 0) and (re.match(".*B0.*", seriesID) or re.match(".*b0.*", seriesID)):
                    #phaseList.append(individualDicom)
                    phasePathList.append(imagePathList[index])

            del dicomList, numSlices, numberEchoes
            return phasePathList, echoList, sliceList
        else:
            return None, None, None
    except Exception as e:
        print('Error in function B0MapDICOM_Image.checkParametersB0Map: Not possible to calculate B0 Map' + str(e))


def saveB0MapSeries(objWeasel):
    try:
        #imagePathList, studyID, _ = weasel.getImagePathList_Copy()
        studyID = objWeasel.selectedStudy
        seriesID = objWeasel.selectedSeries
        imagePathList = \
            objWeasel.getImagePathList(studyID, seriesID)

        # Should insert Slice sorting before and echotime sorting after this
        phasePathList, echoList, sliceList = getParametersB0Map(imagePathList, seriesID)
        print(phasePathList)
        print(echoList)
        print(sliceList)
        if phasePathList:
            print("Algorithm here: returnPixelArray")
            returnPixelArray(phasePathList, sliceList, echoList)
        else:
            objWeasel.displayMessageSubWindow("NOT POSSIBLE TO CALCULATE B0 MAP")


        print("STILL NEED TO CORRECT FROM THIS LINE - WEASEL WILL RETURN ERROR CORRECTLY AFTER THIS MESSAGE")
        # Iterate through list of images and make a copy of each image
        copiedImagePathList = []
        copiedImageList = []
        numImages = len(imagePathList)
        objWeasel.displayMessageSubWindow(
            "<H4>Copying {} DICOM files</H4>".format(numImages),
            "Copying DICOM images")
        objWeasel.setMsgWindowProgBarMaxValue(numImages)
        imageCounter = 0
        # for imagePath in imagePathList:
        # copiedImageFilePath = returnCopiedFile(imagePath)
        #copiedImage = readDICOM_Image.returnPixelArray(imagePath)
        # copiedImagePathList.append(copiedImageFilePath)
        # copiedImageList.append(copiedImage)
        #imageCounter += 1
        # objWeasel.setMsgWindowProgBarValue(imageCounter)

        objWeasel.closeMessageSubWindow()
        newSeriesID = objWeasel.insertNewSeriesInXMLFile(imagePathList,
                                                         copiedImagePathList, FILE_SUFFIX)
        # Save new DICOM series locally
        saveDICOM_Image.save_dicom_newSeries(
            copiedImagePathList, imagePathList, copiedImageList, FILE_SUFFIX)
        objWeasel.displayMultiImageSubWindow(copiedImagePathList,
                                             studyID, newSeriesID)
        objWeasel.refreshDICOMStudiesTreeView(newSeriesID)
    except Exception as e:
        print('Error in B0MapDICOM_Image.saveB0MapSeries: ' + str(e))
