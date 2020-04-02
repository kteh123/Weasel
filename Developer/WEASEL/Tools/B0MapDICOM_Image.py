import os
import numpy as np
import re
import struct
import CoreModules.readDICOM_Image as readDICOM_Image
import CoreModules.saveDICOM_Image as saveDICOM_Image
from CoreModules.weaselToolsXMLReader import WeaselToolsXMLReader
from CoreModules.imagingTools import formatArrayForAnalysis, unWrapPhase
from ukrinAlgorithms import ukrinMaps

FILE_SUFFIX = '_B0Map'
# THE ENHANCED MRI B0 STILL NEEDS MORE TESTING. I DON'T HAVE ANY CASE WITH 2 TEs IN ENHANCED MRI

def returnPixelArray(imagePathList, sliceList, echoList):
    """Returns the B0 Map Array with the Phase images as starting point"""
    try:
        if os.path.exists(imagePathList[0]):
            dataset = readDICOM_Image.getDicomDataset(imagePathList[0])
            if hasattr(dataset, 'PerFrameFunctionalGroupsSequence'): # For Enhanced MRI, sliceList is a list of indices
                volumeArray, sliceList, numberSlices = readDICOM_Image.getMultiframeBySlices(dataset, sliceList=sliceList, sort=True)
            else: # For normal DICOM, slicelist is a list of slice locations in mm.
                volumeArray = readDICOM_Image.returnSeriesPixelArray(imagePathList)
                numberSlices = len(sliceList)
            pixelArray = formatArrayForAnalysis(volumeArray, numberSlices, dataset, dimension='4D')
            # Algorithm
            derivedImage = ukrinMaps(pixelArray).B0MapOriginal(echoList)
            del volumeArray, pixelArray, dataset
            return derivedImage
        else:
            return None
    except Exception as e:
        print('Error in function B0MapDICOM_Image.returnPixelArray: ' + str(e))


def returnPixelArrayFromRealIm(imagePathList, sliceList, echoList):
    """Returns the B0 Map Array with the Real and Imaginary images as starting point"""
    try:
        if os.path.exists(imagePathList[0][0]) and os.path.exists(imagePathList[1][0]):
            dataset = readDICOM_Image.getDicomDataset(imagePathList[0][0])
            if hasattr(dataset, 'PerFrameFunctionalGroupsSequence'): # For Enhanced MRI, sliceList is a list of indices
                realVolumeArray, sliceList, numberSlices = readDICOM_Image.getMultiframeBySlices(dataset, sliceList=imagePathList[0][1:], sort=True)
                imaginaryVolumeArray, _, _ = readDICOM_Image.getMultiframeBySlices(dataset, sliceList=imagePathList[1][1:], sort=True)
            else: # For normal DICOM, slicelist is a list of slice locations in mm.
                realVolumeArray = readDICOM_Image.returnSeriesPixelArray(imagePathList[0])
                imaginaryVolumeArray = readDICOM_Image.returnSeriesPixelArray(imagePathList[1])  
                numberSlices = len(sliceList)
            volumeArray = np.arctan2(realVolumeArray, imaginaryVolumeArray)
            pixelArray = formatArrayForAnalysis(volumeArray, numberSlices, dataset, dimension='4D')
            # Algorithm
            derivedImage = ukrinMaps(pixelArray).B0MapOriginal(echoList) # Maybe np.invert() to have the same result as the other series
            del volumeArray, pixelArray, dataset, imaginaryVolumeArray, realVolumeArray
            return derivedImage
        else:
            return None
    except Exception as e:
        print('Error in function B0MapDICOM_Image.returnPixelArrayFromRealIm: ' + str(e))


