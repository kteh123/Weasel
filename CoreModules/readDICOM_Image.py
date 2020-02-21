import pydicom
import os
import numpy as np

def returnPixelArray(imagePath):
    """This method reads the DICOM file in imagePath and returns the Image/Pixel array"""
    try:
        if os.path.exists(imagePath):
            dataset = getDicomDataset(imagePath)
            pixelArray = getPixelArray(dataset)
            return pixelArray
        else:
            return None
    except Exception as e:
        print('Error in function readDICOM_Image.returnPixelArray: ' + str(e))


def returnAffineArray(imagePath):
    """This method reads the DICOM file in imagePath and returns the Affine/Orientation matrix"""
    try:
        if os.path.exists(imagePath):
            dataset = getDicomDataset(imagePath)
            affineArray = getAffineArray(dataset)
            return affineArray
        else:
            return None
    except Exception as e:
        print('Error in function readDICOM_Image.returnAffineArray: ' + str(e))


def returnSeriesPixelArray(imagePathList):
    """This method reads the DICOM files in imagePathList and 
    returns a list where each element is a DICOM Dataset object/class"""
    try:
        datasetList = getSeriesDicomDataset(imagePathList)
        imageList = list()
        for dataset in datasetList:
            imageList.append(getPixelArray(dataset))
        if imageList:
            volumeArray = np.array(imageList)
            del imageList
            return volumeArray
        else:
            del imageList
            return None
    except Exception as e:
        print('Error in function readDICOM_Image.getDicomDataset: ' + str(e))


def getMultiframeBySlices(dataset, sliceList=None, sort=False):
    try:
        if hasattr(dataset, 'PixelData') and hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
            originalArray = getPixelArray(dataset)
            numberSlices = dataset[0x20011018].value
            sortedArray = list()
            sortedSlicesList = list()
            if sliceList is None:
                numberFrames = dataset.NumberOfFrames
            else:
                numberFrames = len(sliceList)
            
            if (sort == True):
                if '2D' in dataset.MRAcquisitionType:
                    for start in range(int(numberFrames/numberSlices)):
                        sortedSlicesList.append(list(range(start, numberFrames, int(numberFrames/numberSlices))))
                    sortedSlicesList = np.array(sortedSlicesList).flatten()
                elif '3D' in dataset.MRAcquisitionType:
                    sortedSlicesList = list(range(numberFrames))
            elif (sort == False) and ((type(sliceList) is list) or (type(sliceList) is np.array)):
                sortedSlicesList = sliceList
            else:
                sortedSlicesList = list(range(numberFrames))
                
            for index in sortedSlicesList:
                sortedArray.append(np.squeeze(originalArray[index, ...]))
            sortedArray = np.array(sortedArray)
            return sortedArray, sortedSlicesList, numberSlices
        else:
            return None, None, None
    except Exception as e:
        print('Error in function readDICOM_Image.getMultiframeBySlices: ' + str(e))


def sortSequenceByTag(imagePathList, dicomTag):
    """This method reads the DICOM files in imagePathList and sorts the list according to the given DICOM tag"""
    try:
        if os.path.exists(imagePathList[0]):
            datasetList = getSeriesDicomDataset(imagePathList)
            if hasattr(datasetList[0], 'PerFrameFunctionalGroupsSequence'):
                #Enhanced MRI
                sortedSequencePathAux = list()
                sortedSequenceAux = list()
                sortedSequencePath = imagePathList[0]
                sortedSequence = datasetList[0]
                numAttribute = datasetList[0][0x20011018].value #NumberOfSlicesMR for Philips Enhanced MRI
            else:
                attributeList = list()
                sortedSequencePathAux = list()
                sortedSequenceAux = list()
                sortedSequencePath = imagePathList
                sortedSequence = datasetList
                [attributeList.append(float(dataset.data_element(str(dicomTag)).value)) for dataset in datasetList]
                attributeList = np.unique(attributeList)
                attributeList.sort()
                [sortedSequencePathAux.append(imagePathList[indexAux]) for attributeValue in attributeList for indexAux, dataset in enumerate(datasetList) if float(dataset.data_element(str(dicomTag)).value) == attributeValue]
                [sortedSequenceAux.append(dataset) for attributeValue in attributeList for dataset in datasetList if float(dataset.data_element(str(dicomTag)).value) == attributeValue]
                numAttribute = len(attributeList)
                #At this point, it's sorted as 111222333. The next step will sort the values in the format 123123123
                repetition = 0
                index = 0
                for indexAux, image in enumerate(sortedSequenceAux):
                    sortedSequence[index] = image
                    sortedSequencePath[index] = sortedSequencePathAux[indexAux]
                    index += numAttribute
                    if index > len(sortedSequence)-1:
                        repetition += 1
                        if repetition > numAttribute:
                            break
                        else:
                            index = repetition
                            
                del datasetList, sortedSequencePathAux, sortedSequenceAux, sortedSequence
                return sortedSequencePath, attributeList, numAttribute
        else:
            return None, None, None
    except Exception as e:
        print('Error in function readDICOM_Image.sortSequenceByTag: ' + str(e))


