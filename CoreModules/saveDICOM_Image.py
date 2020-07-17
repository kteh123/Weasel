import os
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.sequence import Sequence
import datetime
import copy
import random
from matplotlib import cm
import CoreModules.readDICOM_Image as readDICOM_Image
import CoreModules.ParametricMapsDictionary as param
import logging

logger = logging.getLogger(__name__)


def returnFilePath(imagePath, suffix, new_path=None):
    """This method returns the new filepath of the object to be saved."""
    # Think of a way to choose a select a new FilePath
    try:
        if os.path.exists(imagePath):
            # Need to think about what new name to give to the file and how to save multiple files for the same sequence
            if new_path is not None:
                newFilePath = new_path + '.dcm'
            else:
                outputFolder = os.path.join(os.path.dirname(imagePath), "output" + suffix)
                fileName = os.path.splitext(os.path.basename(imagePath))[0]
                try: os.mkdir(outputFolder)
                except: pass
                newFilePath = os.path.join(outputFolder, fileName + suffix + '.dcm')
            return newFilePath

        else:
            return None
    except Exception as e:
        print('Error in function saveDICOM_Image.returnFilePath: ' + str(e))


def saveDicomOutputResult(newFilePath, imagePath, pixelArray, suffix, series_id=None, series_uid=None, image_number=None, parametric_map=None, colourmap=None, list_refs_path=None):
    """This method saves the new pixelArray into DICOM in the given newFilePath"""
    try:
        if os.path.exists(imagePath):
            dataset = readDICOM_Image.getDicomDataset(imagePath)
            if list_refs_path is not None:
                refs = []
                for individualRef in list_refs_path:
                    refs.append(readDICOM_Image.getDicomDataset(individualRef))
            else:
                refs = None
            newDataset = createNewSingleDicom(dataset, pixelArray, series_id=series_id, series_uid=series_uid, comment=suffix, parametric_map=parametric_map, colourmap=colourmap, list_refs=refs)
            if (image_number is not None) and (len(np.shape(pixelArray)) < 3):
                newDataset.InstanceNumber = image_number
                newDataset.ImageNumber = image_number
            saveDicomToFile(newDataset, output_path=newFilePath)
            del dataset, newDataset, refs, image_number
            return
        else:
            return None

    except Exception as e:
        print('Error in function saveDICOM_Image.saveDicomOutputResult: ' + str(e))


def saveDicomNewSeries(derivedImagePathList, imagePathList, pixelArrayList, suffix, series_id=None, series_uid=None, parametric_map=None, colourmap=None, list_refs_path=None):
    """This method saves the pixelArrayList into DICOM files with metadata pointing to the same series"""
    # What if it's a map with less files than original? Think about iterating the first elements and sort path list by SliceLocation - see T2* algorithm
    # Think of a way to choose a select a new FilePath or Folder
    try:
        if os.path.exists(imagePathList[0]):
            if series_id is None:
                series_id = int(str(readDICOM_Image.getDicomDataset(imagePathList[0]).SeriesNumber) + str(random.randint(0, 9999)))
            if series_uid is None:
                series_uid = pydicom.uid.generate_uid()

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

                saveDicomOutputResult(newFilePath, imagePathList[index], pixelArrayList[index], suffix, series_id=series_id, series_uid=series_uid, image_number=index,  parametric_map=parametric_map, 
                                      colourmap=colourmap, list_refs_path=refs)
            del series_id, series_uid, refs
            return
        else:
            return None
    except Exception as e:
        print('Error in function saveDICOM_Image.saveDicomNewSeries: ' + str(e))


