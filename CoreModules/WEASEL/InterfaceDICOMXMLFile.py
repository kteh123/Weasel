import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image
import CoreModules.WEASEL.TreeView as treeView
import logging
logger = logging.getLogger(__name__)


def insertNewImageInXMLFile(self, imagePath, newImageFileName, suffix, newSeriesName=None):
    """This function inserts information regarding a new image 
       in the DICOM XML file
    """
    try:
        logger.info("InterfaceDICOMXMLFile insertNewImageInXMLFile called")
        #(subjectID, studyID, seriesID) = treeView.getPathParentNode(self, imagePath)
        (subjectID, studyID, seriesID) = self.objXMLReader.getImageParentIDs(imagePath)
        return self.objXMLReader.insertNewImageInXML(imagePath,
               newImageFileName, subjectID, studyID, seriesID, suffix, newSeriesName=newSeriesName)
        
    except Exception as e:
        print('Error in insertNewImageInXMLFile: ' + str(e))
        logger.error('Error in insertNewImageInXMLFile: ' + str(e))


def getNewSeriesName(self, subjectID, studyID, dataset, suffix, newSeriesName=None):
    """This function uses recursion to find the next available
    series name.  A new series name is created by adding a suffix
    at the end of an existing series name. """
    try:
        # Swapped SeriesNumber with SeriesDescription
        if newSeriesName:
            seriesID = str(dataset.SeriesNumber) + "_" + newSeriesName
        else:
            if hasattr(dataset, "SeriesDescription"):
                seriesID = str(dataset.SeriesNumber) + "_" + dataset.SeriesDescription
            elif hasattr(dataset, "SequenceName"):
                seriesID = str(dataset.SeriesNumber) + "_" + dataset.SequenceName
            elif hasattr(dataset, "ProtocolName"):
                seriesID = str(dataset.SeriesNumber) + "_" + dataset.ProtocolName
        imageList = self.objXMLReader.getImageList(subjectID, studyID, seriesID)
        if imageList:
            #A series of images already exists 
            #for the series called seriesID
            #so make another new series ID 
            #by adding the suffix to the previous
            #new series ID
            if newSeriesName:
                dataset.SeriesDescription = newSeriesName
                return getNewSeriesName(subjectID, studyID, dataset, suffix, newSeriesName=None)
            else:
                if hasattr(dataset, "SeriesDescription"):
                    dataset.SeriesDescription = dataset.SeriesDescription + suffix
                elif hasattr(dataset, "SequenceName"):
                    dataset.SequenceName = dataset.SequenceName + suffix
                elif hasattr(dataset, "ProtocolName"):
                    dataset.ProtocolName = dataset.ProtocolName + suffix
                return getNewSeriesName(subjectID, studyID, dataset, suffix)
        else:
            logger.info("InterfaceDICOMXMLFile getNewSeriesName returns seriesID {}".format(seriesID))
            return seriesID
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile.getNewSeriesName: ' + str(e))
            

def insertNewSeriesInXMLFile(self, origImageList, newImageList, suffix, newSeriesName=None):
    """Creates a new series to hold the series of New images"""
    try:
        logger.info("InterfaceDICOMXMLFile insertNewSeriesInXMLFile called")
        #(subjectID, studyID, seriesID) = treeView.getPathParentNode(self, origImageList[0])
        (subjectID, studyID, seriesID) = self.objXMLReader.getImageParentIDs(origImageList[0])
        dataset = readDICOM_Image.getDicomDataset(newImageList[0])
        newSeriesID = getNewSeriesName(self, subjectID, studyID, dataset, suffix, newSeriesName=newSeriesName) # If developer sets seriesName
        self.objXMLReader.insertNewSeriesInXML(origImageList, 
                    newImageList, subjectID, studyID, newSeriesID, seriesID, suffix)
        self.statusBar.showMessage('New series created: - ' + newSeriesID)
        return newSeriesID
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile.insertNewSeriesInXMLFile: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile.insertNewSeriesInXMLFile: ' + str(e))


def insertNewStudyInXMLFile(self, subjectID, newStudyID, suffix, seriesList = []):
    """Creates a new study to hold the new series"""
    try:
        logger.info("InterfaceDICOMXMLFile insertNewStudyInXMLFile called")
        self.objXMLReader.insertNewStudyinXML(seriesList, subjectID, newStudyID, suffix)
        self.statusBar.showMessage('New study created: - ' + newStudyID)
        return newStudyID
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile.insertNewStudyInXMLFile: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile.insertNewStudyInXMLFile: ' + str(e))


def insertNewSubjectInXMLFile(self, newSubjectID, suffix, studyList = []):
    """Creates a new study to hold the new series"""
    try:
        logger.info("InterfaceDICOMXMLFile insertNewSubjectInXMLFile called")
        self.objXMLReader.insertNewSubjectinXML(studyList, subjectID, suffix)
        self.statusBar.showMessage('New subject created: - ' + newSubjectID)
        return newSubjectID
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile.insertNewStudyInXMLFile: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile.insertNewStudyInXMLFile: ' + str(e))


def removeImageFromXMLFile(self, imageFileName):
    """Removes an image from the DICOM XML file"""
    try:
        logger.info("InterfaceDICOMXMLFile removeImageFromXMLFile called")
        #(subjectID, studyID, seriesID) = treeView.getPathParentNode(self, imageFileName)
        (subjectID, studyID, seriesID) = self.objXMLReader.getImageParentIDs(imageFileName)
        images = self.objXMLReader.getImageList(subjectID, studyID, seriesID)
        if len(images) == 1:
            removeOneSeriesFromStudy(self, subjectID, studyID, seriesID)
        elif len(images) > 1:
            self.objXMLReader.removeOneImageFromSeries(subjectID, studyID, seriesID, imageFileName)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile removeImageFromXMLFile: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile removeImageFromXMLFile: ' + str(e))


