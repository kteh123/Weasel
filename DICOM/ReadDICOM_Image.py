"""
Collection of functions that read DICOM files and return meaningful content stored in these files (related to image, colourmap, dates and times, acquisiton, etc.).
"""

import os
import struct
import numpy as np
from datetime import datetime
# from cv2 import data
import pydicom
from nibabel.affines import apply_affine
import logging
logger = logging.getLogger(__name__)


def returnPixelArray(imagePath):
    """This method reads the DICOM file in imagePath and returns the Image/Pixel array"""
    logger.info("ReadDICOM_Image.returnPixelArray called")
    try:
        if os.path.exists(imagePath):
            dataset = getDicomDataset(imagePath)
            pixelArray = getPixelArray(dataset)
            return pixelArray
        else:
            return None
    except Exception as e:
        print('Error in function ReadDICOM_Image.returnPixelArray: ' + str(e))
        logger.exception('Error in ReadDICOM_Image.returnPixelArray: ' + str(e))


def returnAffineArray(imagePath):
    """This method reads the DICOM file in imagePath and returns the Affine/Orientation matrix"""
    logger.info("ReadDICOM_Image.returnAffineArray called")
    try:
        if os.path.exists(imagePath):
            dataset = getDicomDataset(imagePath)
            affineArray = getAffineArray(dataset)
            return affineArray
        else:
            return None
    except Exception as e:
        print('Error in function ReadDICOM_Image.returnAffineArray: ' + str(e))
        logger.exception('Error in ReadDICOM_Image.returnAffineArray: ' + str(e))


def returnSeriesPixelArray(imagePathList):
    """This method reads the DICOM files in imagePathList and 
    returns a list where each element is a DICOM Dataset object/class"""
    logger.info("ReadDICOM_Image.returnSeriesPixelArray called")
    try:
        datasetList = getSeriesDicomDataset(imagePathList)
        imageList = [getPixelArray(dataset) for dataset in datasetList]
        if imageList:
            volumeArray = np.array(imageList)
            del imageList
            return volumeArray
        else:
            del imageList
            return None
    except Exception as e:
        print('Error in function ReadDICOM_Image.returnSeriesPixelArray: ' + str(e))
        logger.exception('Error in ReadDICOM_Image.returnSeriesPixelArray: ' + str(e))


def getMultiframeBySlices(dataset, sliceList=None, sort=False):
    """This method splits and sorts the slices in the variable `dataset`. In this case, `dataset` is an Enhanced DICOM object."""
    try:
        if any(hasattr(dataset, attr) for attr in ['PixelData', 'FloatPixelData', 'DoubleFloatPixelData']) and hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
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
        print('Error in function ReadDICOM_Image.getMultiframeBySlices: ' + str(e))
        logger.exception('Error in ReadDICOM_Image.getMultiframeBySlices: ' + str(e))


def getImageTagValue(imagePath, dicomTag):
    """This method reads the DICOM file in imagePath and returns the value in the given DICOM tag
        Output is : attribute
    """
    logger.info("ReadDICOM_Image.getImageTagValue called")
    try:
        if os.path.exists(imagePath):
            dataset = getDicomDataset(imagePath)
            # The following if statement is an exception for Multi-frame / Enhanced DICOM images (13/08/2021)
            if (dicomTag == "SliceLocation" or dicomTag == (0x0020,0x1041)) and not hasattr(dataset, "SliceLocation"): dicomTag = (0x2001, 0x100a)
            # This is not for Enhanced MRI. Only Classic DICOM
            if isinstance(dicomTag, str):
                try:
                    attribute = dataset.data_element(dicomTag).value
                    if dataset.data_element(dicomTag).VR == "TM":
                        if "." in attribute: attribute = (datetime.strptime(attribute, "%H%M%S.%f") - datetime(1900, 1, 1)).total_seconds()
                        else: attribute = (datetime.strptime(attribute, "%H%M%S") - datetime(1900, 1, 1)).total_seconds()
                except:
                    return None
            elif isinstance(dicomTag, tuple):
                try:
                    attribute = dataset[dicomTag].value
                    if dataset[dicomTag].VR == "TM": 
                        if "." in attribute: attribute = (datetime.strptime(attribute, "%H%M%S.%f") - datetime(1900, 1, 1)).total_seconds()
                        else: attribute = (datetime.strptime(attribute, "%H%M%S") - datetime(1900, 1, 1)).total_seconds()
                except:
                    return None
            else:
                try:
                    attribute = dataset[hex(dicomTag)].value
                    if dataset[hex(dicomTag)].VR == "TM":
                        if "." in attribute: attribute = (datetime.strptime(attribute, "%H%M%S.%f") - datetime(1900, 1, 1)).total_seconds()
                        else: attribute = (datetime.strptime(attribute, "%H%M%S") - datetime(1900, 1, 1)).total_seconds()
                except:
                    return None
            del dataset
            return attribute
        else:
            return None
    except Exception as e:
        print('Error in function ReadDICOM_Image.getImageTagValue: ' + str(e))
        logger.exception('Error in ReadDICOM_Image.getImageTagValue: ' + str(e))


