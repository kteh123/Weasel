"""
Collection of methods for reading and writing DICOM within a Pipeline.
"""

import os
from PyQt5.QtWidgets import QFileDialog
import CoreModules.WriteXMLfromDICOM as WriteXMLfromDICOM
from CoreModules.TreeView import TreeView
from Displays.UserInput import userInput
from DICOM.Classes import ImagesList, SeriesList, StudyList, SubjectList

import logging
logger = logging.getLogger(__name__)

class ReadWrite():

    def log(self, message):
        """
        Prints the content in the input argument "message" to the terminal and logs that information into the "Activity_Log.log" file.
        """
        print(message)
        logger.info(message)

    def log_error(self, message):
        """
        Prints the content in the input argument "message" to the terminal and logs that error and its details into the "Activity_Log.log" file.
        """
        print(message)
        logger.exception(message)

    def images(self, msg=''):
        """
        Returns a list of Images checked by the user.
        """
        list = self.objXMLReader.checkedImages()
        if list == []:
            if msg != '':
                self.message(msg=msg)
        return list

    def images_list(self, normal_list_of_images):
        """
        Returns an instance of ImagesList provided manually by the user.
        """
        return ImagesList(normal_list_of_images)
    
    def series(self, msg=''):
        """
        Returns a list of Series checked by the user.
        """
        list = self.objXMLReader.checkedSeries()
        if list == []:
            if msg != '':
                self.message(msg=msg)
        return list

    def series_list(self, normal_list_of_series):
        """
        Returns an instance of SeriesList provided manually by the user.
        """
        return SeriesList(normal_list_of_series)

    def studies(self, msg=''):
        """
        Returns a list of Studies checked by the user.
        """
        list = self.objXMLReader.checkedStudies()
        if list == []:
            if msg != '':
                self.message(msg=msg)
        return list

    def studies_list(self, normal_list_of_studies):
        """
        Returns an instance of StudyList provided manually by the user.
        """
        return StudyList(normal_list_of_studies)

    def subjects(self, msg=''):
        """
        Returns a list of Subjects checked by the user.
        """
        list = self.objXMLReader.checkedSubjects()
        if list == []:
            if msg != '':
                self.message(msg=msg)
        return list

    def subjects_list(self, normal_list_of_subjects):
        """
        Returns an instance of SubjectList provided manually by the user.
        """
        return SubjectList(normal_list_of_subjects)

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
        self.DICOMFolder = self.select_folder(title="Select the folder with DICOM data")
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

    def user_input(self, *fields, help_text="", title="User input window"):
        """
        Launches a window to get user input.
        """ 
        return userInput(*fields, help_text=help_text, title=title)       

    def data_folder(self):
        """
        Returns the default folder for saving & loading data.
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