def getSeriesDicomDataset(imagePathList):
    """This method reads the DICOM files in imagePathList and 
    returns a list where each element is a DICOM Dataset object/class"""
    try:
        datasetList = list()
        for imagePath in imagePathList:
            datasetList.append(getDicomDataset(imagePath))
        if datasetList:
            return datasetList
        else:
            return None
    except Exception as e:
        print('Error in function readDICOM_Image.getDicomDataset: ' + str(e))


def getDicomDataset(imagePath):
    """This method reads the DICOM file in imagePath and returns the DICOM Dataset object/class"""
    try:
        if os.path.exists(imagePath):
            dataset = pydicom.dcmread(imagePath)
            return dataset
        else:
            return None
    except Exception as e:
        print('Error in function readDICOM_Image.getDicomDataset: ' + str(e))


def getPixelArray(dataset):
    """This method reads the DICOM Dataset object/class and returns the Image/Pixel array"""
    try:
        if hasattr(dataset, 'PixelData'):
            if hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
                imageList = list()
                originalArray = dataset.pixel_array.astype(np.float32)
                if len(np.shape(originalArray))==2:
                    slope = float(getattr(dataset.PerFrameFunctionalGroupsSequence[0].PixelValueTransformationSequence[0], 'RescaleSlope', 1)) * np.ones(originalArray.shape)
                    intercept = float(getattr(dataset.PerFrameFunctionalGroupsSequence[0].PixelValueTransformationSequence[0], 'RescaleIntercept', 0)) * np.ones(originalArray.shape)
                    pixelArray = originalArray * slope + intercept
                else:
                    for index in range(np.shape(originalArray)[0]):
                        sliceArray = np.squeeze(originalArray[index, ...])
                        slope = float(getattr(dataset.PerFrameFunctionalGroupsSequence[index].PixelValueTransformationSequence[0], 'RescaleSlope', 1)) * np.ones(sliceArray.shape)
                        intercept = float(getattr(dataset.PerFrameFunctionalGroupsSequence[index].PixelValueTransformationSequence[0], 'RescaleIntercept', 0)) * np.ones(sliceArray.shape)
                        tempArray = sliceArray * slope + intercept
                        imageList.append(tempArray)
                    pixelArray = np.array(imageList)
                    del sliceArray, tempArray, index
                del originalArray
            else:
                slope = float(getattr(dataset, 'RescaleSlope', 1)) * np.ones(dataset.pixel_array.shape)
                intercept = float(getattr(dataset, 'RescaleIntercept', 0)) * np.ones(dataset.pixel_array.shape)
                pixelArray = dataset.pixel_array.astype(np.float32) * slope + intercept
            del slope, intercept
            return pixelArray
        else:
            return None
    except Exception as e:
        print('Error in function readDICOM_Image.getPixelArray: ' + str(e))


def getAffineArray(dataset):
    """This method reads the DICOM Dataset object/class and returns the Affine/Orientation matrix"""
    try:
        if hasattr(dataset, 'PixelData'):
            if hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
                affineList = list()
                for index in range(len(dataset.PerFrameFunctionalGroupsSequence)):
                    image_orientation = dataset.PerFrameFunctionalGroupsSequence[index].PlaneOrientationSequence[0].ImageOrientationPatient
                    row_cosine = np.array(image_orientation[:3])
                    column_cosine = np.array(image_orientation[3:])
                    slice_cosine = np.cross(row_cosine, column_cosine)
                    row_spacing, column_spacing = dataset.PerFrameFunctionalGroupsSequence[index].PixelMeasuresSequence[0].PixelSpacing
                    slice_spacing = dataset.PerFrameFunctionalGroupsSequence[index].PixelMeasuresSequence[0].SpacingBetweenSlices

                    affine = np.identity(4, dtype=np.float32)
                    affine[:3, 0] = row_cosine * column_spacing
                    affine[:3, 1] = column_cosine * row_spacing
                    affine[:3, 2] = slice_cosine * slice_spacing
                    affine[:3, 3] = dataset.PerFrameFunctionalGroupsSequence[index].PlanePositionSequence[0].ImagePositionPatient
                    affineList.append(affine)
                affine = np.squeeze(np.array(affineList))
            else:
                image_orientation = dataset.ImageOrientationPatient
                row_cosine = np.array(image_orientation[:3])
                column_cosine = np.array(image_orientation[3:])
                slice_cosine = np.cross(row_cosine, column_cosine)
                row_spacing, column_spacing = dataset.PixelSpacing
                slice_spacing = dataset.SliceThickness

                affine = np.identity(4, dtype=np.float32)
                affine[:3, 0] = row_cosine * column_spacing
                affine[:3, 1] = column_cosine * row_spacing
                affine[:3, 2] = slice_cosine * slice_spacing
                affine[:3, 3] = dataset.ImagePositionPatient
            return affine
        else:
            return None
    except Exception as e:
        print('Error in function readDICOM_Image.getAffineArray: ' + str(e))