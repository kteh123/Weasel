import os
import numpy as np
import math
import re
import struct
import CoreModules.readDICOM_Image as readDICOM_Image
import CoreModules.saveDICOM_Image as saveDICOM_Image
#from Weasel import Weasel as weasel
from CoreModules.weaselToolsXMLReader import WeaselToolsXMLReader

FILE_SUFFIX = '_B0Map'


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
            print(np.shape(volumeArray))
            # Next step is to reshape to 3D or 4D - the squeeze makes it 3D if number of slices is =1
            imageArray = np.squeeze(np.reshape(volumeArray, (int(np.shape(volumeArray)[0]/len(sliceList)), len(sliceList), np.shape(volumeArray)[1], np.shape(volumeArray)[2])))    
            print(np.shape(imageArray))
            # Algorithm
            pixelArray = B0map(imageArray, echoList)

            del volumeArray, imageArray, imageList, dicomList
            return pixelArray
        else:
            return None
    except Exception as e:
        print('Error in function B0MapDICOM_Image.returnPixelArray: ' + str(e))


def returnPixelArrayFromRealIm(imagePathList, sliceList, echoList):
    """Returns the B0 Map Array"""
    try:
        if os.path.exists(imagePathList[0][0]) and os.path.exists(imagePathList[1][0]):
            # Could make a generic method - need to take the Multiframe into account
            realDicomList = readDICOM_Image.getSeriesDicomDataset(imagePathList[0])
            imaginaryDicomList = readDICOM_Image.getSeriesDicomDataset(imagePathList[1])
            realImageList = []
            imaginaryImageList = []
            for index, individualDicom in enumerate(realDicomList):
                realImageList.append(readDICOM_Image.getPixelArray(individualDicom))
                imaginaryImageList.append(readDICOM_Image.getPixelArray(imaginaryDicomList[index]))
            realVolumeArray = np.array(realImageList)
            imaginaryVolumeArray = np.array(imaginaryImageList)       
            volumeArray = np.arctan2(imaginaryVolumeArray, realVolumeArray) * 1000
            print(np.shape(volumeArray))
            # Next step is to reshape to 3D or 4D - the squeeze makes it 3D if number of slices is =1
            imageArray = np.squeeze(np.reshape(volumeArray, (int(np.shape(volumeArray)[0]/len(sliceList)), len(sliceList), np.shape(volumeArray)[1], np.shape(volumeArray)[2])))    
            print(np.shape(imageArray))
            # Algorithm
            pixelArray = B0map(imageArray, echoList)

            del volumeArray, imageArray#, imageList, dicomList
            return pixelArray
        else:
            return None
    except Exception as e:
        print('Error in function B0MapDICOM_Image.returnPixelArrayFromRealIm: ' + str(e))


def getParametersB0Map(imagePathList, seriesID):
    try:
        if os.path.exists(imagePathList[0]):
            # Sort by slice last place
            sortedSequenceEcho, echoList, numberEchoes = readDICOM_Image.sortSequenceByTag(imagePathList, "EchoTime")
            sortedSequenceSlice, sliceList, numSlices = readDICOM_Image.sortSequenceByTag(sortedSequenceEcho, "SliceLocation")
            phasePathList = []
            riPathList = [[], []]
            dicomList = readDICOM_Image.getSeriesDicomDataset(sortedSequenceSlice)
            for index, individualDicom in enumerate(dicomList):
                flagPhase = False
                flagReal = False
                flagImaginary = False
                try: #MAG = 0; PHASE = 1; REAL = 2; IMAG = 3; # RawDataType_ImageType in GE - '0x0043102f'
                    if struct.unpack('h', individualDicom[0x0043102f].value)[0] == 1:
                        flagPhase = True
                    if struct.unpack('h', individualDicom[0x0043102f].value)[0] == 2:
                        flagReal = True
                    if struct.unpack('h', individualDicom[0x0043102f].value)[0] == 3:
                        flagImaginary = True
                except: pass
                if hasattr(individualDicom, 'ImageType'): 
                    if ('P' in individualDicom.ImageType) or ('PHASE' in individualDicom.ImageType):
                        flagPhase = True
                    elif ('R' in individualDicom.ImageType) or ('REAL' in individualDicom.ImageType):
                        flagReal = True
                    elif ('I' in individualDicom.ImageType) or ('IMAGINARY' in individualDicom.ImageType):
                        flagImaginary = True
                if (numberEchoes == 2) and flagPhase and re.match(".*b0.*", seriesID.lower()):
                    phasePathList.append(imagePathList[index])
                elif (numberEchoes == 2) and flagReal and re.match(".*b0.*", seriesID.lower()):
                    riPathList[0].append(imagePathList[index])
                elif (numberEchoes == 2) and flagImaginary and re.match(".*b0.*", seriesID.lower()):
                    riPathList[1].append(imagePathList[index])
                print(riPathList)

            del dicomList, numSlices, numberEchoes, flagPhase, flagReal, flagImaginary
            return phasePathList, sliceList, echoList, riPathList
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
        phasePathList, sliceList, echoList, riPathList = getParametersB0Map(imagePathList, seriesID)
        if phasePathList:
            B0Image = returnPixelArray(phasePathList, sliceList, echoList)
        elif riPathList[0] and riPathList[1]:
            B0Image = returnPixelArrayFromRealIm(riPathList, sliceList, echoList)
            phasePathList = riPathList[0] # Here we're assuming that the saving will be performed based on the Real Images
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