def getSeriesTagValues(imagePathList, dicomTag):
    """This method reads the DICOM files in imagePathList and returns the list of values in the given DICOM tag
        Outputs are : attributeList, numAttribute
        The output attributeList may have repeated values. 
        Removing these repetitions will be up to the developer of the specific algorithm
    """
    logger.info("ReadDICOM_Image.getSeriesTagValues called")
    try:
        if os.path.exists(imagePathList[0]):
            datasetList = getSeriesDicomDataset(imagePathList)
            # The following if statement is an exception for Multi-frame / Enhanced DICOM images (13/08/2021)
            if (dicomTag == "SliceLocation" or dicomTag == (0x0020,0x1041)) and not hasattr(datasetList[0], "SliceLocation"): dicomTag = (0x2001, 0x100a)
            if not hasattr(datasetList[0], 'PerFrameFunctionalGroupsSequence'):
                # Classic DICOM
                if isinstance(dicomTag, str):
                    try:
                        attributeList = [dataset.data_element(dicomTag).value for dataset in datasetList]
                        if datasetList[0].data_element(dicomTag).VR == "TM": 
                            if "." in attributeList[0]: attributeList = [(datetime.strptime(attr, "%H%M%S.%f") - datetime(1900, 1, 1)).total_seconds() for attr in attributeList]
                            else: attributeList = [(datetime.strptime(attr, "%H%M%S") - datetime(1900, 1, 1)).total_seconds() for attr in attributeList]
                    except:
                        return None, None
                elif isinstance(dicomTag, tuple):
                    try:
                        attributeList = [dataset[dicomTag].value for dataset in datasetList]
                        if datasetList[0][dicomTag].VR == "TM": 
                            if "." in attributeList[0]: attributeList = [(datetime.strptime(attr, "%H%M%S.%f") - datetime(1900, 1, 1)).total_seconds() for attr in attributeList]
                            else: attributeList = [(datetime.strptime(attr, "%H%M%S") - datetime(1900, 1, 1)).total_seconds() for attr in attributeList]
                    except:
                        return None, None
                else:
                    try:
                        attributeList = [dataset[hex(dicomTag)].value for dataset in datasetList]
                        if datasetList[0][hex(dicomTag)].VR == "TM":
                            if "." in attributeList[0]: attributeList = [(datetime.strptime(attr, "%H%M%S.%f") - datetime(1900, 1, 1)).total_seconds() for attr in attributeList]
                            else: attributeList = [(datetime.strptime(attr, "%H%M%S") - datetime(1900, 1, 1)).total_seconds() for attr in attributeList]
                    except:
                        return None, None
                attributeList = [0 if x is None else x for x in attributeList]
                attributeListUnique = []
                for x in attributeList:
                    if x not in attributeListUnique:
                        attributeListUnique.append(x)
                numAttribute = len(attributeListUnique)
                del datasetList
                return attributeList, numAttribute
            else:
                # Enhanced MRI => This else will probably never happen, because this type of DICOM is converted at Import (13/08/2021)
                dataset = datasetList[0]
                attributeList = []
                fields = dicomTag.split('.')
                if len(fields) == 1:
                    if isinstance(dicomTag, str):
                        try:
                            attributeList = [dataset.data_element(dicomTag).value for dataset in datasetList]
                            if datasetList[0].data_element(dicomTag).VR == "TM": attributeList = [(datetime.strptime(attr, "%H%M%S") - datetime(1900, 1, 1)).total_seconds() for attr in attributeList]
                        except:
                            return None, None
                    elif isinstance(dicomTag, tuple):
                        try:
                            attributeList = [dataset[dicomTag].value for dataset in datasetList]
                            if datasetList[0][dicomTag].VR == "TM": attributeList = [(datetime.strptime(attr, "%H%M%S") - datetime(1900, 1, 1)).total_seconds() for attr in attributeList]
                        except:
                            return None, None
                    else:
                        try:
                            attributeList = [dataset[hex(dicomTag)].value for dataset in datasetList]
                            if datasetList[0][hex(dicomTag)].VR == "TM": attributeList = [(datetime.strptime(attr, "%H%M%S") - datetime(1900, 1, 1)).total_seconds() for attr in attributeList]
                        except:
                            return None, None
                elif fields[0] == "PerFrameFunctionalGroupsSequence":
                    remaining_fields = ""
                    for field in fields[1:-1]:
                        remaining_fields += "." + str(field) + "[0]"
                    remaining_fields += "." + fields[-1]
                    for singleSlice in dataset.PerFrameFunctionalGroupsSequence:
                        pyDicom_command_string = "singleSlice" + remaining_fields
                        attributeList.append(eval(pyDicom_command_string))
                else:
                    # These seem to be the only options for now
                    return None, None
                attributeList = [0 if x is None else x for x in attributeList]
                attributeListUnique = []
                for x in attributeList:
                    if x not in attributeListUnique:
                        attributeListUnique.append(x)
                numAttribute = len(attributeListUnique)
                # numAttribute = len(np.unique(attributeList))
                del dataset, datasetList, fields
                return attributeList, numAttribute
        else:
            return None, None
    except Exception as e:
        print('Error in function ReadDICOM_Image.getSeriesTagValues: ' + str(e))
        logger.exception('Error in ReadDICOM_Image.getSeriesTagValues: ' + str(e))


