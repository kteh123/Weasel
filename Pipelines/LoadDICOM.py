import os
import time
import logging
from PyQt5 import QtCore 
from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QMessageBox, QApplication, QFileDialog, QVBoxLayout, 
                             QMdiSubWindow, QLabel, QProgressBar, 
    QMdiArea,  QWidget, QGridLayout, QVBoxLayout, QSpinBox,
         QGroupBox, QMainWindow, QHBoxLayout, QDoubleSpinBox,
        QPushButton, QStatusBar, QLabel, QAbstractSlider, QHeaderView,
        QTreeWidgetItem, QGridLayout, QSlider, QCheckBox, QLayout, 
         QComboBox, QTableWidget, QTableWidgetItem, QFrame)
from PyQt5.QtGui import QCursor, QIcon, QColor

import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.WEASEL.WriteXMLfromDICOM as WriteXMLfromDICOM
import CoreModules.WEASEL.MessageWindow  as messageWindow
import Pipelines.CloseAllSubWindows as closeAllSubWindows

logger = logging.getLogger(__name__)

def isEnabled(self):
    return True

def main(self):
    """This function is executed when the Load DICOM menu item is selected.
    It displays a folder dialog box.  After the user has selected the folder
    containing the DICOM file, an existing XML is searched for.  If one is 
    found then the user is given the option of using it, rather than build
    a new one from scratch.
    """
    try:
        logger.info("LoadDICOM.main called")
        closeAllSubWindows.main(self)
        #self.selectedSubject = ''  SS 13.03.21
        #self.selectedStudy = ''
        #self.selectedSeries = ''
        self.selectedImageName = ''
        self.selectedImagePath = ''
        #browse to DICOM folder and get DICOM folder name
        scan_directory = getScanDirectory(self)
        #print(" scan_directory = ",  scan_directory)
        if scan_directory:
            #look inside DICOM folder for XML file with same name as DICOM folder
            if existsDICOMXMLFile(scan_directory):
                #an XML file exists, so ask user if they wish to use it or create new one
                buttonReply = QMessageBox.question(self, 
                    'Load DICOM images', 
                    'This DICOM folder has already been processed. Would you like to load it?', 
                        QMessageBox.Yes| QMessageBox.No, QMessageBox.Yes)
                if buttonReply == QMessageBox.Yes:
                    XML_File_Path = scan_directory + '//' + os.path.basename(scan_directory) + '.xml'
                else:
                    #the user wishes to create a new xml file,
                    #thus overwriting the old one
                    QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
                    XML_File_Path = makeDICOM_XML_File(self, scan_directory)
                    QApplication.restoreOverrideCursor()
            else:
                #if there is no XML file, create one
                QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
                XML_File_Path = makeDICOM_XML_File(self, scan_directory)
                QApplication.restoreOverrideCursor()

            QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
            treeView.makeDICOMStudiesTreeView(self, XML_File_Path)
            QApplication.restoreOverrideCursor()
    except Exception as e:
        print('Error in function LoadDICOM.main: ' + str(e))
        logger.error('Error in function LoadDICOM.main: ' + str(e))


def getScanDirectory(self):
        """Displays an open folder dialog window to allow the
        user to select the folder holding the DICOM files"""
        try:
            logger.info('LoadDICOM.getScanDirectory called.')
            #cwd = os.getcwd()

            scan_directory = QFileDialog.getExistingDirectory(
               self,
               'Select the directory containing the scan', 
               self.weaselDataFolder, 
               QFileDialog.ShowDirsOnly)
            return scan_directory
        except Exception as e:
            print('Error in function LoadDICOM.getScanDirectory: ' + str(e))


def existsDICOMXMLFile(scanDirectory):
    """This function returns True if an XML file of scan images already
    exists in the scan directory."""
    try:
        logger.info("LoadDICOM.existsDICOMXMLFile called")
        flag = False
        with os.scandir(scanDirectory) as entries:
                for entry in entries:
                    if entry.is_file():
                        if entry.name.lower() == \
                            os.path.basename(scanDirectory).lower() + ".xml":
                            flag = True
                            break
        return flag                   
    except Exception as e:
        print('Error in function LoadDICOM.existsDICOMXMLFile: ' + str(e))
        logger.error('Error in function LoadDICOM.existsDICOMXMLFile: ' + str(e))


def makeDICOM_XML_File(self, scan_directory):
    """Creates an XML file that describes the contents of the scan folder,
    scan_directory.  Returns the full file path of the resulting XML file,
    which takes it's name from the scan folder."""
    try:
        logger.info("LoadDICOM.makeDICOM_XML_File called.")
        if scan_directory:
            start_time=time.time()
            numFiles, numFolders = WriteXMLfromDICOM.get_files_info(scan_directory)
            if numFolders == 0:
                folder = os.path.basename(scan_directory) + ' folder.'
            else:
                folder = os.path.basename(scan_directory) + ' folder and {} '.format(numFolders) \
                    + 'subdirectory(s)'

            messageWindow.displayMessageSubWindow(self,
                "Collecting {} files from the {}".format(numFiles, folder))
            scans, paths = WriteXMLfromDICOM.get_scan_data(scan_directory, messageWindow, self)
            messageWindow.displayMessageSubWindow(self,"<H4>Reading data from each DICOM file</H4>")
            dictionary = WriteXMLfromDICOM.build_dictionary(scans, messageWindow, self)
            messageWindow.displayMessageSubWindow(self,"<H4>Writing DICOM data to an XML file</H4>")
            xml = WriteXMLfromDICOM.open_dicom_to_xml(dictionary, scans, paths, messageWindow, self)
            messageWindow.displayMessageSubWindow(self,"<H4>Saving XML file</H4>")
            fullFilePath = WriteXMLfromDICOM.create_XML_file(xml, scan_directory)
            self.msgSubWindow.close()
            end_time=time.time()
            xmlCreationTime = end_time - start_time 
            print('XML file creation time = {}'.format(xmlCreationTime))
            logger.info("LoadDICOM.makeDICOM_XML_File returns {}."
                        .format(fullFilePath))
        return fullFilePath
    except Exception as e:
        print('Error in function LoadDICOM.makeDICOM_XML_File: ' + str(e))
        logger.error('Error in function LoadDICOM.makeDICOM_XML_File: ' + str(e))