def updateSingleDicomImage(objWeasel, spinBoxIntensity, spinBoxContrast, 
                imagePath='', seriesID='', studyID='', colourmap=None, lut=None):
    try:
        logger.info("In saveDICOM_Image.updateSingleDicomImage")
        objWeasel.displayMessageSubWindow(
            "<H4>Updating 1 DICOM file</H4>",
            "Updating DICOM images")
        objWeasel.setMsgWindowProgBarMaxValue(1)
        objWeasel.setMsgWindowProgBarValue(0)
        dataset = readDICOM_Image.getDicomDataset(imagePath)
        levels = [spinBoxIntensity.value(), spinBoxContrast.value()]
        updatedDataset = updateSingleDicom(dataset, colourmap=colourmap, levels=levels, lut=lut)
        saveDicomToFile(updatedDataset, output_path=imagePath)
        objWeasel.setMsgWindowProgBarValue(1)
        objWeasel.closeMessageSubWindow()
    except Exception as e:
        print('Error in saveDICOM_Image.updateSingleDicomImage: ' + str(e))


def createNewSingleDicom(dicomData, imageArray, series_id=None, series_uid=None, comment=None, parametric_map=None, colourmap=None, list_refs=None):
    """This function takes a DICOM Object, copies most of the DICOM tags from the DICOM given in input
        and writes the imageArray into the new DICOM Object in PixelData. 
    """
    try:
        newDicom = copy.deepcopy(dicomData)
        imageArray = copy.deepcopy(imageArray)

        # Generate Unique ID
        newDicom.SOPInstanceUID = pydicom.uid.generate_uid()

        # Series ID and UID
        if series_id is None:
            newDicom.SeriesNumber = int(str(dicomData.SeriesNumber) + str(random.randint(0, 999)))
        else:
            newDicom.SeriesNumber = series_id
        if series_uid is None:
            newDicom.SeriesInstanceUID = pydicom.uid.generate_uid()
        else:
            newDicom.SeriesInstanceUID = series_uid

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
        newDicom.ImageType = ["DERIVED"]

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
            if len(dicomData.dir("SeriesDescription"))>0:
                newDicom.SeriesDescription = dicomData.SeriesDescription + comment
            elif len(dicomData.dir("SequenceName"))>0 & len(dicomData.dir("PulseSequenceName"))==0:
                newDicom.SeriesDescription = dicomData.SequenceName + comment
            elif len(dicomData.dir("SeriesDescription"))>0:
                newDicom.SeriesDescription = dicomData.SeriesDescription + comment
            elif len(dicomData.dir("ProtocolName"))>0:
                newDicom.SeriesDescription = dicomData.ProtocolName + comment
            else:
                newDicom.SeriesDescription = "NewSeries" + newDicom.SeriesNumber 

        # Parametric Map
        if parametric_map is not None:
            param.editDicom(newDicom, imageArray, parametric_map)
            #return param.editDicom(newDicom, imageArray, parametric_map)

        numberFrames = 1
        enhancedArrayInt = []
        # If Enhanced MRI, then:
        # For each frame, slope and intercept are M and B. For registration, I will have to add Image Position and Orientation
        if hasattr(dicomData, 'PerFrameFunctionalGroupsSequence'):
            if len(np.shape(imageArray)) == 2:
                newDicom.NumberOfFrames = 1
            else:
                newDicom.NumberOfFrames = np.shape(imageArray)[0]
            del newDicom.PerFrameFunctionalGroupsSequence[newDicom.NumberOfFrames:]
            numberFrames = newDicom.NumberOfFrames
        for index in range(numberFrames):
            if len(np.shape(imageArray)) == 2:
                tempArray = imageArray
            else:
                tempArray = np.squeeze(imageArray[index, ...])
    
            if int(np.amin(imageArray)) < 0:
                newDicom.PixelRepresentation = 1
                target = (np.power(2, newDicom.BitsAllocated) - 1)*(np.ones(np.shape(tempArray)))
                maximum = np.ones(np.shape(tempArray))*np.amax(tempArray)
                minimum = np.ones(np.shape(tempArray))*np.amin(tempArray)
                extra = target / (2*np.ones(np.shape(tempArray)))
                imageScaled = target * (tempArray - minimum) / (maximum - minimum) - extra
                slope =  target / (maximum - minimum)
                intercept = (- target * minimum - extra * (maximum - minimum))/ (maximum - minimum)
                rescaleSlope = np.ones(np.shape(tempArray)) / slope
                rescaleIntercept = - intercept / slope
                if newDicom.BitsAllocated == 8:
                    imageArrayInt = imageScaled.astype(np.int8)
                elif newDicom.BitsAllocated == 16:
                    imageArrayInt = imageScaled.astype(np.int16)
                elif newDicom.BitsAllocated == 32:
                    imageArrayInt = imageScaled.astype(np.int32)
                elif newDicom.BitsAllocated == 64:
                    imageArrayInt = imageScaled.astype(np.int64)
                else:
                    imageArrayInt = imageScaled.astype(dicomData.pixel_array.dtype)
                newDicom.add_new('0x00280106', 'SS', int(np.amin(imageArrayInt)))
                newDicom.add_new('0x00280107', 'SS', int(np.amax(imageArrayInt)))
            else:
                newDicom.PixelRepresentation = 0
                target = (np.power(2, newDicom.BitsAllocated) - 1)*np.ones(np.shape(tempArray))
                maximum = np.ones(np.shape(tempArray))*np.amax(tempArray)
                minimum = np.ones(np.shape(tempArray))*np.amin(tempArray)
                imageScaled = target * (tempArray - minimum) / (maximum - minimum)
                slope =  target / (maximum - minimum)
                intercept = (- target * minimum)/ (maximum - minimum)
                rescaleSlope = np.ones(np.shape(tempArray)) / slope
                rescaleIntercept = - intercept / slope
                if newDicom.BitsAllocated == 8:
                    imageArrayInt = imageScaled.astype(np.uint8)
                elif newDicom.BitsAllocated == 16:
                    imageArrayInt = imageScaled.astype(np.uint16)
                elif newDicom.BitsAllocated == 32:
                    imageArrayInt = imageScaled.astype(np.uint32)
                elif newDicom.BitsAllocated == 64:
                    imageArrayInt = imageScaled.astype(np.uint64)
                else:
                    imageArrayInt = imageScaled.astype(dicomData.pixel_array.dtype)
                newDicom.add_new('0x00280106', 'US', int(np.amin(imageArrayInt)))
                newDicom.add_new('0x00280107', 'US', int(np.amax(imageArrayInt)))
            if hasattr(dicomData, 'PerFrameFunctionalGroupsSequence'):
                enhancedArrayInt.append(imageArrayInt)
                newDicom.PerFrameFunctionalGroupsSequence[index].PixelValueTransformationSequence[0].RescaleSlope = rescaleSlope.flatten()[0]
                newDicom.PerFrameFunctionalGroupsSequence[index].PixelValueTransformationSequence[0].RescaleIntercept = rescaleIntercept.flatten()[0]
            else:
                newDicom.RescaleSlope = rescaleSlope.flatten()[0]
                newDicom.RescaleIntercept = rescaleIntercept.flatten()[0]
        if enhancedArrayInt:
            imageArrayInt = np.array(enhancedArrayInt)
            imageArrayInt = np.rollaxis(imageArrayInt, 0)

        # Add colourmap here
        # colourmap = "hot"
        if colourmap is not None:
            newDicom.PhotometricInterpretation = 'PALETTE COLOR'
            newDicom.RGBLUTTransferFunction = 'TABLE'
            newDicom.ContentLabel = colourmap
            minValue = int(np.amin(imageArrayInt))
            numberOfValues = int(np.amax(imageArrayInt))
            arrayForRGB = np.arange(0, numberOfValues)
            colorsList = cm.ScalarMappable(cmap=colourmap).to_rgba(np.array(arrayForRGB), bytes=False)
            stringType = ('SS' if minValue < 0 else 'US')
            dicomData.PixelRepresentation = (1 if minValue < 0 else 0)
            constant = (2 if minValue < 0 else 1)
            totalBytes = dicomData.BitsAllocated
            newDicom.add_new('0x00281101', stringType, [numberOfValues, minValue, totalBytes])
            newDicom.add_new('0x00281102', stringType, [numberOfValues, minValue, totalBytes])
            newDicom.add_new('0x00281103', stringType, [numberOfValues, minValue, totalBytes])
            newDicom.RedPaletteColorLookupTableData = bytes(np.array([int((np.power(
                2, totalBytes)/constant - 1)*value) for value in colorsList[:, 0].flatten()]).astype('uint'+str(totalBytes)))
            newDicom.GreenPaletteColorLookupTableData = bytes(np.array([int((np.power(
                2,totalBytes)/constant - 1)*value) for value in colorsList[:, 1].flatten()]).astype('uint'+str(totalBytes)))
            newDicom.BluePaletteColorLookupTableData = bytes(np.array([int((np.power(
                2, totalBytes)/constant - 1)*value) for value in colorsList[:, 2].flatten()]).astype('uint'+str(totalBytes)))

        # Take Phase Encoding into account
        if newDicom.InPlanePhaseEncodingDirection == "ROW" or len(np.shape(imageArrayInt)) > 2:
            imageArrayInt = np.transpose(imageArrayInt, axes=(1,0))
        newDicom.Rows = np.shape(imageArrayInt)[-2]
        newDicom.Columns = np.shape(imageArrayInt)[-1]
        newDicom.WindowCenter = (0 if int(np.amin(imageArrayInt)) < 0 else int(target.flatten()[0]/2))
        newDicom.WindowWidth = int(target.flatten()[0])
        newDicom.PixelData = imageArrayInt.tobytes()

        del dicomData, imageArray, imageScaled, imageArrayInt, enhancedArrayInt, tempArray
        return newDicom
    except Exception as e:
        print('Error in function createNewSingleDicom: ' + str(e))


