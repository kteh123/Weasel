import os
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.sequence import Sequence
from pydicom.datadict import dictionary_VR
import datetime
import copy
import random
from matplotlib import cm
import CoreModules.WEASEL.ReadDICOM_Image as ReadDICOM_Image
import CoreModules.WEASEL.ParametricMapsDictionary as param
import CoreModules.WEASEL.MessageWindow as messageWindow
import logging

logger = logging.getLogger(__name__)


def returnFilePath(imagePath, suffix, new_path=None, output_folder=None):
    """This method returns the new filepath of the object to be saved."""
    # Think of a way to choose a select a new FilePath
    try:
        if os.path.exists(imagePath):
            # Need to think about what new name to give to the file and how to save multiple files for the same sequence
            if new_path is not None:
                newFilePath = new_path + '.dcm'
            else:
                if output_folder is None:
                    outputFolder = os.path.join(os.path.dirname(imagePath), "output" + suffix)
                else:
                    outputFolder = output_folder
                fileName = os.path.splitext(os.path.basename(imagePath))[0]
                try: os.mkdir(outputFolder)
                except: pass
                newFilePath = os.path.join(outputFolder, fileName + suffix + '.dcm')
                counter = 1
                if os.path.exists(newFilePath):
                    newFilePath = os.path.join(outputFolder, fileName + suffix + '(' + str(counter) + ')' + '.dcm')
                    counter += 1
            return newFilePath

        else:
            return None
    except Exception as e:
        print('Error in function SaveDICOM_Image.returnFilePath: ' + str(e))


def saveNewSingleDicomImage(newFilePath, imagePath, pixelArray, suffix, series_id=None, series_uid=None, series_name=None, image_number=None, parametric_map=None, colourmap=None, list_refs_path=None):
    """This method saves the new pixelArray into DICOM in the given newFilePath"""
    try:
        if os.path.exists(imagePath):
            dataset = ReadDICOM_Image.getDicomDataset(imagePath)
            if list_refs_path is not None:
                refs = []
                for individualRef in list_refs_path:
                    refs.append(ReadDICOM_Image.getDicomDataset(individualRef))
            else:
                refs = None
            newDataset = createNewSingleDicom(dataset, pixelArray, series_id=series_id, series_uid=series_uid, series_name=series_name, comment=suffix, parametric_map=parametric_map, colourmap=colourmap, list_refs=refs)
            if (image_number is not None) and (len(np.shape(pixelArray)) < 3):
                newDataset.InstanceNumber = image_number
                newDataset.ImageNumber = image_number
            saveDicomToFile(newDataset, output_path=newFilePath)
            del dataset, newDataset, refs, image_number
            return
        else:
            return None

    except Exception as e:
        print('Error in function SaveDICOM_Image.saveNewSingleDicomImage: ' + str(e))


def updateSingleDicomImage(objWeasel, spinBoxIntensity, spinBoxContrast, 
                imagePath='', seriesID='', studyID='', colourmap=None, lut=None):
    try:
        logger.info("In SaveDICOM_Image.updateSingleDicomImage")
        messageWindow.displayMessageSubWindow(objWeasel,
            "<H4>Updating 1 DICOM file</H4>",
            "Updating DICOM images")
        messageWindow.setMsgWindowProgBarMaxValue(objWeasel,1)
        messageWindow.setMsgWindowProgBarValue(objWeasel,0)
        dataset = ReadDICOM_Image.getDicomDataset(imagePath)
        levels = [spinBoxIntensity.value(), spinBoxContrast.value()]
        updatedDataset = updateSingleDicom(dataset, colourmap=colourmap, levels=levels, lut=lut)
        saveDicomToFile(updatedDataset, output_path=imagePath)
        messageWindow.setMsgWindowProgBarValue(objWeasel,1)
        messageWindow.closeMessageSubWindow(objWeasel)
    except Exception as e:
        print('Error in SaveDICOM_Image.updateSingleDicomImage: ' + str(e))