def sortSequenceByTag(imagePathList, dicomTag):
    """This method reads the DICOM files in imagePathList and sorts the list according to the given DICOM tag
        Outputs are : sortedSequencePath, attributeList, numAttribute
        The output attributeList may have repeated values. 
        Removing these repetitions will be up to the developer of the specific algorithm
    """
    logger.info("ReadDICOM_Image.sortSequenceByTag called")
    try:
        if os.path.exists(imagePathList[0]):
            attributeList, numAttribute = getSeriesTagValues(imagePathList, dicomTag)
            #attributeListUnique = np.unique(attributeList) # sorted(np.unique(attributeList))
            attributeListUnique = [] # Works for strings as well, unlike np.unique
            for x in attributeList:
                if x not in attributeListUnique:
                    attributeListUnique.append(x)
            attributeListUnique = [0 if x is None else x for x in attributeListUnique]
            indicesSorted = list()
            for i in range(numAttribute):
                indices = [index for index, value in enumerate(attributeList) if value == attributeListUnique[i]]
                indicesSorted.extend(indices)
            # If/Else regarding Multi-Frame DICOM
            dataset = getDicomDataset(imagePathList[0])
            if not hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
                sortedSequencePath = [imagePathList[index] for index in indicesSorted]
            else:
                sortedSequencePath = imagePathList
            attributeListSorted = [attributeList[index] for index in indicesSorted]
            del dataset, attributeList, attributeListUnique
            return sortedSequencePath, attributeListSorted, numAttribute, indicesSorted
        else:
            return None, None, None, None
    except Exception as e:
        print('Error in function ReadDICOM_Image.sortSequenceByTag: ' + str(e))
        logger.exception('Error in ReadDICOM_Image.sortSequenceByTag: ' + str(e))


def getSeriesDicomDataset(imagePathList):
    """This method reads the DICOM files in imagePathList and 
    returns a list where each element is a DICOM Dataset object/class"""
    logger.info("ReadDICOM_Image.getSeriesDicomDataset called")
    try:
        #datasetList = [getDicomDataset(imagePath) for imagePath in imagePathList if getDicomDataset(imagePath) is not None]
        datasetList = []
        for imagePath in imagePathList:
            dataset = getDicomDataset(imagePath)
            if dataset is not None:
                datasetList.append(dataset)
        if datasetList:
            return datasetList
        else:
            return None
    except Exception as e:
        print('Error in function ReadDICOM_Image.getSeriesDicomDataset: ' + str(e))
        logger.exception('Error in ReadDICOM_Image.getSeriesDicomDataset: ' + str(e))