def removeMultipleImagesFromXMLFile(self, origImageList):
    """Removes a list of images from the DICOM XML file"""
    try:
        logger.info("InterfaceDICOMXMLFile removeOneSeriesFromStudy called")
        for image in origImageList:
            removeImageFromXMLFile(self, image)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile removeOneSeriesFromStudy: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile removeOneSeriesFromStudy: ' + str(e))


def removeOneSeriesFromStudy(self, origImageList):
    """Removes a whole series from the DICOM XML file"""
    try:
        logger.info("InterfaceDICOMXMLFile removeOneSeriesFromStudy called")
        #(subjectID, studyID, seriesID) = treeView.getPathParentNode(self, origImageList[0])
        (subjectID, studyID, seriesID) = self.objXMLReader.getImageParentIDs(origImageList[0])
        seriesList = self.objXMLReader.getStudy(subjectID, studyID)
        if len(seriesList) == 1:
            removeOneStudyFromSubject(self, subjectID, studyID)
        elif len(seriesList) > 1:
            self.objXMLReader.removeOneSeriesFromStudy(subjectID, studyID, seriesID)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile removeOneSeriesFromStudy: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile removeOneSeriesFromStudy: ' + str(e))


def removeOneSeriesFromStudy(self, subjectID, studyID, seriesID):
    """Removes a whole series from the DICOM XML file"""
    try:
        logger.info("InterfaceDICOMXMLFile removeOneSeriesFromStudy called")
        seriesList = self.objXMLReader.getStudy(subjectID, studyID)
        if len(seriesList) == 1:
            removeOneStudyFromSubject(self, subjectID, studyID)
        elif len(seriesList) > 1:
            self.objXMLReader.removeOneSeriesFromStudy(subjectID, studyID, seriesID)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile removeOneSeriesFromStudy: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile removeOneSeriesFromStudy: ' + str(e))


def removeOneStudyFromSubject(self, subjectID, studyID):
    """Removes a study from the given subject from the DICOM XML file"""
    try:
        logger.info("InterfaceDICOMXMLFile removeOneStudyFromSubject called")
        studiesList = self.objXMLReader.getSubject(subjectID)
        if len(studiesList) == 1:
            removeSubjectinXMLFile(self, subjectID)
        elif len(studiesList) > 1:
            self.objXMLReader.removeOneStudyFromSubject(subjectID, studyID)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile removeOneStudyFromSubject: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile removeOneStudyFromSubject: ' + str(e))
    

def removeAllStudiesFromSubject(self, subjectID):
    """Removes all studies from a subject from the DICOM XML file"""
    try:
        logger.info("InterfaceDICOMXMLFile removeAllStudiesFromSubject called")
        subject = self.objXMLReader.getSubject(subjectID)
        for study in subject:
            studyID = study.attrib['id']
            removeOneStudyFromSubject(subjectID, studyID)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile removeAllStudiesFromSubject: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile removeAllStudiesFromSubject: ' + str(e))
    

def removeSubjectinXMLFile(self, subjectID):
    """Removes a subject from the DICOM XML file"""
    try:
        logger.info("InterfaceDICOMXMLFile removeSubject called")
        self.objXMLReader.removeSubjectFromXMLFile(subjectID)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile removeSubject: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile removeSubject: ' + str(e))


def renameSeriesinXMLFile(self, imageList, series_id=None, series_name=None):
    """Renames a whole series in the DICOM XML file"""
    try:
        logger.info("InterfaceDICOMXMLFile renameSeriesinXMLFile called")
        #(subjectID, studyID, seriesID) = treeView.getPathParentNode(self, imageList[0])
        (subjectID, studyID, seriesID) = self.objXMLReader.getImageParentIDs(imageList[0])
        seriesNumber = str(readDICOM_Image.getDicomDataset(imageList[0]).SeriesNumber) if series_id is None else str(series_id)
        try:
            newName = str(readDICOM_Image.getDicomDataset(imageList[0]).SeriesDescription) if series_name is None else str(series_name)
        except:
            try:
                newName = str(readDICOM_Image.getDicomDataset(imageList[0]).SequenceName) if series_name is None else str(series_name)
            except:
                newName = str(readDICOM_Image.getDicomDataset(imageList[0]).ProtocolName) if series_name is None else str(series_name)
        xmlSeriesName = seriesNumber + "_" + newName
        self.objXMLReader.renameSeriesinXMLFile(subjectID, studyID, seriesID, xmlSeriesName)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile removeOneSeriesFromStudy: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile removeOneSeriesFromStudy: ' + str(e))


def renameStudyinXMLFile(self, subjectID, studyID, newStudyID, newSubject=None):
    """Renames a whole series in the DICOM XML file"""
    try:
        logger.info("InterfaceDICOMXMLFile renameStudyinXMLFile called")
        self.objXMLReader.renameStudyInXMLFile(subjectID, studyID, newStudyID)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile renameStudyinXMLFile: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile renameStudyinXMLFile: ' + str(e))
    

def renameSubjectinXMLFile(self, subjectID, newSubjectID):
    """Renames a whole series in the DICOM XML file"""
    try:
        logger.info("InterfaceDICOMXMLFile renameStudyinXMLFile called")
        self.objXMLReader.renameSubjectInXMLFile(subjectID, newSubjectID)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile renameStudyinXMLFile: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile renameStudyinXMLFile: ' + str(e))