import os
import time
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QCursor
from PyQt5 import QtCore 
from PyQt5.QtCore import  Qt
import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.WEASEL.Menus as menus
import CoreModules.WEASEL.WriteXMLfromDICOM as WriteXMLfromDICOM
import CoreModules.WEASEL.CloseAllSubWindows as closeAllSubWindows

logger = logging.getLogger(__name__)

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
        #self.selectedImageName = ''
        #self.selectedImagePath = ''
        #browse to DICOM folder and get DICOM folder name
        scan_directory = WriteXMLfromDICOM.getScanDirectory(self)
        self.DICOMFolder = scan_directory

        menus.setFileMenuItemEnabled(self, "Refresh DICOM folder", True)
        menus.setFileMenuItemEnabled(self, "Close DICOM folder", True)
        menus.setFileMenuItemEnabled(self,"Reset Tree View", True)

        #print(" scan_directory = ",  scan_directory)
        if scan_directory:
            #look inside DICOM folder for an XML file with same name as DICOM folder
            if WriteXMLfromDICOM.existsDICOMXMLFile(scan_directory):
                XML_File_Path = scan_directory + '//' + os.path.basename(scan_directory) + '.xml'
            else:
                #if there is no XML file, create one
                QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
                XML_File_Path = WriteXMLfromDICOM.makeDICOM_XML_File(self, scan_directory)
                QApplication.restoreOverrideCursor()

            QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
            treeView.makeDICOMStudiesTreeView(self, XML_File_Path)
            QApplication.restoreOverrideCursor()
    except Exception as e:
        print('Error in function LoadDICOM.main: ' + str(e))
        logger.error('Error in function LoadDICOM.main: ' + str(e))











