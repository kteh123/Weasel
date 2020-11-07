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
                   newImageFileName, studyID, seriesID, suffix, newSeriesName=newSeriesName)
            
        except Exception as e:
            print('Error in insertNewImageInXMLFile: ' + str(e))
            logger.error('Error in insertNewImageInXMLFile: ' + str(e))


def getNewSeriesName(self, studyID, dataset, suffix, newSeriesName=None):
    """This function uses recursion to find the next available
    series name.  A new series name is created by adding a suffix
    at the end of an existing series name. """
    try:
        # Swapped SeriesNumber with SeriesDescription
        if newSeriesName:
            seriesID = str(dataset.SeriesNumber) + "_" + newSeriesName
        else:
            seriesID = str(dataset.SeriesNumber) + "_" + dataset.SeriesDescription
        imageList = self.objXMLReader.getImageList(studyID, seriesID)
        if imageList:
            #A series of images already exists 
            #for the series called seriesID
            #so make another new series ID 
            #by adding the suffix to the previous
            #new series ID
            if newSeriesName:
                dataset.SeriesDescription = newSeriesName
                return getNewSeriesName(studyID, dataset, suffix, newSeriesName=newSeriesName)
            else:
                dataset.SeriesDescription = dataset.SeriesDescription + suffix
                return getNewSeriesName(studyID, dataset, suffix)
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
        newSeriesID = getNewSeriesName(self, studyID, dataset, suffix, newSeriesName=newSeriesName) # If developer sets seriesName
        self.objXMLReader.insertNewSeriesInXML(origImageList, 
                    newImageList, studyID, newSeriesID, seriesID, suffix)
        self.statusBar.showMessage('New series created: - ' + newSeriesID)
        return  newSeriesID
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile.insertNewSeriesInXMLFile: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile.insertNewImageInXMLFile: ' + str(e))


def removeImageFromXMLFile(self, imageFileName):
    """Removes an image from the DICOM XML file"""
    try:
        logger.info("InterfaceDICOMXMLFile removeImageFromXMLFile called")
        (subjectID, studyID, seriesID) = treeView.getPathParentNode(self, imageFileName)
        images = self.objXMLReader.getImageList(studyID, seriesID)
        if len(images) == 1:
            self.objXMLReader.removeSeriesFromXMLFile(studyID, seriesID)
        elif len(images) > 1:
            self.objXMLReader.removeOneImageFromSeries(studyID, seriesID, imageFileName)
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
        self.objXMLReader.removeSeriesFromXMLFile(studyID, seriesID)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile removeSeriesFromXMLFile: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile removeSeriesFromXMLFile: ' + str(e))
    

def renameSeriesinXMLFile(self, imageList, newName):
    """Removes a whole series from the DICOM XML file"""
    try:
        logger.info("InterfaceDICOMXMLFile renameSeriesinXMLFile called")
        (subjectID, studyID, seriesID) = treeView.getPathParentNode(self, imageList[0])
        #seriesNumber = seriesID.split("_", 1)[0] # MAYBE THIS SHOULD COME FROM THE DICOM TAG?
        seriesNumber = str(readDICOM_Image.getDicomDataset(imageList[0]).SeriesNumber)
        xmlSeriesName = seriesNumber + "_" + newName
        self.objXMLReader.renameSeriesinXMLFile(studyID, seriesID, xmlSeriesName)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile removeSeriesFromXMLFile: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile removeSeriesFromXMLFile: ' + str(e))
