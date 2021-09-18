import os
from PyQt5.QtWidgets import QFileDialog
import CoreModules.WEASEL.WriteXMLfromDICOM as WriteXMLfromDICOM
from CoreModules.TreeView import TreeView
from Displays.UserInput import userInput 
from DICOM.Classes import (ImagesList, SeriesList, StudyList, SubjectList, Image, Series, Study, Subject)

import logging
logger = logging.getLogger(__name__)

class ReadWrite():
    """
    Methods for reading and writing within a Pipeline 
    """
    def log(self, message):
        print(message)
        logger.info(message)

    def log_error(self, message):
        print(message)
        logger.exception(message)

    def images(self, msg=None):
        """
        Returns a list of Images checked by the user.
        """
        imagesList = [] 
        images = self.objXMLReader.checkedImageList
        if images == []:
            if self.cmd == True:
                print("=====================================")
                print(msg)
                print("=====================================")
            elif msg is not None:
                self.message(msg=msg)
        else:
            for image in images:
                id = self.objXMLReader.objectID(image)
                newImage = Image(self, id[0], id[1], id[2], id[3])
                imagesList.append(newImage)
        return ImagesList(imagesList)

    def series(self, msg=None):
        """
        Returns a list of Series checked by the user.
        """
        seriesList = []  
        checked_series = self.objXMLReader.checkedSeriesList     
        if checked_series == []:
            if self.cmd == True:
                print("=====================================")
                print(msg)
                print("=====================================")
            elif msg is not None:
                self.message(msg=msg)
        else:
            for series in checked_series:
                images = [image.find('name').text for image in series]
                id = self.objXMLReader.objectID(series)
                newSeries = Series(self, id[0], id[1], id[2], listPaths=images)
                seriesList.append(newSeries)
        return SeriesList(seriesList)

    def studies(self, msg=None):
        """
        Returns a list of Studies checked by the user.
        """
        studyList = []
        checked_studies = self.objXMLReader.checkedStudyList 
        if checked_studies == []:
            if self.cmd == True:
                print("=====================================")
                print(msg)
                print("=====================================")
            elif msg is not None:
                self.message(msg=msg)
        else:
            for study in checked_studies:
                id = self.objXMLReader.objectID(study)
                newStudy = Study(self, id[0], id[1])
                studyList.append(newStudy)
        return StudyList(studyList)

    def subjects(self, msg=None):
        """
        Returns a list of Subjects checked by the user.
        """
        subjectList = []
        checked_subjects = self.objXMLReader.checkedSubjectList
        if checked_subjects == []:
            if self.cmd == True:
                print("=====================================")
                print(msg)
                print("=====================================")
            elif msg is not None:
                self.message(msg=msg)
        else:
            for subject in checked_subjects:
                id = self.objXMLReader.objectID(subject)
                newSubject = Subject(self, id[0])
                subjectList.append(newSubject)    
        return SubjectList(subjectList)

    def read_dicom_folder(self):
        """
        Read a DICOM folder, create XML and refresh display.
        """
        if self.DICOMFolder:
            self.close_subwindows()
            self.cursor_arrow_to_hourglass()
            XML_File_Path = WriteXMLfromDICOM.makeDICOM_XML_File(self, self.DICOMFolder)
            self.cursor_hourglass_to_arrow()
            self.treeView = TreeView(self, XML_File_Path)
              
    def open_dicom_folder(self): 
        """
        Open a DICOM folder and update display.
        """ 
        self.DICOMFolder = WriteXMLfromDICOM.getScanDirectory(self)
        if self.DICOMFolder:
            self.close_subwindows()
            self.cursor_arrow_to_hourglass()
            if WriteXMLfromDICOM.existsDICOMXMLFile(self.DICOMFolder):
                XML_File_Path = self.DICOMFolder + '//' + os.path.basename(self.DICOMFolder) + '.xml'
            else:
                XML_File_Path = WriteXMLfromDICOM.makeDICOM_XML_File(self, self.DICOMFolder)
            self.cursor_hourglass_to_arrow() 
            self.treeView = TreeView(self, XML_File_Path) 
             
    def close_dicom_folder(self):
        """
        Closes the DICOM folder and updates display.
        """  
        self.close_subwindows()
        self.treeView.close()  
        self.DICOMFolder = ''  

    def user_input(self, *fields, title="User input window"):
        """
        Launches a window to get user input.
        """ 
        return userInput(*fields, title=title)       

    def data_folder(self):
        """
        Returns the default folder for saving & loading data
        """
        return self.weaselDataFolder
    
    def select_folder(self, title="Select Folder", initial_folder=None):
        """
        Prompts a native FileDialog window where the user can select the desired folder in the system's file explorer.
        """
        if initial_folder is None:
            initial_folder = self.data_folder()
        scan_directory = QFileDialog.getExistingDirectory(self, title, initial_folder, QFileDialog.ShowDirsOnly)
        if scan_directory == '':
            return None
        else:
            return scan_directory
    
    def select_file_to_read(self, title='Save file as ...', initial_folder=None, extension="All files (*.*)"):
        """
        Prompts a native FileDialog window where the user can select the desired file to read in the system's file explorer.
        """
        if initial_folder is None:
            initial_folder = self.data_folder()
        filename, _ = QFileDialog.getOpenFileName(self, title, initial_folder, extension)
        if filename == '':
            return None
        else:
            return filename

    def select_file_to_save(self, title='Save file as ...', initial_folder=None, extension="All files (*.*)"):
        """
        Prompts a native FileDialog window where the user can select the desired file to save in the system's file explorer.
        """
        if initial_folder is None:
            initial_folder = self.data_folder()
        filename, _ = QFileDialog.getSaveFileName(self, title, initial_folder, extension)
        if filename == '':
            return None
        else:
            return filename