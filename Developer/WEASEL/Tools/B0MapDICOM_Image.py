import os
import numpy as np
import re
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image
import CoreModules.WEASEL.saveDICOM_Image as saveDICOM_Image
import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.WEASEL.DisplayImageColour  as displayImageColour
import CoreModules.WEASEL.MessageWindow  as messageWindow
import CoreModules.WEASEL.InterfaceDICOMXMLFile  as interfaceDICOMXMLFile
from Developer.WEASEL.ScientificLibrary.imagingTools import formatArrayForAnalysis, unWrapPhase
from Developer.WEASEL.ScientificLibrary.ukrinAlgorithms import ukrinMaps

FILE_SUFFIX = '_B0Map'
# THE ENHANCED MRI B0 STILL NEEDS MORE TESTING. I DON'T HAVE ANY CASE WITH 2 TEs IN ENHANCED MRI


def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True


def returnPixelArray(imagePathList, sliceList, echoList):
    """Returns the B0 Map Array with the Phase images as starting point"""
    try:
        if os.path.exists(imagePathList[0]):
            dataset = readDICOM_Image.getDicomDataset(imagePathList[0])
            if hasattr(dataset, 'PerFrameFunctionalGroupsSequence'): # For Enhanced MRI, sliceList is a list of indices
                volumeArray, sliceList, numberSlices = readDICOM_Image.getMultiframeBySlices(dataset, sliceList=sliceList, sort=True)
            else: # For normal DICOM, slicelist is a list of slice locations in mm.
                volumeArray = readDICOM_Image.returnSeriesPixelArray(imagePathList)
                numberSlices = len(np.unique(sliceList))
            # The echo values repeat, so this is to remove all values=0 and repetitions
            echoList = np.delete(np.unique(echoList), np.where(np.unique(echoList) == 0.0))
            pixelArray = formatArrayForAnalysis(volumeArray, numberSlices, dataset, dimension='4D')
            # Algorithm
            derivedImage = ukrinMaps(pixelArray).B0Map(echoList)
            del volumeArray, pixelArray, numberSlices, dataset, echoList
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
                numberSlices = len(np.unique(sliceList))
            # The echo values repeat, so this is to remove all values=0 and repetitions
            echoList = np.delete(np.unique(echoList), np.where(np.unique(echoList) == 0.0))
            volumeArray = np.arctan2(imaginaryVolumeArray, realVolumeArray)
            pixelArray = formatArrayForAnalysis(volumeArray, numberSlices, dataset, dimension='4D')
            # Algorithm
            derivedImage = ukrinMaps(pixelArray).B0Map(echoList) # Maybe np.invert() to have the same result as the other series
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
                    _, flagPhase, flagReal, flagImaginary, _ = readDICOM_Image.checkImageType(dataset)
                    echo = dataset.MREchoSequence[0].EffectiveEchoTime
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
                    phasePathList = imagePathList
                elif riPathList and echoList:
                    riPathList[0] = imagePathList + riPathList[0]
                    riPathList[1] = imagePathList + riPathList[1]
            else:
                imagePathList, firstSliceList, numberSlices, _ = readDICOM_Image.sortSequenceByTag(imagePathList, "SliceLocation")
                imagePathList, echoList, numberEchoes, indicesSorted = readDICOM_Image.sortSequenceByTag(imagePathList, "EchoTime")
                # After sorting, it needs to update the sliceList
                sliceList = [firstSliceList[index] for index in indicesSorted]
                for index in range(len(imagePathList)):
                    dataset = readDICOM_Image.getDicomDataset(imagePathList[index])
                    echo = echoList[index]
                    _, flagPhase, flagReal, flagImaginary, flagMap = readDICOM_Image.checkImageType(dataset)
                    if (numberEchoes >= 1) and (flagPhase or flagMap) and (re.match(".*b0.*", seriesID.lower()), re.match(".*t2.*", seriesID.lower()) or re.match(".*r2.*", seriesID.lower())):
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
        imagePathList = objWeasel.objXMLReader.getImagePathList(studyID, 
                                                               seriesID)

        messageWindow.displayMessageSubWindow(objWeasel,
            "<H4>Extracting parameters to calculate B0 Map</H4>",
            "Saving B0 Map")
        messageWindow.setMsgWindowProgBarMaxValue(objWeasel, 4)
        messageWindow.setMsgWindowProgBarValue(objWeasel, 1)

        phasePathList, sliceList, echoList, riPathList = getParametersB0Map(imagePathList, seriesID)

        messageWindow.displayMessageSubWindow(objWeasel,
            "<H4>Calculating the B0 Map</H4>",
            "Saving B0 Map")
        messageWindow.setMsgWindowProgBarMaxValue(objWeasel, 4)   
        messageWindow.setMsgWindowProgBarValue(objWeasel, 2)

        if phasePathList:
            B0Image = returnPixelArray(phasePathList, sliceList, echoList)
        elif riPathList:
            if riPathList[0] and riPathList[1]:
                B0Image = returnPixelArrayFromRealIm(riPathList, sliceList, echoList)
                phasePathList = riPathList[0] # Here we're assuming that the saving will be performed based on the Real Images
            else:
                messageWindow.displayMessageSubWindow(objWeasel, "NOT POSSIBLE TO CALCULATE B0 MAP IN THIS SERIES.")
                raise Exception("This series doesn't meet the criteria to calculate B0 Map.")
        else:
            messageWindow.displayMessageSubWindow(objWeasel, "NOT POSSIBLE TO CALCULATE B0 MAP IN THIS SERIES.")
            raise Exception("This series doesn't meet the criteria to calculate B0 Map.")

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
            numImages = (1 if len(np.shape(B0Image)) < 3 else np.shape(B0Image)[0])
            for index in range(numImages):
                B0ImageFilePath = saveDICOM_Image.returnFilePath(phasePathList[index], FILE_SUFFIX)
                B0ImagePathList.append(B0ImageFilePath)
                if numImages==1:
                    B0ImageList.append(B0Image)
                else:
                    B0ImageList.append(B0Image[index, ...])
        
        messageWindow.displayMessageSubWindow(objWeasel,
            "<H4>Saving {} DICOM files for the B0 Map calculated</H4>".format(numImages),
            "Saving B0 Map")
        messageWindow.setMsgWindowProgBarMaxValue(objWeasel,4)
        messageWindow.setMsgWindowProgBarValue(objWeasel,3)
        
        # Save new DICOM series locally
        saveDICOM_Image.saveDicomNewSeries(
            B0ImagePathList, imagePathList, B0ImageList, FILE_SUFFIX)
        newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(objWeasel,
                                                            phasePathList[:len(B0ImagePathList)], 
                                                            B0ImagePathList, FILE_SUFFIX)
        messageWindow.setMsgWindowProgBarValue(objWeasel,4)                                                    
        messageWindow.closeMessageSubWindow(objWeasel)
        displayImageColour.displayMultiImageSubWindow(objWeasel, B0ImagePathList,
                                             studyID, newSeriesID)
        treeView.refreshDICOMStudiesTreeView(objWeasel, newSeriesID)
    except Exception as e:
        print('Error in B0MapDICOM_Image.saveB0MapSeries: ' + str(e))
