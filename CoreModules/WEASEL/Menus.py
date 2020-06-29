from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QAction)
from PyQt5.QtGui import  QIcon
import os
import sys
import logging
import pathlib
import importlib
from CoreModules.weaselToolsXMLReader import WeaselToolsXMLReader
import Developer.WEASEL.Tools.copyDICOM_Image as copyDICOM_Image
logger = logging.getLogger(__name__)

FERRET_LOGO = 'images\\FERRET_LOGO.png'

def setupMenus(self):  
    """Builds the menus in the menu bar of the MDI"""
    logger.info("Menus.setupMenus")
    mainMenu = self.menuBar()
    self.fileMenu = mainMenu.addMenu('File')
    self.toolsMenu = mainMenu.addMenu('Tools')
    self.helpMenu = mainMenu.addMenu('Help')

    #File Menu
    buildFileMenu(self)

    #Tools Menu
    buildToolsMenu(self)


def buildFileMenu(self):
    try:
        loadDICOM = QAction('&Load DICOM Images', self)
        loadDICOM.setShortcut('Ctrl+L')
        loadDICOM.setStatusTip('Load DICOM images from a scan folder')
        loadDICOM.triggered.connect(self.loadDICOM)
        self.fileMenu.addAction(loadDICOM)

        tileSubWindows = QAction('&Tile Subwindows', self)
        tileSubWindows.setShortcut('Ctrl+T')
        tileSubWindows.setStatusTip('Returns subwindows to a tile pattern')
        tileSubWindows.triggered.connect(self.tileAllSubWindows)
        self.fileMenu.addAction(tileSubWindows)
        
        closeAllImageWindowsButton = QAction('Close &All Image Windows', self)
        closeAllImageWindowsButton.setShortcut('Ctrl+A')
        closeAllImageWindowsButton.setStatusTip('Closes all image sub windows')
        closeAllImageWindowsButton.triggered.connect(self.closeAllImageWindows)
        self.fileMenu.addAction(closeAllImageWindowsButton)
        
        closeAllSubWindowsButton = QAction('&Close All Sub Windows', self)
        closeAllSubWindowsButton.setShortcut('Ctrl+X')
        closeAllSubWindowsButton.setStatusTip('Closes all sub windows')
        closeAllSubWindowsButton.triggered.connect(self.closeAllSubWindows)
        self.fileMenu.addAction(closeAllSubWindowsButton)
    except Exception as e:
        print('Error in function Menus.buildFileMenu: ' + str(e))


