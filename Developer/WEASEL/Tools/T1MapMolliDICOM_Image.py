import os
import numpy as np
import re
import CoreModules.readDICOM_Image as readDICOM_Image
import CoreModules.saveDICOM_Image as saveDICOM_Image
from CoreModules.weaselToolsXMLReader import WeaselToolsXMLReader
from CoreModules.imagingTools import formatArrayForAnalysis
import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.WEASEL.DisplayImageColour  as displayImageColour
import CoreModules.WEASEL.MessageWindow  as messageWindow
import CoreModules.WEASEL.InterfaceDICOMXMLFile  as interfaceDICOMXMLFile
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
            # The MATLAB code is designed to work with [x, y, TI] as input
            # As of 1st June 2020, I'm using the Python version of T1
            if len(np.shape(pixelArray)) == 4: # If it's 3D with different TIs per slice - Assumption in this specific case
                derivedImage = []
                for zSlice in range(np.shape(pixelArray)[2]):
                    tempImage = ukrinMaps(np.squeeze(pixelArray[:, :, zSlice, :])).T1Map(inversionArray[:, zSlice]) # There's MATLAB version T1MapMolli
                    derivedImage.append(tempImage)
                derivedImage = np.array(derivedImage)
                del tempImage
            else:
                derivedImage = ukrinMaps(pixelArray).T1Map(inversionArray) # There's MATLAB version T1MapMolli
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
                    flagMagnitude, _, _, _, _ = readDICOM_Image.checkImageType(dataset)
                    echo = dataset.MREchoSequence[0].EffectiveEchoTime
                    if (numberTIs > 2) and (echo != 0) and flagMagnitude and (re.match(".*t2.*", seriesID.lower()) or re.match(".*r2.*", seriesID.lower())):
                        sliceList.append(originalSliceList[index])
                        inversionList.append(echo)
                if sliceList and inversionList:
                    inversionList = np.unique(inversionList)
                    magnitudePathList = imagePathList
            else:
                imagePathList, firstSliceList, numberSlices, _ = readDICOM_Image.sortSequenceByTag(imagePathList, "SliceLocation")
                if hasattr(datasetList, 'InversionTime'):
                    imagePathList, inversionList, numberTIs, indicesSorted = readDICOM_Image.sortSequenceByTag(imagePathList, "InversionTime")
                else: # Or elseif
                    imagePathList, inversionList, numberTIs, indicesSorted = readDICOM_Image.sortSequenceByTag(imagePathList, 0x20051572)
                # After sorting, it needs to update the sliceList
                sliceList = [firstSliceList[index] for index in indicesSorted]
                for index in range(len(imagePathList)):
                    dataset = readDICOM_Image.getDicomDataset(imagePathList[index])
                    flagMagnitude, _, _, _, _ = readDICOM_Image.checkImageType(dataset)
                    ti = inversionList[index]
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
            objWeasel.objXMLReader.getImagePathList(studyID, seriesID)

        messageWindow.displayMessageSubWindow(objWeasel,
            "<H4>Extracting parameters to calculate T1 Map</H4>",
            "Saving T1 Map")
        messageWindow.setMsgWindowProgBarMaxValue(objWeasel,4)
        messageWindow.setMsgWindowProgBarValue(objWeasel, 1)

        magnitudePathList, sliceList, inversionList = getParametersT1Map(imagePathList, seriesID)

        messageWindow.displayMessageSubWindow(objWeasel,
            "<H4>Calculating the T1 Map</H4>",
            "Saving T1 Map")
        messageWindow.setMsgWindowProgBarMaxValue(objWeasel, 4)   
        messageWindow.setMsgWindowProgBarValue(objWeasel, 2)

        if magnitudePathList:
            T1Image = returnPixelArray(magnitudePathList, sliceList, inversionList)
        else:
            messageWindow.displayMessageSubWindow(objWeasel, "NOT POSSIBLE TO CALCULATE T1 MAP IN THIS SERIES.")
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

        messageWindow.displayMessageSubWindow(objWeasel, 
            "<H4>Saving {} DICOM files for the T1 Map calculated</H4>".format(numImages),
            "Saving T1 Map")
        messageWindow.setMsgWindowProgBarMaxValue(objWeasel, 4)
        messageWindow.setMsgWindowProgBarValue(objWeasel, 3)

        # Save new DICOM series locally
        saveDICOM_Image.saveDicomNewSeries(
            T1ImagePathList, imagePathList, T1ImageList, FILE_SUFFIX)
        newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(objWeasel,
                                                     magnitudePathList[:len(T1ImagePathList)],
                                                        T1ImagePathList, FILE_SUFFIX)
        messageWindow.setMsgWindowProgBarValue(objWeasel, 4)                                                    
        messageWindow.closeMessageSubWindow(objWeasel)
        displayImageColour.displayMultiImageSubWindow(objWeasel,T1ImagePathList,
                                             studyID, newSeriesID)
        treeView.refreshDICOMStudiesTreeView(objWeasel, newSeriesID)
    except Exception as e:
        print('Error in T1MapDICOM_Image.saveT1MapSeries: ' + str(e))
