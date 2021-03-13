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
            #studyID = self.selectedStudy 
            #seriesID = self.selectedSeries
            (subjectID, studyID, seriesID) = treeView.getPathParentNode(self, imagePath)
            #if self.selectedImagePath:
            #    imagePath = self.selectedImagePath
            #else:
            #    imagePath = None
            #returns new series ID or existing series ID as appropriate
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
                return getNewSeriesName(subjectID, studyID, dataset, suffix, newSeriesName=newSeriesName)
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
        #Get current study & series IDs
        #studyID = self.selectedStudy 
        #seriesID = self.selectedSeries
        # Get a new series ID by default
        (subjectID, studyID, seriesID) = treeView.getPathParentNode(self, origImageList[0])
        dataset = readDICOM_Image.getDicomDataset(newImageList[0])
        newSeriesID = getNewSeriesName(self, subjectID, studyID, dataset, suffix, newSeriesName=newSeriesName) # If developer sets seriesName
        self.objXMLReader.insertNewSeriesInXML(origImageList, 
                    newImageList, subjectID, studyID, newSeriesID, seriesID, suffix)
        self.statusBar.showMessage('New series created: - ' + newSeriesID)
        return newSeriesID
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile.insertNewSeriesInXMLFile: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile.insertNewSeriesInXMLFile: ' + str(e))


def removeImageFromXMLFile(self, imageFileName):
    """Removes an image from the DICOM XML file"""
    try:
        logger.info("InterfaceDICOMXMLFile removeImageFromXMLFile called")
        (subjectID, studyID, seriesID) = treeView.getPathParentNode(self, imageFileName)
        images = self.objXMLReader.getImageList(subjectID, studyID, seriesID)
        if len(images) == 1:
            self.objXMLReader.removeSeriesFromXMLFile(subjectID, studyID, seriesID)
        elif len(images) > 1:
            self.objXMLReader.removeOneImageFromSeries(subjectID, studyID, seriesID, imageFileName)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile removeImageFromXMLFile: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile removeImageFromXMLFile: ' + str(e))


def removeMultipleImagesFromXMLFile(self, origImageList):
    """Removes a whole series from the DICOM XML file"""
    try:
        logger.info("InterfaceDICOMXMLFile removeSeriesFromXMLFile called")
        for image in origImageList:
            removeImageFromXMLFile(self, image)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile removeSeriesFromXMLFile: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile removeSeriesFromXMLFile: ' + str(e))


def removeSeriesFromXMLFile(self, origImageList):
    """Removes a whole series from the DICOM XML file"""
    try:
        logger.info("InterfaceDICOMXMLFile removeSeriesFromXMLFile called")
        (subjectID, studyID, seriesID) = treeView.getPathParentNode(self, origImageList[0])
        self.objXMLReader.removeSeriesFromXMLFile(subjectID, studyID, seriesID)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile removeSeriesFromXMLFile: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile removeSeriesFromXMLFile: ' + str(e))
    

def renameSeriesinXMLFile(self, imageList, series_id=None, series_name=None):
    """Removes a whole series from the DICOM XML file"""
    try:
        logger.info("InterfaceDICOMXMLFile renameSeriesinXMLFile called")
        (subjectID, studyID, seriesID) = treeView.getPathParentNode(self, imageList[0])
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
        print('Error in InterfaceDICOMXMLFile removeSeriesFromXMLFile: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile removeSeriesFromXMLFile: ' + str(e))