def saveDicomNewSeries(derivedImagePathList, imagePathList, pixelArrayList, suffix, series_id=None, series_uid=None, series_name=None, parametric_map=None, colourmap=None, list_refs_path=None):
    """This method saves the pixelArrayList into DICOM files with metadata pointing to the same series"""
    # What if it's a map with less files than original? Think about iterating the first elements and sort path list by SliceLocation - see T2* algorithm
    # Think of a way to choose a select a new FilePath or Folder
    try:
        if os.path.exists(imagePathList[0]):
            # Series ID and UID
            if (series_id is None) and (series_uid is None):
                ids = generateUIDs(ReadDICOM_Image.getDicomDataset(imagePathList[0]))
                series_id = ids[0]
                series_uid = ids[1]
            elif (series_id is not None) and (series_uid is None):
                series_uid = generateUIDs(ReadDICOM_Image.getDicomDataset(imagePathList[0]), seriesNumber=series_id)[1]
            elif (series_id is None) and (series_uid is not None):
                series_id = int(str(ReadDICOM_Image.getDicomDataset(imagePathList[0]).SeriesNumber) + str(random.randint(0, 9999)))

            refs = None
            for index, newFilePath in enumerate(derivedImagePathList):
                # Extra references, besides the main one, which is imagePathList
                if list_refs_path is not None:
                    if len(np.shape(list_refs_path)) == 1:
                        refs = list_refs_path[index]
                    else:
                        refs = []
                        for individualRef in list_refs_path:
                            refs.append(individualRef[index])

                saveNewSingleDicomImage(newFilePath, imagePathList[index], pixelArrayList[index], suffix, series_id=series_id, series_uid=series_uid, series_name=series_name, image_number=index+1, parametric_map=parametric_map, 
                                      colourmap=colourmap, list_refs_path=refs)
            del series_id, series_uid, refs
            return
        else:
            return None
    except Exception as e:
        print('Error in function SaveDICOM_Image.saveDicomNewSeries: ' + str(e))
 
    
def generateUIDs(dataset, seriesNumber=None, studyUID=None):
    """
    This function generates and returns a SeriesUID and an InstanceUID.
    It also returns SeriesNumber in the first index of the output list.
    The SeriesUID is generated based on the StudyUID and on seriesNumber (if provided)
    The InstanceUID is generated based on SeriesUID.
    """
    try:
        if studyUID is None:     
            studyUID = dataset.StudyInstanceUID
        # See http://dicom.nema.org/dicom/2013/output/chtml/part05/chapter_B.html regarding UID creation rules
        prefix = studyUID.split(".", maxsplit=7)
        prefix = '.'.join(prefix[:6])
        if seriesNumber is None:
            seriesNumber = str(dataset.SeriesNumber) + str(random.randint(0, 999))
        prefixSeries = prefix + "." + str(seriesNumber) + "."
        imageNumber = str(dataset.InstanceNumber).lstrip("0")
        if imageNumber == "": imageNumber = "999999" 
        prefixImage = prefix + "." + str(seriesNumber) + "." + imageNumber + "."
        seriesUID = pydicom.uid.generate_uid(prefix=prefixSeries)
        imageUID = pydicom.uid.generate_uid(prefix=prefixImage)
        return [seriesNumber, seriesUID, imageUID]
    except Exception as e:
        print('Error in function SaveDICOM_Image.generateUIDs: ' + str(e))