def updateSingleDicom(dicomData, colourmap=None, levels=None, lut=None):
    """This function takes a DICOM Object and changes it to include the
        new colourmap selected in the interface. It will have more features in the future.
    """
    try:
        if (colourmap is not None) and (colourmap != 'gray') \
            and (colourmap != 'custom') and (colourmap != 'default') and isinstance(colourmap, str):
            dicomData.PhotometricInterpretation = 'PALETTE COLOR'
            dicomData.RGBLUTTransferFunction = 'TABLE'
            dicomData.ContentLabel = colourmap
            pixelArray = dicomData.pixel_array
            minValue = int(np.amin(pixelArray))
            maxValue = int(np.amax(pixelArray))
            numberOfValues = int(maxValue - minValue)
            arrayForRGB = np.arange(0, numberOfValues)
            colorsList = cm.ScalarMappable(cmap=colourmap).to_rgba(np.array(arrayForRGB), bytes=False)
            stringType = ('SS' if minValue < 0 else 'US')
            dicomData.PixelRepresentation = (1 if minValue < 0 else 0)
            constant = (2 if minValue < 0 else 1)
            totalBytes = dicomData.BitsAllocated
            dicomData.add_new('0x00280106', stringType, minValue)
            dicomData.add_new('0x00280107', stringType, maxValue)
            dicomData.add_new('0x00281101', stringType, [numberOfValues, minValue, totalBytes])
            dicomData.add_new('0x00281102', stringType, [numberOfValues, minValue, totalBytes])
            dicomData.add_new('0x00281103', stringType, [numberOfValues, minValue, totalBytes])
            dicomData.RedPaletteColorLookupTableData = bytes(np.array([int((np.power(
                2, totalBytes)/constant - 1)*value) for value in colorsList[:, 0].flatten()]).astype('uint'+str(totalBytes)))
            dicomData.GreenPaletteColorLookupTableData = bytes(np.array([int((np.power(
                2,totalBytes) /constant - 1)*value) for value in colorsList[:, 1].flatten()]).astype('uint'+str(totalBytes)))
            dicomData.BluePaletteColorLookupTableData = bytes(np.array([int((np.power(
                2, totalBytes)/constant - 1)*value) for value in colorsList[:, 2].flatten()]).astype('uint'+str(totalBytes)))
        # elif (colourmap is 'custom') and (isinstance(lut, np.ndarray)):
        #     # 2 options here!
        #     # a) We create a matplotlib.cm named "Custom" on the UI and then pass it here and process as usual
        #     # b) We colourmap is not a string and we parse the array with the 3 columns/columns
        #     # Below will be an attempt to situation b). It will need testing!  
        #     dicomData.PhotometricInterpretation = 'PALETTE COLOR'
        #     dicomData.RGBLUTTransferFunction = 'TABLE'
        #     dicomData.ContentLabel = colourmap
        #     pixelArray = dicomData.pixel_array
        #     minValue = int(np.amin(pixelArray))
        #     maxValue = int(np.amax(pixelArray))
        #     numberOfValues = int(maxValue - minValue)
        #     # This is where I need to confirm whether it's correct - colorsList from lut
        #     colorsList = lut(np.linspace(0, 1, numberOfValues))
        #     stringType = ('SS' if minValue < 0 else 'US')
        #     totalBytes = dicomData.BitsAllocated
        #     dicomData.PixelRepresentation = (1 if minValue < 0 else 0)
        #     constant = (2 if minValue < 0 else 1)
        #     dicomData.add_new('0x00280106', stringType, minValue)
        #     dicomData.add_new('0x00280107', stringType, maxValue)
        #     dicomData.add_new('0x00281101', stringType, [numberOfValues, minValue, totalBytes])
        #     dicomData.add_new('0x00281102', stringType, [numberOfValues, minValue, totalBytes])
        #     dicomData.add_new('0x00281103', stringType, [numberOfValues, minValue, totalBytes])
        #     # The next lines may change slightly depending on the format of colorsList
        #     dicomData.RedPaletteColorLookupTableData = bytes(np.array([int((np.power(
        #         2, totalBytes)/constant - 1)*value) for value in colorsList[:, 0].flatten()]).astype('uint'+str(totalBytes)))
        #     dicomData.GreenPaletteColorLookupTableData = bytes(np.array([int((np.power(
        #         2,totalBytes)/constant - 1)*value) for value in colorsList[:, 1].flatten()]).astype('uint'+str(totalBytes)))
        #     dicomData.BluePaletteColorLookupTableData = bytes(np.array([int((np.power(
        #         2, totalBytes)/constant - 1)*value) for value in colorsList[:, 2].flatten()]).astype('uint'+str(totalBytes)))
        
        if (levels is not None):
            if hasattr(dicomData, 'PerFrameFunctionalGroupsSequence'):
                slope = float(getattr(dicomData.PerFrameFunctionalGroupsSequence[0].PixelValueTransformationSequence[0], 'RescaleSlope', 1))
                intercept = float(getattr(dicomData.PerFrameFunctionalGroupsSequence[0].PixelValueTransformationSequence[0], 'RescaleIntercept', 0))
            else:
                slope = float(getattr(dicomData, 'RescaleSlope', 1))
                intercept = float(getattr(dicomData, 'RescaleIntercept', 0))
            center = (levels[0] - intercept) / slope
            width = levels[1] / slope
            dicomData.add_new('0x00281050', 'DS', center)
            dicomData.add_new('0x00281051', 'DS', width)

        return dicomData
        
    except Exception as e:
        print('Error in function updateSingleDicom: ' + str(e))

    
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
        del dicomData
        return
    except Exception as e:
        print('Error in function saveDicomToFile: ' + str(e))