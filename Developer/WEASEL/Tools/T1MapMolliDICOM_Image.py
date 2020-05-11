import os
import numpy as np
import re
import struct
import CoreModules.readDICOM_Image as readDICOM_Image
import CoreModules.saveDICOM_Image as saveDICOM_Image
from CoreModules.weaselToolsXMLReader import WeaselToolsXMLReader
from CoreModules.imagingTools import formatArrayForAnalysis
from ukrinAlgorithms import ukrinMaps

FILE_SUFFIX = '_T1Map'

def returnPixelArray(imagePathList, sliceList, inversionList):
    """Returns the T1 Map Array"""
    try:
        if os.path.exists(imagePathList[0]):
            dataset = readDICOM_Image.getDicomDataset(imagePathList[0])
            if hasattr(dataset, 'PerFrameFunctionalGroupsSequence'): # For Enhanced MRI, sliceList is a list of indices
                volumeArray, sliceList, numberSlices = readDICOM_Image.getMultiframeBySlices(dataset, sliceList=sliceList, sort=True)
            else: # For normal DICOM, slicelist is a list of slice locations in mm.
                volumeArray = readDICOM_Image.returnSeriesPixelArray(imagePathList)
                numberSlices = len(np.unique(sliceList))
            pixelArray = formatArrayForAnalysis(volumeArray, numberSlices, dataset, dimension='4D', transpose=True)
            inversionArray = formatArrayForAnalysis(inversionList, numberSlices, dataset, dimension='2D')
            # Algorithm
            # This MATLAB code is designed to work with [x, y, TI] as input
            if len(np.shape(pixelArray)) == 4: # If it's 3D with different TIs
                derivedImage = []
                for zSlice in range(np.shape(pixelArray)[2]):
                    tempImage = ukrinMaps(np.squeeze(pixelArray[:, :, zSlice, :])).T1MapMolli(inversionArray[:, zSlice])
                    derivedImage.append(tempImage)
                derivedImage = np.array(derivedImage)
                del tempImage
            else:
                derivedImage = ukrinMaps(pixelArray).T1MapMolli(inversionArray)
            del volumeArray, pixelArray, numberSlices, dataset, inversionArray
            return derivedImage
        else:
            return None
    except Exception as e:
        print('Error in function T1MapDICOM_Image.returnPixelArray: ' + str(e))


def getParametersT1Map(imagePathList, seriesID):
    """This method checks if the series in imagePathList meets the criteria to be processed and calculate T1 Map"""
    try:
        if os.path.exists(imagePathList[0]):
            magnitudePathList = []
            datasetList = readDICOM_Image.getDicomDataset(imagePathList[0]) # even though it can be 1 file only, I'm naming datasetList due to consistency
            # Still need to change Echo Time to Inversion Time - need an example Enhanced MRI dataset
            ############################################################################
            if hasattr(datasetList, 'PerFrameFunctionalGroupsSequence'):
                inversionList = []
                sliceList = []
                numberTIs = datasetList[0x20011014].value
                _, originalSliceList, numberSlices = readDICOM_Image.getMultiframeBySlices(datasetList)
                for index, dataset in enumerate(datasetList.PerFrameFunctionalGroupsSequence):
                    flagMagnitude = False
                    echo = dataset.MREchoSequence[0].EffectiveEchoTime
                    if hasattr(dataset.MRImageFrameTypeSequence[0], 'FrameType') and hasattr(dataset.MRImageFrameTypeSequence[0], 'ComplexImageComponent'):
                        if set(['M', 'MAGNITUDE']).intersection(set(dataset.MRImageFrameTypeSequence[0].FrameType)) or set(['M', 'MAGNITUDE']).intersection(set(dataset.MRImageFrameTypeSequence[0].ComplexImageComponent)):
                            flagMagnitude = True
                    if (numberTIs > 2) and (echo != 0) and flagMagnitude and (re.match(".*t2.*", seriesID.lower()) or re.match(".*r2.*", seriesID.lower())):
                        sliceList.append(originalSliceList[index])
                        inversionList.append(echo)
                if sliceList and inversionList:
                    inversionList = np.unique(inversionList)
                    magnitudePathList = imagePathList
            else:
                if hasattr(datasetList, 'InversionTime'):
                    sortedSequenceTI, inversionList, numberTIs = readDICOM_Image.sortSequenceByTag(imagePathList, "InversionTime")
                else: # Or elseif
                    sortedSequenceTI, inversionList, numberTIs = readDICOM_Image.sortSequenceByTag(imagePathList, 0x20051572)
                sortedSequenceSlice, sliceList, numberSlices = readDICOM_Image.sortSequenceByTag(sortedSequenceTI, "SliceLocation")
                datasetList = readDICOM_Image.getSeriesDicomDataset(sortedSequenceSlice)
                for index, dataset in enumerate(datasetList):
                    flagMagnitude = False
                    ti = inversionList[index]
                    try: #MAG = 0; PHASE = 1; REAL = 2; IMAG = 3; # RawDataType_ImageType in GE - '0x0043102f'
                        try:
                            if struct.unpack('h', dataset[0x0043102f].value)[0] == 0:
                                flagMagnitude = True
                        except:
                            if dataset[0x0043102f].value == 0:
                                flagMagnitude = True
                    except: pass
                    if hasattr(dataset, 'ImageType'):
                        if set(['M', 'MAGNITUDE']).intersection(set(dataset.ImageType)):
                            flagMagnitude = True
                    if (numberTIs > 1) and (ti != 0) and flagMagnitude and (re.match(".*t1.*", seriesID.lower()) or re.match(".*molli.*", seriesID.lower()) or re.match(".*tfl.*", seriesID.lower())):
                        magnitudePathList.append(imagePathList[index])
            del datasetList, numberSlices, numberTIs, flagMagnitude
            return magnitudePathList, sliceList, inversionList
        else:
            return None, None, None
    except Exception as e:
        print('Error in function T1MapDICOM_Image.getParametersT1Map: ' + str(e))


