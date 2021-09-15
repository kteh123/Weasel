import DICOM.ReadDICOM_Image as ReadDICOM_Image
import logging
logger = logging.getLogger(__name__)


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


def moveSeriesInXMLFile(self, subjectID, studyID, seriesID, newSubjectID, newStudyID, newSeriesID, suffix):
    """NOT IN USE - SEEMS WORK IN PROGRESS (05/09/2021)"""
    try:
        #self.objXMLReader.insertNewSeriesInXML()#(imageName, imageName, newSubjectID, newStudyID, newSeriesID, suffix)
        series = self.objXMLReader.getStudy(subjectID, studyID)
        if len(series) == 1:
            removeOneStudyFromSubject(self, subjectID, studyID)
        elif len(series) > 1:
            self.objXMLReader.removeOneSeriesFromStudy(subjectID, studyID, seriesID)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile.moveSeriesInXMLFile: ' + str(e)) 
        logger.error('Error in InterfaceDICOMXMLFile.moveSeriesInXMLFile: ' + str(e))


def moveStudyInXMLFile(self, subjectID, studyID, newSubjectID, newStudyID, suffix):
    try:
        #self.objXMLReader.insertNewStudyInXML()
        study = self.objXMLReader.getSubject(subjectID)
        if len(study) == 1:
            removeSubjectinXMLFile(self, subjectID)
        elif len(study) > 1:
            self.objXMLReader.removeOneStudyFromSubject(subjectID, studyID)
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile.moveStudyInXMLFile: ' + str(e)) 
        logger.error('Error in InterfaceDICOMXMLFile.moveStudyInXMLFile: ' + str(e))

  
def removeOneSeriesFromStudy(self, origImageList):
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
    

def insertNewSubjectInXMLFile(self, newSubjectID, suffix, studyList=[]):
    """NOT IN USE. CAN'T WORK BECAUSE subjectID not defined"""
    try:
        logger.info("InterfaceDICOMXMLFile insertNewSubjectInXMLFile called")
        self.objXMLReader.insertNewSubjectinXML(studyList, subjectID, suffix)
        self.statusBar.showMessage('New subject created: - ' + newSubjectID)
        return newSubjectID
    except Exception as e:
        print('Error in InterfaceDICOMXMLFile.insertNewSubjectInXMLFile: ' + str(e))
        logger.error('Error in InterfaceDICOMXMLFile.insertNewSubjectInXMLFile: ' + str(e))