def overwriteDicomFileTag(imagePath, dicomTag, newValue):
    try:
        if isinstance(imagePath, list):
            datasetList = ReadDICOM_Image.getSeriesDicomDataset(imagePath)
            for index, dataset in enumerate(datasetList):
                if isinstance(dicomTag, str):
                    try: dataset.data_element(dicomTag).value = newValue
                    except: dataset.add_new(dicomTag, dictionary_VR(dicomTag), newValue)
                else:
                    try: dataset[hex(dicomTag)].value = newValue
                    except: dataset.add_new(hex(dicomTag), dictionary_VR(hex(dicomTag)), newValue)
                saveDicomToFile(dataset, output_path=imagePath[index])
        else:
            dataset = ReadDICOM_Image.getDicomDataset(imagePath)
            if isinstance(dicomTag, str):
                try: dataset.data_element(dicomTag).value = newValue
                except: dataset.add_new(dicomTag, dictionary_VR(dicomTag), newValue)
            else:
                try: dataset[hex(dicomTag)].value = newValue
                except: dataset.add_new(hex(dicomTag), dictionary_VR(hex(dicomTag)), newValue)
            saveDicomToFile(dataset, output_path=imagePath)
        return
    except Exception as e:
        print('Error in SaveDICOM_Image.overwriteDicomFileTag: ' + str(e))


def createNewPixelArray(imageArray, dataset):
    try:        
        # If the new array is a binary image / mask
        if len(np.unique(imageArray)) == 2:
            param.editDicom(dataset, imageArray, "SEG")
            return dataset
        numberFrames = 1
        enhancedArrayInt = []
        numDimensions = len(np.shape(imageArray))
        # If Enhanced MRI, then:
        # For each frame, slope and intercept are M and B. For registration, I will have to add Image Position and Orientation
        if hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
            if numDimensions == 2:
                dataset.NumberOfFrames = 1
            else:
                dataset.NumberOfFrames = np.shape(imageArray)[0]
            del dataset.PerFrameFunctionalGroupsSequence[dataset.NumberOfFrames:]
            numberFrames = dataset.NumberOfFrames
        for index in range(numberFrames):
            if len(np.shape(imageArray)) == 2:
                tempArray = imageArray
            else:
                tempArray = np.squeeze(imageArray[index, ...])
            dataset.PixelRepresentation = 0
            target = (np.power(2, dataset.BitsAllocated) - 1) * np.ones(np.shape(tempArray))
            maximum = np.ones(np.shape(tempArray)) * np.amax(tempArray)
            minimum = np.ones(np.shape(tempArray)) * np.amin(tempArray)
            imageScaled = target * (tempArray - minimum) / (maximum - minimum)
            slope =  target / (maximum - minimum)
            intercept = (- target * minimum)/ (maximum - minimum)
            rescaleSlope = np.ones(np.shape(tempArray)) / slope
            rescaleIntercept = - intercept / slope
            if dataset.BitsAllocated == 8:
                imageArrayInt = imageScaled.astype(np.uint8)
            elif dataset.BitsAllocated == 16:
                imageArrayInt = imageScaled.astype(np.uint16)
            elif dataset.BitsAllocated == 32:
                imageArrayInt = imageScaled.astype(np.uint32)
            elif dataset.BitsAllocated == 64:
                imageArrayInt = imageScaled.astype(np.uint64)
            else:
                imageArrayInt = imageScaled.astype(dataset.pixel_array.dtype)
            dataset.add_new('0x00280106', 'US', int(np.amin(imageArrayInt)))
            dataset.add_new('0x00280107', 'US', int(np.amax(imageArrayInt)))
            if hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
                # Rotate back to Original Position
                enhancedArrayInt.append(np.transpose(imageArrayInt))
                # Rescsale Slope and Intercept
                dataset.PerFrameFunctionalGroupsSequence[index].PixelValueTransformationSequence[0].RescaleSlope = rescaleSlope.flatten()[0]
                dataset.PerFrameFunctionalGroupsSequence[index].PixelValueTransformationSequence[0].RescaleIntercept = rescaleIntercept.flatten()[0]
                # Set Window Center and Width
                center = (np.amax(tempArray) + np.amin(tempArray)) / 2 # (0 if int(np.amin(imageArrayInt)) < 0 else int(target.flatten()[0]/2))
                width = np.amax(tempArray) - np.amin(tempArray) # int(target.flatten()[0])
                if width == 1.0: width = 1.1 
                dataset.PerFrameFunctionalGroupsSequence[index].FrameVOILUTSequence[0].WindowCenter = center
                dataset.PerFrameFunctionalGroupsSequence[index].FrameVOILUTSequence[0].WindowWidth = width
            else:
                # Rotate back to Original Position
                imageArrayInt = np.transpose(imageArrayInt)
                # Rescsale Slope and Intercept
                dataset.RescaleSlope = rescaleSlope.flatten()[0]
                dataset.RescaleIntercept = rescaleIntercept.flatten()[0]
                # Set Window Center and Width
                center = (np.amax(tempArray) + np.amin(tempArray)) / 2
                width = np.amax(tempArray) - np.amin(tempArray)
                if width == 1.0: width = 1.1
                dataset.add_new('0x00281050', 'DS', center)
                dataset.add_new('0x00281051', 'DS', width)
                # dataset.WindowCenter = (0 if int(np.amin(imageArrayInt)) < 0 else int(target.flatten()[0]/2))
                # dataset.WindowWidth = int(target.flatten()[0])
        if enhancedArrayInt:
            imageArrayInt = np.array(enhancedArrayInt)
        
        # Set the shape/dimensions and PixelData
        dataset.Rows = np.shape(imageArrayInt)[-2]
        dataset.Columns = np.shape(imageArrayInt)[-1]
        dataset.PixelData = imageArrayInt.tobytes()
        del imageScaled, enhancedArrayInt, tempArray
        return dataset
    except Exception as e:
        print('Error in SaveDICOM_Image.createNewPixelArray: ' + str(e))


