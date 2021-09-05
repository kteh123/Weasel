import os
import numpy as np
import random
import logging
import CoreModules.WEASEL.ReadDICOM_Image as ReadDICOM_Image
import CoreModules.WEASEL.SaveDICOM_Image as SaveDICOM_Image
import CoreModules.WEASEL.MessageWindow as messageWindow

logger = logging.getLogger(__name__)


class GenericDICOMTools:

    def __repr__(self):
       return '{}'.format(self.__class__.__name__)

    def copyDICOM(self, inputPath, series_id=None, series_uid=None, series_name=None, study_uid=None, study_name=None, patient_id=None, suffix="_Copy", output_dir=None):
        """
        Creates a DICOM copy of all files in "inputPath" (1 or more) into a new series.
        """
        logger.info("GenericDICOMTools.copyDICOM called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                if (series_id is None) and (series_uid is None):
                    series_id, series_uid = GenericDICOMTools.generateSeriesIDs(self, inputPath, studyUID=study_uid)
                elif (series_id is not None) and (series_uid is None):
                    _, series_uid = GenericDICOMTools.generateSeriesIDs(self, inputPath, seriesNumber=series_id, studyUID=study_uid)
                elif (series_id is None) and (series_uid is not None):
                    series_id = int(str(ReadDICOM_Image.getDicomDataset(inputPath).SeriesNumber) + str(random.randint(0, 9999)))
                newDataset = ReadDICOM_Image.getDicomDataset(inputPath)
                derivedPath = SaveDICOM_Image.returnFilePath(inputPath, suffix, output_folder=output_dir)
                SaveDICOM_Image.saveDicomToFile(newDataset, output_path=derivedPath)
                # The next lines perform an overwrite operation over the copied images
                if patient_id:
                        SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "PatientID", patient_id)
                if study_uid:
                    SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "StudyInstanceUID", study_uid)
                if study_name:
                    SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "StudyDescription", study_name)
                instance_uid = SaveDICOM_Image.generateUIDs(newDataset, seriesNumber=series_id, studyUID=study_uid)[2]
                SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "SOPInstanceUID", instance_uid)
                SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesInstanceUID", series_uid)
                SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesNumber", series_id)
                if series_name:
                    SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesDescription", series_name)
                else:
                    SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesDescription", str(newDataset.SeriesDescription + suffix))
                    #if hasattr(newDataset, "SeriesDescription"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "SeriesDescription", str(newDataset.SeriesDescription + suffix))
                    #elif hasattr(newDataset, "SequenceName"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "SequenceName", str(newDataset.SequenceName + suffix))
                    #elif hasattr(newDataset, "ProtocolName"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(derivedPath, "ProtocolName", str(newDataset.ProtocolName + suffix))
                newSeriesID = self.objXMLReader.insertNewImageInXMLFile(inputPath,
                                             derivedPath, suffix, newSeriesName=series_name, newStudyName=study_name, newSubjectName=patient_id)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                if (series_id is None) and (series_uid is None):
                    series_id, series_uid = GenericDICOMTools.generateSeriesIDs(self, inputPath, studyUID=study_uid)
                elif (series_id is not None) and (series_uid is None):
                    _, series_uid = GenericDICOMTools.generateSeriesIDs(self, inputPath, seriesNumber=series_id, studyUID=study_uid)
                elif (series_id is None) and (series_uid is not None):
                    series_id = int(str(ReadDICOM_Image.getDicomDataset(inputPath[0]).SeriesNumber) + str(random.randint(0, 9999)))
                derivedPath = []
                for path in inputPath:
                    newDataset = ReadDICOM_Image.getDicomDataset(path)
                    newFilePath = SaveDICOM_Image.returnFilePath(path, suffix, output_folder=output_dir)
                    SaveDICOM_Image.saveDicomToFile(newDataset, output_path=newFilePath)
                    derivedPath.append(newFilePath)
                    # The next lines perform an overwrite operation over the copied images
                    if patient_id:
                        SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "PatientID", patient_id)
                    if study_uid:
                        SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "StudyInstanceUID", study_uid)
                    if study_name:
                        SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "StudyDescription", study_name)
                    instance_uid = SaveDICOM_Image.generateUIDs(newDataset, seriesNumber=series_id, studyUID=study_uid)[2]
                    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SOPInstanceUID", instance_uid)
                    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesInstanceUID", series_uid)
                    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesNumber", series_id)
                    if series_name:
                        SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", series_name)
                    else:
                        SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", str(newDataset.SeriesDescription + suffix))
                        #if hasattr(newDataset, "SeriesDescription"):
                        #    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", str(newDataset.SeriesDescription + suffix))
                        #elif hasattr(newDataset, "SequenceName"):
                        #    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SequenceName", str(newDataset.SequenceName + suffix))
                        #elif hasattr(newDataset, "ProtocolName"):
                        #    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "ProtocolName", str(newDataset.ProtocolName + suffix))
                newSeriesID = self.objXMLReader.insertNewSeriesInXMLFile(
                                inputPath, derivedPath, suffix, newSeriesName=series_name, newStudyName=study_name, newSubjectName=patient_id)
            return derivedPath, newSeriesID
        except Exception as e:
            print('Error in function GenericDICOMTools.copyDICOM: ' + str(e))
            logger.exception('Error in GenericDICOMTools.copyDICOM: ' + str(e))

    def deleteDICOM(self, inputPath):
        """
        This functions remove all files in inputhPath and updates the XML file accordingly.
        """
        logger.info("GenericDICOMTools.deleteDICOM called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                os.remove(inputPath)
                self.objXMLReader.removeImageFromXMLFile(inputPath)
                for displayWindow in self.mdiArea.subWindowList():
                    if displayWindow.windowTitle().split(" - ")[-1] == os.path.basename(inputPath):
                        displayWindow.close()
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                for path in inputPath:
                    os.remove(path)
                self.objXMLReader.removeMultipleImagesFromXMLFile(inputPath)
                for displayWindow in self.mdiArea.subWindowList():
                    if displayWindow.windowTitle().split(" - ")[-1] in list(map(os.path.basename, inputPath)):
                        displayWindow.close()
        except Exception as e:
            print('Error in function GenericDICOMTools.deleteDICOM: ' + str(e))
            logger.exception('Error in GenericDICOMTools.deleteDICOM: ' + str(e))

    def mergeDicomIntoOneSeries(self, imagePathList, series_id=None, series_name="New Series", series_uid=None, study_name=None, study_uid=None, patient_id=None, suffix="_Merged", overwrite=False, progress_bar=False):
        """
        Merges all DICOM files in "imagePathList" into 1 series.
        It creates a copy if "overwrite=False" (default).
        """
        logger.info("GenericDICOMTools.mergeDicomIntoOneSeries called")
        try:
            if os.path.exists(imagePathList[0]):
                if (series_id is None) and (series_uid is None):
                    series_id, series_uid = GenericDICOMTools.generateSeriesIDs(self, imagePathList, studyUID=study_uid)
                elif (series_id is not None) and (series_uid is None):
                    _, series_uid = GenericDICOMTools.generateSeriesIDs(self, imagePathList, seriesNumber=series_id, studyUID=study_uid)
                elif (series_id is None) and (series_uid is not None):
                    series_id = int(str(ReadDICOM_Image.getDicomDataset(imagePathList[0]).SeriesNumber) + str(random.randint(0, 9999)))
            newImagePathList = []
            if progress_bar == True: messageWindow.displayMessageSubWindow(self, ("<H4>Merging {} images</H4>").format(len(imagePathList)), "Progress Bar - Merging")
            if overwrite:
                originalPathList = imagePathList
                if progress_bar == True: messageWindow.setMsgWindowProgBarMaxValue(self, len(imagePathList))
                for index, path in enumerate(imagePathList):
                    if progress_bar == True: messageWindow.setMsgWindowProgBarValue(self, index+1)
                    if patient_id:
                        SaveDICOM_Image.overwriteDicomFileTag(path, "PatientID", patient_id)
                    if study_uid:
                        SaveDICOM_Image.overwriteDicomFileTag(path, "StudyInstanceUID", study_uid)
                    if study_name:
                        SaveDICOM_Image.overwriteDicomFileTag(path, "StudyDescription", study_name)
                    SaveDICOM_Image.overwriteDicomFileTag(path, "SeriesInstanceUID", series_uid)
                    SaveDICOM_Image.overwriteDicomFileTag(path, "SeriesNumber", series_id)
                    SaveDICOM_Image.overwriteDicomFileTag(path, "SeriesDescription", series_name)
                    #dataset = ReadDICOM_Image.getDicomDataset(path)
                    #if hasattr(dataset, "SeriesDescription"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(path, "SeriesDescription", series_name)
                    #elif hasattr(dataset, "SequenceName"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(path, "SequenceName", series_name)
                    #elif hasattr(dataset, "ProtocolName"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(path, "ProtocolName", series_name)
                newImagePathList = imagePathList
                self.objXMLReader.insertNewSeriesInXMLFile(
                                originalPathList, newImagePathList, suffix, newSeriesName=series_name, newStudyName=study_name, newSubjectName=patient_id)
                self.objXMLReader.removeMultipleImagesFromXMLFile(originalPathList)
            else:
                if progress_bar == True: messageWindow.setMsgWindowProgBarMaxValue(self, len(imagePathList))
                for index, path in enumerate(imagePathList):
                    if progress_bar == True: messageWindow.setMsgWindowProgBarValue(self, index+1)
                    newDataset = ReadDICOM_Image.getDicomDataset(path)
                    newFilePath = SaveDICOM_Image.returnFilePath(path, suffix)
                    SaveDICOM_Image.saveDicomToFile(newDataset, output_path=newFilePath)
                    # The next lines perform an overwrite operation over the copied images
                    if patient_id:
                        SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "PatientID", patient_id)
                    if study_uid:
                        SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "StudyInstanceUID", study_uid)
                    if study_name:
                        SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "StudyDescription", study_name)
                    instance_uid = SaveDICOM_Image.generateUIDs(newDataset, seriesNumber=series_id, studyUID=study_uid)[2]
                    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SOPInstanceUID", instance_uid)
                    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesInstanceUID", series_uid)
                    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesNumber", series_id)
                    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", series_name)
                    #if hasattr(newDataset, "SeriesDescription"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SeriesDescription", series_name)
                    #elif hasattr(newDataset, "SequenceName"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "SequenceName", series_name)
                    #elif hasattr(newDataset, "ProtocolName"):
                    #    SaveDICOM_Image.overwriteDicomFileTag(newFilePath, "ProtocolName", series_name)
                    newImagePathList.append(newFilePath)
                self.objXMLReader.insertNewSeriesInXMLFile(imagePathList, newImagePathList, suffix, newSeriesName=series_name, newStudyName=study_name, newSubjectName=patient_id)
            return newImagePathList
        except Exception as e:
            print('Error in function GenericDICOMTools.mergeDicomIntoOneSeries: ' + str(e))
            logger.exception('Error in GenericDICOMTools.mergeDicomIntoOneSeries: ' + str(e))

    def generateSeriesIDs(self, inputPath, seriesNumber=None, studyUID=None):
        """
        This function generates and returns a SeriesUID and an InstanceUID.
        The SeriesUID is generated based on the StudyUID and on seriesNumber (if provided)
        The InstanceUID is generated based on SeriesUID.
        """
        logger.info("GenericDICOMTools.generateSeriesIDs called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                dataset = PixelArrayDICOMTools.getDICOMobject(inputPath)
                if seriesNumber is None:
                    (subjectID, studyID, seriesID) = self.objXMLReader.getImageParentIDs(inputPath)
                    seriesNumber = str(int(self.objXMLReader.getStudy(subjectID, studyID)[-1].attrib['id'].split('_')[0]) + 1)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                dataset = PixelArrayDICOMTools.getDICOMobject(inputPath[0])
                if seriesNumber is None:
                    (subjectID, studyID, seriesID) = self.objXMLReader.getImageParentIDs(inputPath[0])
                    seriesNumber = str(int(self.objXMLReader.getStudy(subjectID, studyID)[-1].attrib['id'].split('_')[0]) + 1)
            ids = SaveDICOM_Image.generateUIDs(dataset, seriesNumber=seriesNumber, studyUID=studyUID)
            seriesID = ids[0]
            seriesUID = ids[1]
            return seriesID, seriesUID
        except Exception as e:
            print('Error in function GenericDICOMTools.generateSeriesIDs: ' + str(e))
            logger.exception('Error in GenericDICOMTools.generateSeriesIDs: ' + str(e))

    @staticmethod
    def editDICOMTag(inputPath, dicomTag, newValue):
        """
        Overwrites all "dicomTag" of the DICOM files in "inputPath"
        with "newValue".
        """
        logger.info("GenericDICOMTools.editDICOMTag called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                SaveDICOM_Image.overwriteDicomFileTag(inputPath, dicomTag, newValue)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                for path in inputPath:
                    SaveDICOM_Image.overwriteDicomFileTag(path, dicomTag, newValue)
        except Exception as e:
            print('Error in GenericDICOMTools.editDICOMTag: ' + str(e))
            logger.exception('Error in GenericDICOMTools.editDICOMTag: ' + str(e))
        

class PixelArrayDICOMTools:

    def __repr__(self):
       return '{}'.format(self.__class__.__name__)
    
    @staticmethod
    def getPixelArrayFromDICOM(inputPath):
        """
        Returns the PixelArray of the DICOM file(s) in "inputPath".
        """
        logger.info("PixelArrayDICOMTools.getPixelArrayFromDICOM called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                pixelArray = ReadDICOM_Image.returnPixelArray(inputPath)
                return np.squeeze(pixelArray)
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                pixelArray = ReadDICOM_Image.returnSeriesPixelArray(inputPath)
                return np.squeeze(pixelArray)
            else:
                return None
        except Exception as e:
            print('Error in PixelArrayDICOMTools.getPixelArrayFromDICOM: ' + str(e))
            logger.exception('Error in PixelArrayDICOMTools.getPixelArrayFromDICOM: ' + str(e))

    @staticmethod
    def getDICOMobject(inputPath):
        """
        Returns the DICOM object (or list of DICOM objects) of the file(s) in "inputPath".
        """
        logger.info("PixelArrayDICOMTools.getDICOMobject called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                dataset = ReadDICOM_Image.getDicomDataset(inputPath)
                return dataset
            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                dataset = ReadDICOM_Image.getSeriesDicomDataset(inputPath)
                return dataset
            else:
                return None
        except Exception as e:
            print('Error in PixelArrayDICOMTools.getDICOMobject: ' + str(e))
            logger.exception('Error in PixelArrayDICOMTools.getDICOMobject: ' + str(e))

    def writeNewPixelArray(self, pixelArray, inputPath, suffix, series_id=None, series_uid=None, series_name=None, parametric_map=None, colourmap=None, output_dir=None):
        """
        Saves the "pixelArray" into new DICOM files with a new series, based
        on the "inputPath" and on the "suffix".
        """
        logger.info("PixelArrayDICOMTools.writeNewPixelArray called")
        try:
            if isinstance(inputPath, str) and os.path.exists(inputPath):
                numImages = 1
                derivedImageList = [pixelArray]
                derivedImageFilePath = SaveDICOM_Image.returnFilePath(inputPath, suffix, output_folder=output_dir)
                derivedImagePathList = [derivedImageFilePath]

            elif isinstance(inputPath, list) and os.path.exists(inputPath[0]):
                if hasattr(ReadDICOM_Image.getDicomDataset(inputPath[0]), 'PerFrameFunctionalGroupsSequence'):
                    # If it's Enhanced MRI
                    numImages = 1
                    derivedImageList = [pixelArray]
                    derivedImageFilePath = SaveDICOM_Image.returnFilePath(inputPath[0], suffix, output_folder=output_dir)
                    derivedImagePathList = [derivedImageFilePath]
                else:
                    # Iterate through list of images (slices) and save the resulting Map for each DICOM image
                    numImages = (1 if len(np.shape(pixelArray)) < 3 else np.shape(pixelArray)[0])
                    derivedImagePathList = []
                    derivedImageList = []
                    for index in range(numImages):
                        derivedImageFilePath = SaveDICOM_Image.returnFilePath(inputPath[index], suffix, output_folder=output_dir)
                        derivedImagePathList.append(derivedImageFilePath)
                        if numImages==1:
                            derivedImageList.append(pixelArray)
                        else:
                            derivedImageList.append(pixelArray[index, ...])
                    if len(inputPath) > len(derivedImagePathList):
                        inputPath = inputPath[:len(derivedImagePathList)]

            if numImages == 1:
                if isinstance(inputPath, list):
                    inputPath = inputPath[0]
                SaveDICOM_Image.saveNewSingleDicomImage(derivedImagePathList[0], (''.join(inputPath)), derivedImageList[0], suffix, series_id=series_id, series_uid=series_uid, series_name=series_name, list_refs_path=[(''.join(inputPath))], parametric_map=parametric_map, colourmap=colourmap)
                # Record derived image in XML file
                self.objXMLReader.insertNewImageInXMLFile((''.join(inputPath)), derivedImagePathList[0], suffix, newSeriesName=series_name)
            else:
                SaveDICOM_Image.saveDicomNewSeries(derivedImagePathList, inputPath, derivedImageList, suffix, series_id=series_id, series_uid=series_uid, series_name=series_name, list_refs_path=[inputPath], parametric_map=parametric_map, colourmap=colourmap)
                # Insert new series into the DICOM XML file
                self.objXMLReader.insertNewSeriesInXMLFile(inputPath, derivedImagePathList, suffix, newSeriesName=series_name)            
                
            return derivedImagePathList

        except Exception as e:
            print('Error in PixelArrayDICOMTools.writeNewPixelArray: ' + str(e))
            logger.exception('Error in PixelArrayDICOMTools.writeNewPixelArray: ' + str(e))

    @staticmethod
    def overwritePixelArray(pixelArray, inputPath):
        """
        Overwrites the DICOM files in the "pixelArray" into new DICOM files with a new series, based
        on the "inputPath" and on the "suffix".
        """
        logger.info("PixelArrayDICOMTools.overwritePixelArray called")
        try:
            if isinstance(inputPath, list) and len(inputPath) > 1:
                datasetList = ReadDICOM_Image.getSeriesDicomDataset(inputPath)
                for index, dataset in enumerate(datasetList):
                    modifiedDataset = SaveDICOM_Image.createNewPixelArray(pixelArray[index], dataset)
                    SaveDICOM_Image.saveDicomToFile(modifiedDataset, output_path=inputPath[index])
            else:
                dataset = ReadDICOM_Image.getDicomDataset(inputPath)
                modifiedDataset = SaveDICOM_Image.createNewPixelArray(pixelArray, dataset)
                SaveDICOM_Image.saveDicomToFile(modifiedDataset, output_path=inputPath)
        except Exception as e:
            print('Error in PixelArrayDICOMTools.overwritePixelArray: ' + str(e))
            logger.exception('Error in PixelArrayDICOMTools.overwritePixelArray: ' + str(e))