def buildToolsMenu(self):
    try:
        bothImagesAndSeries = True
        self.viewImageButton = QAction('&View Image', self)
        self.viewImageButton.setShortcut('Ctrl+V')
        self.viewImageButton.setStatusTip('View DICOM Image or series')
        self.viewImageButton.triggered.connect(self.viewImage)
        self.viewImageButton.setData(bothImagesAndSeries)
        self.viewImageButton.setEnabled(False)
        self.toolsMenu.addAction(self.viewImageButton)

        self.viewImageROIButton = QAction('View Image with &ROI', self)
        self.viewImageROIButton.setShortcut('Ctrl+R')
        self.viewImageROIButton.setStatusTip('View DICOM Image or series with the ROI tool')
        self.viewImageROIButton.triggered.connect(self.viewROIImage)
        self.viewImageROIButton.setData(bothImagesAndSeries)
        self.viewImageROIButton.setEnabled(False)
        self.toolsMenu.addAction(self.viewImageROIButton)

        self.viewMetaDataButton = QAction('&View Metadata', self)
        self.viewMetaDataButton.setShortcut('Ctrl+M')
        self.viewMetaDataButton.setStatusTip('View DICOM Image or series metadata')
        self.viewMetaDataButton.triggered.connect(self.viewMetadata)
        self.viewMetaDataButton.setData(bothImagesAndSeries)
        self.viewMetaDataButton.setEnabled(False)
        self.toolsMenu.addAction(self.viewMetaDataButton)
        
        self.deleteImageButton = QAction('&Delete Image', self)
        self.deleteImageButton.setShortcut('Ctrl+D')
        self.deleteImageButton.setStatusTip('Delete a DICOM Image or series')
        self.deleteImageButton.triggered.connect(self.deleteImage)
        self.deleteImageButton.setData(bothImagesAndSeries)
        self.deleteImageButton.setEnabled(False)
        self.toolsMenu.addAction(self.deleteImageButton)
        
        self.copySeriesButton = QAction('&Copy Series', self)
        self.copySeriesButton.setShortcut('Ctrl+C')
        self.copySeriesButton.setStatusTip('Copy a DICOM series') 
        bothImagesAndSeries = False
        self.copySeriesButton.setData(bothImagesAndSeries)
        self.copySeriesButton.triggered.connect(
            lambda:copyDICOM_Image.copySeries(self))
        self.copySeriesButton.setEnabled(False)
        self.toolsMenu.addAction(self.copySeriesButton)
        
        self.toolsMenu.addSeparator()
        self.binaryOperationsButton = QAction('&Binary Operations', self)
        self.binaryOperationsButton.setShortcut('Ctrl+B')
        self.binaryOperationsButton.setStatusTip(
            'Performs binary operations on two images')
        bothImagesAndSeries = False
        self.binaryOperationsButton.setData(bothImagesAndSeries)
        self.binaryOperationsButton.triggered.connect(
            self.displayBinaryOperationsWindow)
        self.binaryOperationsButton.setEnabled(False)
        self.toolsMenu.addAction(self.binaryOperationsButton)
        
        #Add items to the Tools menu as defined in
        #toolsMenu.xml
        addUserDefinedToolsMenuItems(self)
        
        self.toolsMenu.addSeparator()
        self.launchFerretButton = QAction(QIcon(FERRET_LOGO), '&FERRET', self)
        self.launchFerretButton.setShortcut('Ctrl+F')
        self.launchFerretButton.setStatusTip('Launches the FERRET application')
        self.launchFerretButton.triggered.connect(self.displayFERRET)
        self.launchFerretButton.setEnabled(True)
        self.toolsMenu.addAction(self.launchFerretButton)
    except Exception as e:
        print('Error in function Menus.buildToolsMenu: ' + str(e))


def addUserDefinedToolsMenuItems(self):
    try:
        logger.info("WEASEL addUserDefinedToolsMenuItems called.")
        self.objXMLReader = WeaselToolsXMLReader() 
        tools = self.objXMLReader.getTools()
        for tool in tools:
            buildUserDefinedToolsMenuItem(self, tool)
    except Exception as e:
        print('Error in function Menus.addUserDefinedToolsMenuItem: ' + str(e))


def buildUserDefinedToolsMenuItem(self, tool):
    try:
        #create action button on the fly
        logger.info("Menus.buildUserDefinedToolsMenuItem called.")
        self.menuItem = QAction(tool.find('action').text, self)
        self.menuItem.setShortcut(tool.find('shortcut').text)
        self.menuItem.setToolTip(tool.find('tooltip').text)
        if tool.find('applies_both_images_series').text == 'True':
            boolApplyBothImagesAndSeries = True
        else:
            #Only acts on a series
            boolApplyBothImagesAndSeries = False
        self.menuItem.setData(boolApplyBothImagesAndSeries)
        self.menuItem.setEnabled(False)
        moduleName = tool.find('module').text
        function = tool.find('function').text
        moduleFileName = [os.path.join(dirpath, moduleName+".py") 
            for dirpath, dirnames, filenames in os.walk(pathlib.Path().absolute()) if moduleName+".py" in filenames][0]
        spec = importlib.util.spec_from_file_location(moduleName, moduleFileName)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        objFunction = getattr(module, function)
        self.menuItem.triggered.connect(lambda : objFunction(self))
        self.toolsMenu.addAction(self.menuItem)
    except Exception as e:
        print('Error in function Menus.buildUserDefinedToolsMenuItem: ' + str(e))