def saveT1MapSeries(objWeasel):
    """Main method called from WEASEL to calculate the T1 Map"""
    try:
        studyID = objWeasel.selectedStudy
        seriesID = objWeasel.selectedSeries
        imagePathList = \
            objWeasel.getImagePathList(studyID, seriesID)

        objWeasel.displayMessageSubWindow(
            "<H4>Extracting parameters to calculate T1 Map</H4>",
            "Saving T1 Map")
        objWeasel.setMsgWindowProgBarMaxValue(4)
        objWeasel.setMsgWindowProgBarValue(1)

        magnitudePathList, sliceList, inversionList = getParametersT1Map(imagePathList, seriesID)

        objWeasel.displayMessageSubWindow(
            "<H4>Calculating the T1 Map</H4>",
            "Saving T1 Map")
        objWeasel.setMsgWindowProgBarMaxValue(4)   
        objWeasel.setMsgWindowProgBarValue(2)

        if magnitudePathList:
            T1Image = returnPixelArray(magnitudePathList, sliceList, inversionList)
        else:
            objWeasel.displayMessageSubWindow("NOT POSSIBLE TO CALCULATE T1 MAP IN THIS SERIES.")
            raise Exception("Not possible to calculate T1 Map in the selected series.")

        if hasattr(readDICOM_Image.getDicomDataset(magnitudePathList[0]), 'PerFrameFunctionalGroupsSequence'):
            # If it's Enhanced MRI
            numImages = 1
            T1ImageList = [T1Image]
            T1ImageFilePath = saveDICOM_Image.returnFilePath(magnitudePathList[0], FILE_SUFFIX)
            T1ImagePathList = [T1ImageFilePath]
        else:
            # Iterate through list of images and save T1 for each image
            T1ImagePathList = []
            T1ImageList = []
            numImages = (1 if len(np.shape(T1Image)) < 3 else np.shape(T1Image)[0])
            for index in range(numImages):
                T1ImageFilePath = saveDICOM_Image.returnFilePath(magnitudePathList[index], FILE_SUFFIX)
                T1ImagePathList.append(T1ImageFilePath)
                if numImages==1:
                    T1ImageList.append(T1Image)
                else:
                    T1ImageList.append(T1Image[index, ...])

        objWeasel.displayMessageSubWindow(
            "<H4>Saving {} DICOM files for the T1 Map calculated</H4>".format(numImages),
            "Saving T1 Map")
        objWeasel.setMsgWindowProgBarMaxValue(4)
        objWeasel.setMsgWindowProgBarValue(3)

        # Save new DICOM series locally
        saveDICOM_Image.saveDicomNewSeries(
            T1ImagePathList, imagePathList, T1ImageList, FILE_SUFFIX)
        newSeriesID = objWeasel.insertNewSeriesInXMLFile(magnitudePathList[:len(T1ImagePathList)],
                                                        T1ImagePathList, FILE_SUFFIX)
        objWeasel.setMsgWindowProgBarValue(4)                                                    
        objWeasel.closeMessageSubWindow()
        objWeasel.displayMultiImageSubWindow(T1ImagePathList,
                                             studyID, newSeriesID)
        objWeasel.refreshDICOMStudiesTreeView(newSeriesID)
    except Exception as e:
        print('Error in T1MapDICOM_Image.saveT1MapSeries: ' + str(e))