def createNewSingleDicom(dicomData, imageArray, series_id=None, series_uid=None, series_name=None, comment=None, parametric_map=None, colourmap=None, list_refs=None):
    """This function takes a DICOM Object, copies most of the DICOM tags from the DICOM given in input
        and writes the imageArray into the new DICOM Object in PixelData. 
    """
    try:
        newDicom = copy.deepcopy(dicomData)
        imageArray = copy.deepcopy(imageArray)

        # Series ID and UID
        if (series_id is None) and (series_uid is None):
            ids = generateUIDs(dicomData)
            series_id = ids[0]
            series_uid = ids[1]
        elif (series_id is not None) and (series_uid is None):
            series_uid = generateUIDs(dicomData, seriesNumber=series_id)[1]
        elif (series_id is None) and (series_uid is not None):
            series_id = str(dicomData.SeriesNumber) + str(random.randint(0, 999))
        newDicom.SeriesNumber = int(series_id)
        newDicom.SeriesInstanceUID = series_uid

        # Generate Unique ID based on the Series ID
        newDicom.SOPInstanceUID = generateUIDs(newDicom, seriesNumber=series_id)[2]

        # Date and Time of Creation
        dt = datetime.datetime.now()
        timeStr = dt.strftime('%H%M%S')  # long format with micro seconds
        newDicom.ContentDate = dt.strftime('%Y%m%d')
        newDicom.ContentTime = timeStr
        newDicom.InstanceCreationDate = dt.strftime('%Y%m%d')
        newDicom.InstanceCreationTime = timeStr
        newDicom.SeriesDate = dt.strftime('%Y%m%d')
        newDicom.ImageDate = dt.strftime('%Y%m%d')
        newDicom.AcquisitionDate = dt.strftime('%Y%m%d')
        newDicom.SeriesTime = timeStr
        newDicom.ImageTime = timeStr
        newDicom.AcquisitionTime = timeStr
        newDicom.ImageType.insert(0, "DERIVED")

        # Series, Instance and Class for Reference
        refd_series_sequence = Sequence()
        newDicom.ReferencedSeriesSequence = refd_series_sequence
        refd_series1 = Dataset()
        refd_instance_sequence = Sequence()
        refd_series1.ReferencedInstanceSequence = refd_instance_sequence
        refd_instance1 = Dataset()
        refd_instance1.ReferencedSOPClassUID = dicomData.SOPClassUID
        refd_instance1.ReferencedSOPInstanceUID = dicomData.SOPInstanceUID
        refd_instance_sequence.append(refd_instance1)
        refd_series1.SeriesInstanceUID = dicomData.SeriesInstanceUID
        refd_series_sequence.append(refd_series1)

        # Extra references, besides the main one, which is dicomData
        if list_refs is not None:
            if np.shape(list_refs) == ():
                refd_series1 = Dataset()
                refd_instance_sequence = Sequence()
                refd_series1.ReferencedInstanceSequence = refd_instance_sequence
                refd_instance1 = Dataset()
                refd_instance1.ReferencedSOPInstanceUID = list_refs.SOPInstanceUID
                refd_instance1.ReferencedSOPClassUID = list_refs.SOPClassUID
                refd_instance_sequence.append(refd_instance1)
                refd_series1.SeriesInstanceUID = list_refs.SeriesInstanceUID
                refd_series_sequence.append(refd_series1)
            else:
                for individualRef in list_refs:
                    refd_series1 = Dataset()
                    refd_instance_sequence = Sequence()
                    refd_series1.ReferencedInstanceSequence = refd_instance_sequence
                    refd_instance1 = Dataset()
                    refd_instance1.ReferencedSOPInstanceUID = individualRef.SOPInstanceUID
                    refd_instance1.ReferencedSOPClassUID = individualRef.SOPClassUID
                    refd_instance_sequence.append(refd_instance1)
                    refd_series1.SeriesInstanceUID = individualRef.SeriesInstanceUID
                    refd_series_sequence.append(refd_series1)
            del list_refs

        # Comments
        if comment is not None:
            newDicom.ImageComments = comment
            # Then assign new Series Name by default
            if len(dicomData.dir("SeriesDescription"))>0:
                newDicom.SeriesDescription = dicomData.SeriesDescription + comment
            elif len(dicomData.dir("SequenceName"))>0 & len(dicomData.dir("PulseSequenceName"))==0:
                newDicom.SeriesDescription = dicomData.SequenceName + comment
            elif len(dicomData.dir("ProtocolName"))>0:
                newDicom.SeriesDescription = dicomData.ProtocolName + comment
            else:
                newDicom.SeriesDescription = "NewSeries" + newDicom.SeriesNumber
                
        # But if the user provides a Series Name
        if series_name:
            newDicom.SeriesDescription = series_name

        # Parametric Map
        if parametric_map is not None:
            param.editDicom(newDicom, imageArray, parametric_map)
            return newDicom

        newDicom = createNewPixelArray(imageArray, newDicom)    

        # Add colourmap here
        if (colourmap is None) and hasattr(newDicom, 'PhotometricInterpretation'):
            if newDicom.PhotometricInterpretation == 'PALETTE COLOR':
                # This deletes the colourmap that came with the source/input DICOM
                stringType = 'US'
                imageArrayInt = newDicom.pixel_array
                minValue = int(np.amin(imageArrayInt))
                numberOfValues = int(np.amax(imageArrayInt))
                arrayForRGB = np.arange(0, numberOfValues)
                colorsList = cm.ScalarMappable(cmap=colourmap).to_rgba(np.array(arrayForRGB), bytes=False)
                totalBytes = dicomData.BitsAllocated
                newDicom.add_new('0x00281101', stringType, [numberOfValues, minValue, totalBytes])
                newDicom.add_new('0x00281102', stringType, [numberOfValues, minValue, totalBytes])
                newDicom.add_new('0x00281103', stringType, [numberOfValues, minValue, totalBytes])
                newDicom.RedPaletteColorLookupTableData = bytes(np.array([int((np.power(
                    2, totalBytes) - 1) * value) for value in colorsList[:, 0].flatten()]).astype('uint'+str(totalBytes)))
                newDicom.GreenPaletteColorLookupTableData = bytes(np.array([int((np.power(
                    2, totalBytes) - 1) * value) for value in colorsList[:, 1].flatten()]).astype('uint'+str(totalBytes)))
                newDicom.BluePaletteColorLookupTableData = bytes(np.array([int((np.power(
                    2, totalBytes) - 1) * value) for value in colorsList[:, 2].flatten()]).astype('uint'+str(totalBytes)))
        elif colourmap is not None:
            newDicom.PhotometricInterpretation = 'PALETTE COLOR'
            newDicom.RGBLUTTransferFunction = 'TABLE'
            newDicom.ContentLabel = colourmap
            stringType = 'US'
            imageArrayInt = newDicom.pixel_array
            minValue = int(np.amin(imageArrayInt))
            numberOfValues = int(np.amax(imageArrayInt))
            arrayForRGB = np.arange(0, numberOfValues)
            colorsList = cm.ScalarMappable(cmap=colourmap).to_rgba(np.array(arrayForRGB), bytes=False)
            totalBytes = dicomData.BitsAllocated
            newDicom.add_new('0x00281101', stringType, [numberOfValues, minValue, totalBytes])
            newDicom.add_new('0x00281102', stringType, [numberOfValues, minValue, totalBytes])
            newDicom.add_new('0x00281103', stringType, [numberOfValues, minValue, totalBytes])
            newDicom.RedPaletteColorLookupTableData = bytes(np.array([int((np.power(
                2, totalBytes) - 1) * value) for value in colorsList[:, 0].flatten()]).astype('uint'+str(totalBytes)))
            newDicom.GreenPaletteColorLookupTableData = bytes(np.array([int((np.power(
                2, totalBytes) - 1) * value) for value in colorsList[:, 1].flatten()]).astype('uint'+str(totalBytes)))
            newDicom.BluePaletteColorLookupTableData = bytes(np.array([int((np.power(
                2, totalBytes) - 1) * value) for value in colorsList[:, 2].flatten()]).astype('uint'+str(totalBytes)))
            del imageArrayInt

        del dicomData, imageArray#, imageArrayInt, imageScaled, enhancedArrayInt, tempArray
        return newDicom
    except Exception as e:
        print('Error in function SaveDICOM_Image.createNewSingleDicom: ' + str(e))