def getParametersB0Map(imagePathList, seriesID):
    """This method checks if the series in imagePathList meets the criteria to be processed and calculate B0 Map"""
    try:
        if os.path.exists(imagePathList[0]):
            phasePathList = []
            riPathList = [[], []]
            datasetList = readDICOM_Image.getDicomDataset(imagePathList[0])
            if hasattr(datasetList, 'PerFrameFunctionalGroupsSequence'):
                echoList = []
                sliceList = []
                numberEchoes = datasetList[0x20011014].value
                _, originalSliceList, numberSlices = readDICOM_Image.getMultiframeBySlices(datasetList)
                for index, dataset in enumerate(datasetList.PerFrameFunctionalGroupsSequence):
                    flagPhase = False
                    flagReal = False
                    flagImaginary = False
                    echo = dataset.MREchoSequence[0].EffectiveEchoTime
                    if hasattr(dataset.MRImageFrameTypeSequence[0], 'FrameType'): # and hasattr(dataset.MRImageFrameTypeSequence[0], 'ComplexImageComponent'):
                        if set(['P', 'PHASE', 'B0', 'FIELD_MAP']).intersection(set(dataset.MRImageFrameTypeSequence[0].FrameType)): # or set(['P', 'PHASE']).intersection(set(dataset.MRImageFrameTypeSequence[0].ComplexImageComponent)):
                            flagPhase = True
                        elif set(['R', 'REAL']).intersection(set(dataset.MRImageFrameTypeSequence[0].FrameType)): # or set(['R', 'REAL']).intersection(set(dataset.MRImageFrameTypeSequence[0].ComplexImageComponent)):
                            flagReal = True
                        elif set(['I', 'IMAGINARY']).intersection(set(dataset.MRImageFrameTypeSequence[0].FrameType)): # or set(['I', 'IMAGINARY']).intersection(set(dataset.MRImageFrameTypeSequence[0].ComplexImageComponent)):
                            flagImaginary = True
                    if (numberEchoes >= 1) and flagPhase and (re.match(".*b0.*", seriesID.lower()), re.match(".*t2.*", seriesID.lower()) or re.match(".*r2.*", seriesID.lower())):
                        sliceList.append(originalSliceList[index])
                        echoList.append(echo)
                    elif (numberEchoes >= 1) and flagReal and (re.match(".*b0.*", seriesID.lower()), re.match(".*t2.*", seriesID.lower()) or re.match(".*r2.*", seriesID.lower())):
                        riPathList[0].append(originalSliceList[index])
                        echoList.append(echo)
                    elif (numberEchoes >= 1) and flagImaginary and (re.match(".*b0.*", seriesID.lower()), re.match(".*t2.*", seriesID.lower()) or re.match(".*r2.*", seriesID.lower())):
                        riPathList[1].append(originalSliceList[index])
                        echoList.append(echo)
                if sliceList and echoList:
                    echoList = np.unique(echoList)
                    phasePathList = imagePathList
                elif riPathList and echoList:
                    echoList = np.unique(echoList)
                    riPathList[0] = imagePathList + riPathList[0]
                    riPathList[1] = imagePathList + riPathList[1]
            else:
                sortedSequenceEcho, echoList, numberEchoes = readDICOM_Image.sortSequenceByTag(imagePathList, "EchoTime")
                sortedSequenceSlice, sliceList, numberSlices = readDICOM_Image.sortSequenceByTag(sortedSequenceEcho, "SliceLocation")
                datasetList = readDICOM_Image.getSeriesDicomDataset(sortedSequenceSlice)
                echoList = np.delete(echoList, np.where(echoList == 0.0))
                numberEchoes = len(echoList)
                for index, dataset in enumerate(datasetList):
                    flagPhase = False
                    flagReal = False
                    flagImaginary = False
                    #echo = dataset.EchoTime
                    try: #MAG = 0; PHASE = 1; REAL = 2; IMAG = 3; # RawDataType_ImageType in GE - '0x0043102f'
                        if struct.unpack('h', dataset[0x0043102f].value)[0] == 1:
                            flagPhase = True
                        if struct.unpack('h', dataset[0x0043102f].value)[0] == 2:
                            flagReal = True
                        if struct.unpack('h', dataset[0x0043102f].value)[0] == 3:
                            flagImaginary = True
                    except: pass
                    if hasattr(dataset, 'ImageType'): 
                        if ('P' in dataset.ImageType) or ('PHASE' in dataset.ImageType) or ('B0' in dataset.ImageType) or ('FIELD_MAP' in dataset.ImageType):
                            flagPhase = True
                        elif ('R' in dataset.ImageType) or ('REAL' in dataset.ImageType):
                            flagReal = True
                        elif ('I' in dataset.ImageType) or ('IMAGINARY' in dataset.ImageType):
                            flagImaginary = True
                    if (numberEchoes >= 1) and flagPhase and (re.match(".*b0.*", seriesID.lower()), re.match(".*t2.*", seriesID.lower()) or re.match(".*r2.*", seriesID.lower())):
                        phasePathList.append(imagePathList[index])
                    elif (numberEchoes >= 1) and flagReal and (re.match(".*b0.*", seriesID.lower()), re.match(".*t2.*", seriesID.lower()) or re.match(".*r2.*", seriesID.lower())):
                        riPathList[0].append(imagePathList[index])
                    elif (numberEchoes >= 1) and flagImaginary and (re.match(".*b0.*", seriesID.lower()), re.match(".*t2.*", seriesID.lower()) or re.match(".*r2.*", seriesID.lower())):
                        riPathList[1].append(imagePathList[index])

            del datasetList, numberSlices, numberEchoes, flagPhase, flagReal, flagImaginary
            return phasePathList, sliceList, echoList, riPathList
        else:
            return None, None, None, None
    except Exception as e:
        print('Error in function B0MapDICOM_Image.getParametersB0Map: ' + str(e))