def getDicomDataset(imagePath):
    """This method reads the DICOM file in imagePath and returns the DICOM Dataset object/class"""
    logger.info("ReadDICOM_Image.getDicomDataset called")
    try:
        if os.path.exists(imagePath):
            return pydicom.dcmread(imagePath)
        else:
            return None
    except Exception as e:
        print('Error in function ReadDICOM_Image.getDicomDataset when imagePath = {}: '.format(imagePath) + str(e))
        logger.exception('Error in ReadDICOM_Image.getDicomDataset: ' + str(e))


def getPixelArray(dataset):
    """This method reads the DICOM Dataset object/class and returns the Image/Pixel array"""
    logger.info("ReadDICOM_Image.getPixelArray called")
    try:
        if any(hasattr(dataset, attr) for attr in ['PixelData', 'FloatPixelData', 'DoubleFloatPixelData']):
            if hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
                imageList = list()
                originalArray = dataset.pixel_array.astype(np.float32)
                if len(np.shape(originalArray)) == 2:
                    slope = float(getattr(dataset.PerFrameFunctionalGroupsSequence[0].PixelValueTransformationSequence[0], 'RescaleSlope', 1)) * np.ones(originalArray.shape)
                    intercept = float(getattr(dataset.PerFrameFunctionalGroupsSequence[0].PixelValueTransformationSequence[0], 'RescaleIntercept', 0)) * np.ones(originalArray.shape)
                    pixelArray = np.transpose(originalArray * slope + intercept)
                else:
                    for index in range(np.shape(originalArray)[0]):
                        sliceArray = np.squeeze(originalArray[index, ...])
                        slope = float(getattr(dataset.PerFrameFunctionalGroupsSequence[index].PixelValueTransformationSequence[0], 'RescaleSlope', 1)) * np.ones(sliceArray.shape)
                        intercept = float(getattr(dataset.PerFrameFunctionalGroupsSequence[index].PixelValueTransformationSequence[0], 'RescaleIntercept', 0)) * np.ones(sliceArray.shape)
                        tempArray = np.transpose(sliceArray * slope + intercept)
                        imageList.append(tempArray)
                    pixelArray = np.array(imageList)
                    del sliceArray, tempArray, index
                del originalArray, imageList
            else:
                slope = float(getattr(dataset, 'RescaleSlope', 1)) * np.ones(dataset.pixel_array.shape)
                intercept = float(getattr(dataset, 'RescaleIntercept', 0)) * np.ones(dataset.pixel_array.shape)
                if len(dataset.pixel_array.shape) == 3:
                    pixelArray = np.rot90(np.array(dataset.pixel_array.astype(np.float32) * slope + intercept), k=1, axes=(0, 1))
                else:
                    pixelArray = np.transpose(dataset.pixel_array.astype(np.float32) * slope + intercept)
            if [0x2005, 0x100E] in dataset: # 'Philips Rescale Slope'
                pixelArray = pixelArray / (slope * dataset[(0x2005, 0x100E)].value)
            del slope, intercept
            return pixelArray
        else:
            return None
    except Exception as e:
        print('Error in function ReadDICOM_Image.getPixelArray: ' + str(e))
        logger.exception('Error in ReadDICOM_Image.getPixelArray: ' + str(e))


def getAffineArray(dataset):
    """This method reads the DICOM Dataset object/class and returns the Affine/Orientation matrix"""
    logger.info("ReadDICOM_Image.getAffineArray called")
    try:
        if any(hasattr(dataset, attr) for attr in ['PixelData', 'FloatPixelData', 'DoubleFloatPixelData']):
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
        print('Error in function ReadDICOM_Image.getAffineArray: ' + str(e))
        logger.exception('Error in ReadDICOM_Image.getAffineArray: ' + str(e))