def updateSingleDicom(dicomData, colourmap=None, levels=None, lut=None):
    """This function takes a DICOM Object and changes it to include the
        new colourmap selected in the interface. It will have more features in the future.
    """
    try:
        #and (colourmap != 'gray') removed from If statement below, so as to save gray colour tables
        if (colourmap == 'gray'):
            dicomData.PhotometricInterpretation = 'MONOCHROME2'
            dicomData.ContentLabel = ''
            if hasattr(dicomData, 'RedPaletteColorLookupTableData'):
                del (dicomData.RGBLUTTransferFunction, dicomData.RedPaletteColorLookupTableData,
                    dicomData.GreenPaletteColorLookupTableData, dicomData.BluePaletteColorLookupTableData,
                    dicomData.RedPaletteColorLookupTableDescriptor, dicomData.GreenPaletteColorLookupTableDescriptor,
                    dicomData.BluePaletteColorLookupTableDescriptor)
        if ((colourmap is not None)  and (colourmap != 'custom') and (colourmap != 'gray') 
            and (colourmap != 'default') and isinstance(colourmap, str)):
            dicomData.PhotometricInterpretation = 'PALETTE COLOR'
            dicomData.RGBLUTTransferFunction = 'TABLE'
            dicomData.ContentLabel = colourmap
            stringType = 'US' # ('SS' if minValue < 0 else 'US')
            dicomData.PixelRepresentation = 0 # (1 if minValue < 0 else 0)
            pixelArray = dicomData.pixel_array
            minValue = int(np.amin(pixelArray))
            maxValue = int(np.amax(pixelArray))
            numberOfValues = int(maxValue - minValue)
            arrayForRGB = np.arange(0, numberOfValues)
            colorsList = cm.ScalarMappable(cmap=colourmap).to_rgba(np.array(arrayForRGB), bytes=False)
            totalBytes = dicomData.BitsAllocated
            dicomData.add_new('0x00281101', stringType, [numberOfValues, minValue, totalBytes])
            dicomData.add_new('0x00281102', stringType, [numberOfValues, minValue, totalBytes])
            dicomData.add_new('0x00281103', stringType, [numberOfValues, minValue, totalBytes])
            dicomData.RedPaletteColorLookupTableData = bytes(np.array([int((np.power(
                2, totalBytes) - 1) * value) for value in colorsList[:, 0].flatten()]).astype('uint'+str(totalBytes)))
            dicomData.GreenPaletteColorLookupTableData = bytes(np.array([int((np.power(
                2, totalBytes) - 1) * value) for value in colorsList[:, 1].flatten()]).astype('uint'+str(totalBytes)))
            dicomData.BluePaletteColorLookupTableData = bytes(np.array([int((np.power(
                2, totalBytes) - 1) * value) for value in colorsList[:, 2].flatten()]).astype('uint'+str(totalBytes)))
        if (levels is not None):
            if hasattr(dicomData, 'PerFrameFunctionalGroupsSequence'):
                for index in range(len(dicomData.PerFrameFunctionalGroupsSequence)):
                    slope = float(getattr(dicomData.PerFrameFunctionalGroupsSequence[index].PixelValueTransformationSequence[0], 'RescaleSlope', 1))
                    intercept = float(getattr(dicomData.PerFrameFunctionalGroupsSequence[index].PixelValueTransformationSequence[0], 'RescaleIntercept', 0))
                    center = levels[0] # (levels[0] - intercept) / slope
                    width = levels[1] # / slope
                    dicomData.PerFrameFunctionalGroupsSequence[index].FrameVOILUTSequence[0].WindowCenter = center
                    dicomData.PerFrameFunctionalGroupsSequence[index].FrameVOILUTSequence[0].WindowWidth = width
            else:
                slope = float(getattr(dicomData, 'RescaleSlope', 1))
                intercept = float(getattr(dicomData, 'RescaleIntercept', 0))
                center = levels[0] # (levels[0] - intercept) / slope
                width = levels[1] # / slope
                dicomData.add_new('0x00281050', 'DS', center)
                dicomData.add_new('0x00281051', 'DS', width)
            
        return dicomData   
    except Exception as e:
        print('Error in function SaveDICOM_Image.updateSingleDicom: ' + str(e))

    
