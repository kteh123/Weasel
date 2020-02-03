import os
import numpy as np
import math
import re
import CoreModules.readDICOM_Image as readDICOM_Image
import CoreModules.saveDICOM_Image as saveDICOM_Image
#from Weasel import Weasel as weasel
from CoreModules.weaselToolsXMLReader import WeaselToolsXMLReader

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
            volumeArray = np.array(imageList)
            # Next step is to reshape to 3D or 4D - the squeeze makes it 3D if number of slices is =1
            imageArray = np.squeeze(np.reshape(volumeArray, (int(np.shape(volumeArray)[0]/len(sliceList)), len(sliceList), np.shape(volumeArray)[1], np.shape(volumeArray)[2])))    
                    
            # Algorithm
            pixelArray = B0map(imageArray, echoList)

            del volumeArray, imageArray, imageList, dicomList
            return pixelArray
        else:
            return None
    except Exception as e:
        print('Error in function B0MapDICOM_Image.returnPixelArray: ' + str(e))


def B0map(imageArray, echoList):
    try:
        # Unwrapping Phase?
        # https://scikit-image.org/docs/dev/auto_examples/filters/plot_phase_unwrap.html
        phaseDiff = np.squeeze(imageArray[0, ...] - imageArray[1, ...])
        deltaTE = np.absolute(echoList[0] - echoList[1]) * 0.001 # Conversion from ms to s
        derivedImage = phaseDiff / (np.ones(np.shape(phaseDiff))*(2*math.pi*deltaTE))
        return derivedImage
    except Exception as e:
        print('Error in function B0MapDICOM_Image.B0map: ' + str(e))


def getParametersB0Map(imagePathList, seriesID):
    try:
        if os.path.exists(imagePathList[0]):
            # Sort by slice last place
            sortedSequenceEcho, echoList, numberEchoes = readDICOM_Image.sortSequenceByTag(imagePathList, "EchoTime")
            sortedSequenceSlice, sliceList, numSlices = readDICOM_Image.sortSequenceByTag(sortedSequenceEcho, "SliceLocation")
            phasePathList = []
            dicomList = readDICOM_Image.getSeriesDicomDataset(sortedSequenceSlice)
            for index, individualDicom in enumerate(dicomList):
                minValue = np.amin(readDICOM_Image.getPixelArray(individualDicom))
                maxValue = np.amax(readDICOM_Image.getPixelArray(individualDicom))
                if (numberEchoes == 2) and (minValue < 0) and (maxValue > 0) and (re.match(".*B0.*", seriesID) or re.match(".*b0.*", seriesID)):
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
        if phasePathList:
            B0Image = returnPixelArray(phasePathList, sliceList, echoList)
        else:
            B0Image = []
            objWeasel.displayMessageSubWindow("NOT POSSIBLE TO CALCULATE B0 MAP IN THIS SERIES.")
            raise ValueError("NOT POSSIBLE TO CALCULATE B0 MAP IN THIS SERIES.")

        # Iterate through list of images and save B0 for each image
        B0ImagePathList = []
        B0ImageList = []
        numImages = len(phasePathList)
        objWeasel.displayMessageSubWindow(
            "<H4Saving {} DICOM files for B0 Map calculated</H4>".format(numImages),
            "Saving B0 Map into DICOM Images")
        objWeasel.setMsgWindowProgBarMaxValue(numImages)
        imageCounter = 0
        for index in range(np.shape(B0Image)[0]):
            B0ImageFilePath = saveDICOM_Image.returnFilePath(phasePathList[index], FILE_SUFFIX)
            B0ImagePathList.append(B0ImageFilePath)
            B0ImageList.append(B0Image[index, ...])
            imageCounter += 1
            objWeasel.setMsgWindowProgBarValue(imageCounter)

        objWeasel.closeMessageSubWindow()
        newSeriesID = objWeasel.insertNewSeriesInXMLFile(phasePathList[:len(B0ImagePathList)],
                                                         B0ImagePathList, FILE_SUFFIX)
        # Save new DICOM series locally
        saveDICOM_Image.save_dicom_newSeries(
            B0ImagePathList, imagePathList, B0ImageList, FILE_SUFFIX)
        objWeasel.displayMultiImageSubWindow(B0ImagePathList,
                                             studyID, newSeriesID)
        objWeasel.refreshDICOMStudiesTreeView(newSeriesID)
    except Exception as e:
        print('Error in B0MapDICOM_Image.saveB0MapSeries: ' + str(e))