def mapMaskToImage(mask, datasetMask, datasetTarget):
    """This method takes a binary mask pixel_array and returns a list of indexes
        of the True values of the mask in the coordinate system of the `datasetTarget`"""
    logger.info("ReadDICOM_Image.mapMaskToImage called")
    try:
        affineTarget = getAffineArray(datasetTarget)
        affineMask = getAffineArray(datasetMask)
        indexes = np.transpose(np.where(mask==1))
        if np.shape(indexes) == (0,2):
            listIndexes = []
        else:
            listIndexes = mapCoordinates(indexes, affineTarget, affineMask)
        return listIndexes
    except Exception as e:
        print('Error in function ReadDICOM_Image.mapMaskToImage: ' + str(e))
        logger.exception('Error in ReadDICOM_Image.mapMaskToImage: ' + str(e))

def mapCoordinates(indexes, affineTarget, affineMask):
    """This method returns a list of indexes that results from mapping the input argument 
        `indexes` to the coordinate system of the target image.
    """
    logger.info("ReadDICOM_Image.mapCoordinates called")
    try:
        coords = [[index[0], index[1], 0] for index in indexes]
        newCoord = np.round(applyAffine(affineTarget, affineMask, np.array(coords)), 3).astype(int)
        return [(coord[1], coord[0]) for coord in newCoord if coord[-1] == 0]

        # Legacy code that might be needed if we move to 3D
        #if len(index) == 2: 
        #coords = [[index[0], index[1], 0] for index in indexes]
        #else:
        #temp_index = np.array([index[1], index[2], index[0]])
        #if (len(index) == 2) and (newCoord[-1] == 0):
        #    return (newCoord[1], newCoord[0])
        #elif len(index) == 3:
        #    return (newCoord[-1], newCoord[1], newCoord[0])
    except Exception as e:
        print('Error in function ReadDICOM_Image.mapCoordinates: ' + str(e))
        logger.exception('Error in ReadDICOM_Image.mapCoordinates: ' + str(e))


def applyAffine(affineReference, affineTarget, coordinates):
    """This method uses the affines from the reference image and from the target image and 
        calculates the new spatial values of the `coordinates` input argument in the target image coordinate system."""
    logger.info("ReadDICOM_Image.applyAffine called")
    try:
        maskToTarget = np.linalg.inv(affineReference).dot(affineTarget)
        return apply_affine(maskToTarget, coordinates)
    except Exception as e:
        print('Error in function ReadDICOM_Image.applyAffine: ' + str(e))
        logger.exception('Error in ReadDICOM_Image.applyAffine: ' + str(e))


def getColourmap(imagePath):
    """This method reads the DICOM file in imagePath and returns the colourmap if there's any"""
    logger.info("ReadDICOM_Image.getColourmap called")
    try:
        dataset = getDicomDataset(imagePath)
        if hasattr(dataset, 'ContentLabel'):
            if dataset.PhotometricInterpretation == 'PALETTE COLOR':
                colourmapName = dataset.ContentLabel
            elif 'MONOCHROME' in dataset.PhotometricInterpretation:
                colourmapName = 'gray'
            else:
                colourmapName = None
        else:
            colourmapName = None
        if len(dataset.dir("PaletteColor"))>=3 and dataset.PhotometricInterpretation == 'PALETTE COLOR':
            if colourmapName is None:
                colourmapName = 'custom'
            redColour = list(dataset.RedPaletteColorLookupTableData)
            greenColour = list(dataset.GreenPaletteColorLookupTableData)
            blueColour = list(dataset.BluePaletteColorLookupTableData)
            redLut = list(struct.unpack('<' + ('H' * dataset.RedPaletteColorLookupTableDescriptor[0]), bytearray(redColour)))
            greenLut = list(struct.unpack('<' + ('H' * dataset.GreenPaletteColorLookupTableDescriptor[0]), bytearray(greenColour)))
            blueLut = list(struct.unpack('<' + ('H' * dataset.BluePaletteColorLookupTableDescriptor[0]), bytearray(blueColour)))
            colours = np.transpose([redLut, greenLut, blueLut])
            normaliseFactor = int(np.power(2, dataset.RedPaletteColorLookupTableDescriptor[2]))
            # Fast ColourTable loading
            colourTable = np.around(colours/normaliseFactor, decimals = 2)
            indexes = np.unique(colourTable, axis=0, return_index=True)[1]
            lut = [colourTable[index].tolist() for index in sorted(indexes)]
            # Full / Complete Colourmap - takes 20 seconds to load each image
            # lut = (colours/normaliseFactor).tolist()
        else:
            lut = None
        return colourmapName, lut
    except Exception as e:
        print('Error in function ReadDICOM_Image.getColourmap: ' + str(e))
        logger.exception('Error in ReadDICOM_Image.getColourmap: ' + str(e))
    

