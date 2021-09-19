import os
from PyQt5.QtWidgets import QFileDialog
import CoreModules.WEASEL.WriteXMLfromDICOM as WriteXMLfromDICOM
from CoreModules.TreeView import TreeView
from Displays.UserInput import userInput 

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

    def images(self, msg=''):
        """
        Returns a list of Images checked by the user.
        """
        list = self.objXMLReader.checkedImages()
        if list == []:
            if msg != '':
                self.message(msg=msg)
        return list

    def series(self, msg=''):
        """
        Returns a list of Series checked by the user.
        """
        list = self.objXMLReader.checkedSeries()
        if list == []:
            if msg != '':
                self.message(msg=msg)
        return list

    def studies(self, msg=''):
        """
        Returns a list of Studies checked by the user.
        """
        list = self.objXMLReader.checkedStudies()
        if list == []:
            if msg != '':
                self.message(msg=msg)
        return list

    def subjects(self, msg=''):
        """
        Returns a list of Subjects checked by the user.
        """
        list = self.objXMLReader.checkedSubjects()
        if list == []:
            if msg != '':
                self.message(msg=msg)
        return list

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