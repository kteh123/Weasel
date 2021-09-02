import os
from PyQt5.QtWidgets import QFileDialog
import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.WriteXMLfromDICOM as WriteXMLfromDICOM
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
        treeView.buildListsCheckedItems(self)
        if self.checkedImageList == []:
            if self.cmd == True:
                print("=====================================")
                print(msg)
                print("=====================================")
            elif msg is not None:
                self.showMessageWindow(msg=msg)
        else:
            for image in self.checkedImageList:
                newImage = Image(self, image[0], image[1], image[2], image[3])
                imagesList.append(newImage)
        return ImagesList(imagesList)

    def series(self, msg=None):
        """
        Returns a list of Series checked by the user.
        """
        seriesList = []       
        treeView.buildListsCheckedItems(self)
        if self.checkedSeriesList == []:
            if self.cmd == True:
                print("=====================================")
                print(msg)
                print("=====================================")
            elif msg is not None:
                self.showMessageWindow(msg=msg)
        else:
            for series in self.checkedSeriesList:
                images = self.objXMLReader.getImagePathList(series[0], series[1], series[2])
                newSeries = Series(self, series[0], series[1], series[2], listPaths=images)
                seriesList.append(newSeries)
        return SeriesList(seriesList)

    def studies(self, msg=None):
        """
        Returns a list of Studies checked by the user.
        """
        studyList = []
        treeView.buildListsCheckedItems(self)
        if self.checkedStudyList == []:
            if self.cmd == True:
                print("=====================================")
                print(msg)
                print("=====================================")
            elif msg is not None:
                self.showMessageWindow(msg=msg)
        else:
            for study in self.checkedStudyList:
                newStudy = Study(self, study[0], study[1])
                studyList.append(newStudy)
        return StudyList(studyList)

    def subjects(self, msg=None):
        """
        Returns a list of Subjects checked by the user.
        """
        subjectList = []
        treeView.buildListsCheckedItems(self)
        if self.checkedSubjectList == []:
            if self.cmd == True:
                print("=====================================")
                print(msg)
                print("=====================================")
            elif msg is not None:
                self.showMessageWindow(msg=msg)
        else:
            for subject in self.checkedSubjectList:
                newSubject = Subject(self, subject)
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
            treeView.makeDICOMStudiesTreeView(self, XML_File_Path)
              
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
            treeView.makeDICOMStudiesTreeView(self, XML_File_Path) 
             
    def close_dicom_folder(self):
        """
        Closes the DICOM folder and updates display.
        """  
        self.save_treeview()
        treeView.closeTreeView(self)  
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