def checkImageType(dataset):
    """This method reads the DICOM Dataset object/class and returns if it is a Magnitude, Phase, Real or Imaginary image or None"""
    logger.info("ReadDICOM_Image.checkImageType called")
    try:
        mapsList = ['ADC', 'FA', 'B0', 'B0 MAP', 'B0_MAP', 'T1', 'T1 MAP', 'T1_MAP', 'T2', 'T2 MAP', 'T2_MAP', 'T2_STAR', 'T2_STAR MAP', 'T2_STAR_MAP', 'MAP', 'FIELD_MAP']
        if hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
            flagMagnitude = []
            flagPhase = []
            flagReal = []
            flagImaginary = []
            flagMap = []
            for index, singleSlice in enumerate(dataset.PerFrameFunctionalGroupsSequence):
                if hasattr(singleSlice.MRImageFrameTypeSequence[0], 'FrameType'):
                    if set(['M', 'MAGNITUDE']).intersection(set(singleSlice.MRImageFrameTypeSequence[0].FrameType)):
                        flagMagnitude.append(index)
                        continue
                    elif set(['P', 'PHASE']).intersection(set(singleSlice.MRImageFrameTypeSequence[0].FrameType)):
                        flagPhase.append(index)
                        continue
                    elif set(['R', 'REAL']).intersection(set(singleSlice.MRImageFrameTypeSequence[0].FrameType)):
                        flagReal.append(index)
                        continue
                    elif set(['I', 'IMAGINARY']).intersection(set(singleSlice.MRImageFrameTypeSequence[0].FrameType)):
                        flagImaginary.append(index)
                        continue
                    elif set(mapsList).intersection(set(singleSlice.MRImageFrameTypeSequence[0].FrameType)):
                        flagMap.append(list(set(mapsList).intersection(set(singleSlice.MRImageFrameTypeSequence[0].FrameType)))[0])
                        continue
                if hasattr(singleSlice.MRImageFrameTypeSequence[0], 'ComplexImageComponent'):
                    if set(['M', 'MAGNITUDE']).intersection(set(singleSlice.MRImageFrameTypeSequence[0].ComplexImageComponent)):
                        flagMagnitude.append(index)
                        continue
                    elif set(['P', 'PHASE']).intersection(set(singleSlice.MRImageFrameTypeSequence[0].ComplexImageComponent)):
                        flagPhase.append(index)
                        continue
                    elif set(['R', 'REAL']).intersection(set(singleSlice.MRImageFrameTypeSequence[0].ComplexImageComponent)):
                        flagReal.append(index)
                        continue
                    elif set(['I', 'IMAGINARY']).intersection(set(singleSlice.MRImageFrameTypeSequence[0].ComplexImageComponent)):
                        flagImaginary.append(index)
                        continue
                    elif set(mapsList).intersection(set(singleSlice.MRImageFrameTypeSequence[0].ComplexImageComponent)):
                        flagMap.append(list(set(mapsList).intersection(set(singleSlice.MRImageFrameTypeSequence[0].ComplexImageComponent)))[0])
                        continue
        else:
            flagMagnitude = False
            flagPhase = False
            flagReal = False
            flagImaginary = False
            flagMap = False
            try: private_ge = dataset[0x0043102f]
            except: private_ge = None
            if private_ge is not None: #MAG = 0; PHASE = 1; REAL = 2; IMAG = 3; # RawDataType_ImageType in GE - '0x0043102f'
                try:
                    if struct.unpack('h', private_ge.value)[0] == 0:
                        flagMagnitude = True
                    elif struct.unpack('h', private_ge.value)[0] == 1:
                        flagPhase = True
                    elif struct.unpack('h', private_ge.value)[0] == 2:
                        flagReal = True
                    elif struct.unpack('h', private_ge.value)[0] == 3:
                        flagImaginary = True
                except:
                    if private_ge.value == 0:
                        flagMagnitude = True
                    elif private_ge.value == 1:
                        flagPhase = True
                    elif private_ge.value == 2:
                        flagReal = True
                    elif private_ge.value == 3:
                        flagImaginary = True
            if hasattr(dataset, 'ImageType'):
                if set(['M', 'MAGNITUDE']).intersection(set(dataset.ImageType)):
                    flagMagnitude = True
                elif set(['P', 'PHASE']).intersection(set(dataset.ImageType)):# or ('B0' in dataset.ImageType) or ('FIELD_MAP' in dataset.ImageType):
                    flagPhase = True
                elif set(['R', 'REAL']).intersection(set(dataset.ImageType)):
                    flagReal = True
                elif set(['I', 'IMAGINARY']).intersection(set(dataset.ImageType)):
                    flagImaginary = True
                elif set(mapsList).intersection(set(dataset.ImageType)):
                    flagMap = list(set(mapsList).intersection(set(dataset.ImageType)))[0]
            if flagMagnitude == False and flagPhase == False and flagReal == False and \
               flagImaginary == False and flagMap == False and hasattr(dataset, 'ComplexImageComponent'):
                if dataset.ComplexImageComponent == 'MAGNITUDE':
                    flagMagnitude = True
                elif dataset.ComplexImageComponent == 'PHASE':
                    flagPhase = True
                elif dataset.ComplexImageComponent == 'REAL':
                    flagReal = True
                elif dataset.ComplexImageComponent == 'IMAGINARY':
                    flagImaginary = True
        return flagMagnitude, flagPhase, flagReal, flagImaginary, flagMap
    except Exception as e:
        print('Error in function ReadDICOM_Image.checkImageType: ' + str(e))
        logger.exception('Error in ReadDICOM_Image.checkImageType: ' + str(e))