def saveDicomToFile(dicomData, output_path=None):
    """This method takes a DICOM object and saves it as a DICOM file 
        with the set filename in the input arguments.
    """
    try:
        if output_path is None:
            try:
                output_path = os.getcwd() + copy.deepcopy(dicomData.InstanceNumber).zfill(6) + ".dcm"
            except:
                try:
                    output_path = os.getcwd() + copy.deepcopy(dicomData.ImageNumber).zfill(6) + ".dcm"
                except:
                    output_path = os.getcwd() + copy.deepcopy(dicomData.SOPInstanceUID) + ".dcm"

        pydicom.filewriter.dcmwrite(output_path, dicomData, write_like_original=True)
        # Try to read the new generated file to check if it's corrupted
        #list_tags = ['InstanceNumber', 'SOPInstanceUID', 'PixelData', 'FloatPixelData', 'DoubleFloatPixelData', 'AcquisitionTime',
        #             'AcquisitionDate', 'SeriesTime', 'SeriesDate', 'PatientName', 'PatientID', 'StudyDate', 'StudyTime', 
        #             'SeriesDescription', 'SequenceName', 'ProtocolName', 'SeriesNumber', 'PerFrameFunctionalGroupsSequence']
        #try:
        #    pydicom.dcmread(output_path, specific_tags=list_tags)
        #except:
        #    del output_path
        #    print('File ' + output_path + ' corrupted during the saving process. Weasel deleted the mentioned file locally.')
        return
    except Exception as e:
        print('Error in function SaveDICOM_Image.saveDicomToFile: ' + str(e))