def saveB0MapSeries(objWeasel):
    """Main method called from WEASEL to calculate the B0 Map"""
    try:
        studyID = objWeasel.selectedStudy
        seriesID = objWeasel.selectedSeries
        imagePathList = \
            objWeasel.getImagePathList(studyID, seriesID)

        objWeasel.displayMessageSubWindow(
            "<H4>Extracting parameters to calculate B0 Map</H4>",
            "Saving B0 Map")
        objWeasel.setMsgWindowProgBarMaxValue(4)
        objWeasel.setMsgWindowProgBarValue(1)

        phasePathList, sliceList, echoList, riPathList = getParametersB0Map(imagePathList, seriesID)

        objWeasel.displayMessageSubWindow(
            "<H4>Calculating the B0 Map</H4>",
            "Saving B0 Map")
        objWeasel.setMsgWindowProgBarMaxValue(4)   
        objWeasel.setMsgWindowProgBarValue(2)

        if phasePathList:
            B0Image = returnPixelArray(phasePathList, sliceList, echoList)
        elif riPathList[0] and riPathList[1]:
            B0Image = returnPixelArrayFromRealIm(riPathList, sliceList, echoList)
            phasePathList = riPathList[0] # Here we're assuming that the saving will be performed based on the Real Images
        else:
            objWeasel.displayMessageSubWindow("NOT POSSIBLE TO CALCULATE B0 MAP IN THIS SERIES.")
            raise Exception("Not possible to calculate B0 Map in the selected series.")

        if hasattr(readDICOM_Image.getDicomDataset(phasePathList[0]), 'PerFrameFunctionalGroupsSequence'):
            # If it's Enhanced MRI
            numImages = 1
            B0ImageList = [B0Image]
            B0ImageFilePath = saveDICOM_Image.returnFilePath(phasePathList[0], FILE_SUFFIX)
            B0ImagePathList = [B0ImageFilePath]
        else:
            # Iterate through list of images and save B0 for each image
            B0ImagePathList = []
            B0ImageList = []
            numImages = np.shape(B0Image)[0]
            for index in range(numImages):
                B0ImageFilePath = saveDICOM_Image.returnFilePath(phasePathList[index], FILE_SUFFIX)
                B0ImagePathList.append(B0ImageFilePath)
                B0ImageList.append(B0Image[index, ...])
        
        objWeasel.displayMessageSubWindow(
            "<H4>Saving {} DICOM files for the B0 Map calculated</H4>".format(numImages),
            "Saving B0 Map")
        objWeasel.setMsgWindowProgBarMaxValue(4)
        objWeasel.setMsgWindowProgBarValue(3)
        
        # Save new DICOM series locally
        saveDICOM_Image.saveDicomNewSeries(
            B0ImagePathList, imagePathList, B0ImageList, FILE_SUFFIX)
        newSeriesID = objWeasel.insertNewSeriesInXMLFile(phasePathList[:len(B0ImagePathList)], 
                                                            B0ImagePathList, FILE_SUFFIX)
        objWeasel.setMsgWindowProgBarValue(4)                                                    
        objWeasel.closeMessageSubWindow()
        objWeasel.displayMultiImageSubWindow(B0ImagePathList,
                                             studyID, newSeriesID)
        objWeasel.refreshDICOMStudiesTreeView(newSeriesID)
    except Exception as e:
        print('Error in B0MapDICOM_Image.saveB0MapSeries: ' + str(e))