def checkAcquisitionType(dataset):
    """This method reads the DICOM Dataset object/class and returns if it is a Water, Fat, In-Phase, Out-phase image or None"""
    logger.info("ReadDICOM_Image.checkImageType called")
    try:
        flagWater = False
        flagFat = False
        flagInPhase = False
        flagOutPhase = False
        if hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
            if hasattr(dataset.MRImageFrameTypeSequence[0], 'FrameType'):
                if set(['W', 'WATER']).intersection(set(dataset.MRImageFrameTypeSequence[0].FrameType)):
                    flagWater = True
                elif set(['F', 'FAT']).intersection(set(dataset.MRImageFrameTypeSequence[0].FrameType)):
                    flagFat = True
                elif set(['IP', 'IN_PHASE']).intersection(set(dataset.MRImageFrameTypeSequence[0].FrameType)):
                    flagInPhase = True
                elif set(['OP', 'OUT_PHASE']).intersection(set(dataset.MRImageFrameTypeSequence[0].FrameType)):
                    flagOutPhase = True
            elif hasattr(dataset.MRImageFrameTypeSequence[0], 'ComplexImageComponent'):
                if set(['W', 'WATER']).intersection(set(dataset.MRImageFrameTypeSequence[0].ComplexImageComponent)):
                    flagWater = True
                elif set(['F', 'FAT']).intersection(set(dataset.MRImageFrameTypeSequence[0].ComplexImageComponent)):
                    flagFat = True
                elif set(['IP', 'IN_PHASE']).intersection(set(dataset.MRImageFrameTypeSequence[0].ComplexImageComponent)):
                    flagInPhase = True
                elif set(['OP', 'OUT_PHASE']).intersection(set(dataset.MRImageFrameTypeSequence[0].ComplexImageComponent)):
                    flagOutPhase = True
        else:
            if hasattr(dataset, 'ImageType'):
                if set(['W', 'WATER']).intersection(set(dataset.ImageType)):
                    flagWater = True
                elif set(['F', 'FAT']).intersection(set(dataset.ImageType)):# or ('B0' in dataset.ImageType) or ('FIELD_MAP' in dataset.ImageType):
                    flagFat = True
                elif set(['IP', 'IN_PHASE']).intersection(set(dataset.ImageType)):
                    flagInPhase = True
                elif set(['OP', 'OUT_PHASE']).intersection(set(dataset.ImageType)):
                    flagOutPhase = True
        return flagWater, flagFat, flagInPhase, flagOutPhase
    except Exception as e:
        print('Error in function ReadDICOM_Image.checkAcquisitionType: ' + str(e))
        logger.exception('Error in ReadDICOM_Image.checkAcquisitionType: ' + str(e))
