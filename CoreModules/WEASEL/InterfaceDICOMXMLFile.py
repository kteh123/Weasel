import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image
import logging
logger = logging.getLogger(__name__)


def insertNewImageInXMLFile(self, newImageFileName, suffix):
        """This function inserts information regarding a new image 
         in the DICOM XML file
       """
        try:
            logger.info("InterfaceDICOMXMLFile insertNewImageInXMLFile called")
            studyID = self.selectedStudy 
            seriesID = self.selectedSeries
            if self.selectedImagePath:
                imagePath = self.selectedImagePath
            else:
                imagePath = None
            #returns new series ID or existing series ID
            #as appropriate
            return self.objXMLReader.insertNewImageInXML(imagePath,
                   newImageFileName, studyID, seriesID, suffix)
            
        except Exception as e:
            print('Error in insertNewImageInXMLFile: ' + str(e))
            logger.error('Error in insertNewImageInXMLFile: ' + str(e))


def getNewSeriesName(self, studyID, dataset, suffix):
    """This function uses recursion to find the next available
    series name.  A new series name is created by adding a suffix
    at the end of an existing series name. """
    try:
        seriesID = dataset.SeriesDescription + "_" + str(dataset.SeriesNumber)
        imageList = self.objXMLReader.getImageList(studyID, seriesID)
        if imageList:
            #A series of images already exists 
            #for the series called seriesID
            #so make another new series ID 
            #by adding the suffix to the previous
            #new series ID
            dataset.SeriesDescription = dataset.SeriesDescription + suffix
            return getNewSeriesName(studyID, dataset, suffix)
        else:
            logger.info("InterfaceDICOMXMLFile getNewSeriesName returns seriesID {}".format(seriesID))
            return seriesID
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile.getNewSeriesName: ' + str(e))
            


def insertNewSeriesInXMLFile(self, origImageList, newImageList, suffix):
    """Creates a new series to hold the series of New images"""
    try:
        logger.info("InterfaceDICOMXMLFile insertNewSeriesInXMLFile called")
        #Get current study & series IDs
        studyID = self.selectedStudy 
        seriesID = self.selectedSeries 
        #Get a new series ID
        dataset = readDICOM_Image.getDicomDataset(newImageList[0])
        newSeriesID = getNewSeriesName(self, studyID, dataset, suffix)
        self.objXMLReader.insertNewSeriesInXML(origImageList, 
                    newImageList, studyID, newSeriesID, seriesID, suffix)
        self.statusBar.showMessage('New series created: - ' + newSeriesID)
        return  newSeriesID
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile.insertNewSeriesInXMLFile: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile.insertNewImageInXMLFile: ' + str(e))  
