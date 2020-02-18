import os
import numpy as np
import math
import re
import struct
from skimage.restoration import unwrap_phase
import CoreModules.readDICOM_Image as readDICOM_Image
import CoreModules.saveDICOM_Image as saveDICOM_Image
from CoreModules.weaselToolsXMLReader import WeaselToolsXMLReader
from Developer.WEASEL.Tools.imagingTools import resizePixelArray

FILE_SUFFIX = '_B0Map'


def B0map(pixelArray, echoList):
    try:
        phaseDiff = np.squeeze(pixelArray[0, ...] - pixelArray[1, ...])
        deltaTE = np.absolute(echoList[0] - echoList[1]) * 0.001 # Conversion from ms to s
        derivedImage = unwrap_phase(phaseDiff) / (np.ones(np.shape(phaseDiff))*(2*math.pi*deltaTE))
        return derivedImage
    except Exception as e:
        print('Error in function B0MapDICOM_Image.B0map: ' + str(e))


def returnPixelArray(imagePathList, sliceList, echoList):
    """Returns the B0 Map Array with the Phase images as starting point"""
    try:
        if os.path.exists(imagePathList[0]):
            datasetSample = readDICOM_Image.getDicomDataset(imagePathList[0])
            volumeArray = readDICOM_Image.returnSeriesPixelArray(imagePathList)
            # Next step is to reshape to 3D or 4D - the squeeze makes it 3D if number of slices is =1
            pixelArray = np.squeeze(np.reshape(volumeArray, (int(np.shape(volumeArray)[0]/len(sliceList)), len(sliceList), np.shape(volumeArray)[1], np.shape(volumeArray)[2])))    
            pixelArray = resizePixelArray(pixelArray, datasetSample.PixelSpacing[0]) 
            # Algorithm
            derivedImage = B0map(pixelArray, echoList)
            del volumeArray, pixelArray, datasetSample
            return derivedImage
        else:
            return None
    except Exception as e:
        print('Error in function B0MapDICOM_Image.returnPixelArray: ' + str(e))


def returnPixelArrayFromRealIm(imagePathList, sliceList, echoList):
    """Returns the B0 Map Array with the Real and Imaginary images as starting point"""
    try:
        if os.path.exists(imagePathList[0][0]) and os.path.exists(imagePathList[1][0]):
            datasetSample = readDICOM_Image.getDicomDataset(imagePathList[0][0])
            realVolumeArray = readDICOM_Image.returnSeriesPixelArray(imagePathList[0])
            imaginaryVolumeArray = readDICOM_Image.returnSeriesPixelArray(imagePathList[1])      
            volumeArray = np.arctan2(imaginaryVolumeArray, realVolumeArray)
            # Next step is to reshape to 3D or 4D - the squeeze makes it 3D if number of slices is =1
            pixelArray = np.squeeze(np.reshape(volumeArray, (int(np.shape(volumeArray)[0]/len(sliceList)), len(sliceList), np.shape(volumeArray)[1], np.shape(volumeArray)[2])))   
            pixelArray = resizePixelArray(pixelArray, datasetSample.PixelSpacing[0]) 
            # Algorithm
            derivedImage = B0map(pixelArray, echoList)
            del volumeArray, pixelArray, datasetSample
            return derivedImage
        else:
            return None
    except Exception as e:
        print('Error in function B0MapDICOM_Image.returnPixelArrayFromRealIm: ' + str(e))


def getParametersB0Map(imagePathList, seriesID):
    """This method checks if the series in imagePathList meets the criteria to be processed and calculate B0 Map"""
    try:
        if os.path.exists(imagePathList[0]):
            # Sort by slice last place
            phasePathList = []
            riPathList = [[], []]
            sortedSequenceEcho, echoList, numberEchoes = readDICOM_Image.sortSequenceByTag(imagePathList, "EchoTime")
            sortedSequenceSlice, sliceList, numSlices = readDICOM_Image.sortSequenceByTag(sortedSequenceEcho, "SliceLocation")
            datasetList = readDICOM_Image.getSeriesDicomDataset(sortedSequenceSlice)
            for index, dataset in enumerate(datasetList):
                flagPhase = False
                flagReal = False
                flagImaginary = False
                try: #MAG = 0; PHASE = 1; REAL = 2; IMAG = 3; # RawDataType_ImageType in GE - '0x0043102f'
                    if struct.unpack('h', dataset[0x0043102f].value)[0] == 1:
                        flagPhase = True
                    if struct.unpack('h', dataset[0x0043102f].value)[0] == 2:
                        flagReal = True
                    if struct.unpack('h', dataset[0x0043102f].value)[0] == 3:
                        flagImaginary = True
                except: pass
                if hasattr(dataset, 'ImageType'): 
                    if ('P' in dataset.ImageType) or ('PHASE' in dataset.ImageType):
                        flagPhase = True
                    elif ('R' in dataset.ImageType) or ('REAL' in dataset.ImageType):
                        flagReal = True
                    elif ('I' in dataset.ImageType) or ('IMAGINARY' in dataset.ImageType):
                        flagImaginary = True
                if (numberEchoes == 2) and flagPhase and re.match(".*b0.*", seriesID.lower()):
                    phasePathList.append(imagePathList[index])
                elif (numberEchoes == 2) and flagReal and re.match(".*b0.*", seriesID.lower()):
                    riPathList[0].append(imagePathList[index])
                elif (numberEchoes == 2) and flagImaginary and re.match(".*b0.*", seriesID.lower()):
                    riPathList[1].append(imagePathList[index])

            del datasetList, numSlices, numberEchoes, flagPhase, flagReal, flagImaginary
            return phasePathList, sliceList, echoList, riPathList
        else:
            return None, None, None, None
    except Exception as e:
        print('Error in function B0MapDICOM_Image.checkParametersB0Map: Not possible to calculate B0 Map' + str(e))


def saveB0MapSeries(objWeasel):
    """Main method called from WEASEL to calculate the B0 Map"""
    try:
        studyID = objWeasel.selectedStudy
        seriesID = objWeasel.selectedSeries
        imagePathList = \
            objWeasel.getImagePathList(studyID, seriesID)

        phasePathList, sliceList, echoList, riPathList = getParametersB0Map(imagePathList, seriesID)
        if phasePathList:
            B0Image = returnPixelArray(phasePathList, sliceList, echoList)
        elif riPathList[0] and riPathList[1]:
            B0Image = returnPixelArrayFromRealIm(riPathList, sliceList, echoList)
            phasePathList = riPathList[0] # Here we're assuming that the saving will be performed based on the Real Images
        else:
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
        
        # Save new DICOM series locally
        saveDICOM_Image.saveDicomNewSeries(
            B0ImagePathList, imagePathList, B0ImageList, FILE_SUFFIX)
        newSeriesID = objWeasel.insertNewSeriesInXMLFile(phasePathList[:len(B0ImagePathList)], 
                                                            B0ImagePathList, FILE_SUFFIX)
        objWeasel.displayMultiImageSubWindow(B0ImagePathList,
                                             studyID, newSeriesID)
        objWeasel.refreshDICOMStudiesTreeView(newSeriesID)
    except Exception as e:
        print('Error in B0MapDICOM_Image.saveB0MapSeries: ' + str(e))
