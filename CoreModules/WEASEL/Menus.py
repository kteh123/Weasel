from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QAction, QApplication, QMessageBox)
from PyQt5.QtGui import  QIcon
import os
import sys
import pathlib
import importlib
import CoreModules.WEASEL.TreeView  as treeView
from CoreModules.WEASEL.weaselToolsXMLReader import WeaselToolsXMLReader
import Developer.WEASEL.Tools.copyDICOM_Image as copyDICOM_Image
import CoreModules.WEASEL.LoadDICOM  as loadDICOMFile
import CoreModules.WEASEL.ViewMetaData  as viewMetaData
import CoreModules.WEASEL.DisplayImageColour  as displayImageColour
import CoreModules.WEASEL.DisplayImageCommon as displayImageCommon
import CoreModules.WEASEL.DisplayImageROI as displayImageROI
import CoreModules.WEASEL.MenuToolBarCommon as menuToolBarCommon
import CoreModules.WEASEL.BinaryOperationsOnImages as binaryOperationsOnImages


import logging
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
        loadDICOM.triggered.connect(lambda: loadDICOMFile.loadDICOM(self))
        self.fileMenu.addAction(loadDICOM)

        tileSubWindows = QAction('&Tile Subwindows', self)
        tileSubWindows.setShortcut('Ctrl+T')
        tileSubWindows.setStatusTip('Returns subwindows to a tile pattern')
        tileSubWindows.triggered.connect(lambda: tileAllSubWindows(self))
        self.fileMenu.addAction(tileSubWindows)
        
        closeAllImageWindowsButton = QAction('Close &All Image Windows', self)
        closeAllImageWindowsButton.setShortcut('Ctrl+A')
        closeAllImageWindowsButton.setStatusTip('Closes all image sub windows')
        closeAllImageWindowsButton.triggered.connect(lambda: closeAllImageWindows(self))
        self.fileMenu.addAction(closeAllImageWindowsButton)
        
        closeAllSubWindowsButton = QAction('&Close All Sub Windows', self)
        closeAllSubWindowsButton.setShortcut('Ctrl+X')
        closeAllSubWindowsButton.setStatusTip('Closes all sub windows')
        closeAllSubWindowsButton.triggered.connect(lambda: displayImageCommon.closeAllSubWindows(self))
        self.fileMenu.addAction(closeAllSubWindowsButton)
    except Exception as e:
        print('Error in function Menus.buildFileMenu: ' + str(e))


def closeAllImageWindows(self):
        """Closes all the sub windows in the MDI except for
        the sub window displaying the DICOM file tree view"""
        logger.info("Menus closeAllImageWindows called")
        for subWin in self.mdiArea.subWindowList():
            if subWin.objectName() == 'tree_view':
                continue
            subWin.close()
            QApplication.processEvents()


def tileAllSubWindows(self):
    logger.info("Menus.tileAllSubWindow called")
    height, width = self.getMDIAreaDimensions()
    for subWin in self.mdiArea.subWindowList():
        if subWin.objectName() == 'tree_view':
            subWin.setGeometry(0, 0, width * 0.4, height)
        elif subWin.objectName() == 'Binary_Operation':
            subWin.setGeometry(0,0,width*0.5,height*0.5)
        elif subWin.objectName() == 'metaData_Window':
            subWin.setGeometry(width * 0.4,0,width*0.6,height)
        elif subWin.objectName() == 'image_viewer':
            subWin.setGeometry(width * 0.4,0,width*0.3,height*0.5)
        #self.mdiArea.tileSubWindows()


def buildToolsMenu(self):
    try:
        bothImagesAndSeries = True
        self.viewImageButton = QAction('&View Image', self)
        self.viewImageButton.setShortcut('Ctrl+V')
        self.viewImageButton.setStatusTip('View DICOM Image or series')
        self.viewImageButton.triggered.connect(lambda: viewImage(self))
        self.viewImageButton.setData(bothImagesAndSeries)
        self.viewImageButton.setEnabled(False)
        self.toolsMenu.addAction(self.viewImageButton)

        self.viewImageROIButton = QAction('View Image with &ROI', self)
        self.viewImageROIButton.setShortcut('Ctrl+R')
        self.viewImageROIButton.setStatusTip('View DICOM Image or series with the ROI tool')
        self.viewImageROIButton.triggered.connect(lambda: viewROIImage(self))
        self.viewImageROIButton.setData(bothImagesAndSeries)
        self.viewImageROIButton.setEnabled(False)
        self.toolsMenu.addAction(self.viewImageROIButton)

        self.viewMetaDataButton = QAction('&View Metadata', self)
        self.viewMetaDataButton.setShortcut('Ctrl+M')
        self.viewMetaDataButton.setStatusTip('View DICOM Image or series metadata')
        self.viewMetaDataButton.triggered.connect(lambda: viewMetaData.viewMetadata(self))
        self.viewMetaDataButton.setData(bothImagesAndSeries)
        self.viewMetaDataButton.setEnabled(False)
        self.toolsMenu.addAction(self.viewMetaDataButton)
        
        self.deleteImageButton = QAction('&Delete Image', self)
        self.deleteImageButton.setShortcut('Ctrl+D')
        self.deleteImageButton.setStatusTip('Delete a DICOM Image or series')
        self.deleteImageButton.triggered.connect(lambda: deleteImage(self))
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
            lambda: binaryOperationsOnImages.displayBinaryOperationsWindow(self))
        self.binaryOperationsButton.setEnabled(False)
        self.toolsMenu.addAction(self.binaryOperationsButton)
        
        #Add items to the Tools menu as defined in
        #toolsMenu.xml
        addUserDefinedToolsMenuItems(self)
        
        self.toolsMenu.addSeparator()
        self.launchFerretButton = QAction(QIcon(FERRET_LOGO), '&FERRET', self)
        self.launchFerretButton.setShortcut('Ctrl+F')
        self.launchFerretButton.setStatusTip('Launches the FERRET application')
        self.launchFerretButton.triggered.connect(lambda: menuToolBarCommon.displayFERRET(self))
        self.launchFerretButton.setEnabled(True)
        self.toolsMenu.addAction(self.launchFerretButton)
    except Exception as e:
        print('Error in function Menus.buildToolsMenu: ' + str(e))



def addUserDefinedToolsMenuItems(self):
    try:
        logger.info("Menus addUserDefinedToolsMenuItems called.")
        objXMLToolsReader = WeaselToolsXMLReader() 
        tools = objXMLToolsReader.getTools()
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


def viewImage(self):
        """Creates a subwindow that displays a DICOM image. Either executed using the 
        'View Image' Menu item in the Tools menu or by double clicking the Image name 
        in the DICOM studies tree view."""
        try:
            logger.info("Menus.viewImage called")
            if treeView.isAnImageSelected(self):
                displayImageColour.displayImageSubWindow(self)
            elif treeView.isASeriesSelected(self):
                studyID = self.selectedStudy 
                seriesID = self.selectedSeries
                self.imageList = self.objXMLReader.getImagePathList(studyID, seriesID)
                displayImageColour.displayMultiImageSubWindow(self, self.imageList, studyID, seriesID)
        except Exception as e:
            print('Error in Menus.viewImage: ' + str(e))
            logger.error('Error in Menus.viewImage: ' + str(e))


def viewROIImage(self):
    """Creates a subwindow that displays a DICOM image with ROI creation functionality. 
    Executed using the 'View Image with ROI' Menu item in the Tools menu."""
    try:
        logger.info("Menus.viewROIImage called")
        if treeView.isAnImageSelected(self):
            displayImageROI.displayImageROISubWindow(self)
        elif treeView.isASeriesSelected(self):
            studyID = self.selectedStudy 
            seriesID = self.selectedSeries
            self.imageList = self.objXMLReader.getImagePathList(studyID, seriesID)
            displayImageROI.displayMultiImageROISubWindow(self, self.imageList, studyID, seriesID)
    except Exception as e:
        print('Error in Menus.viewROIImage: ' + str(e))
        logger.error('Error in Menus.viewROIImage: ' + str(e))


def deleteImage(self):
        """TO DO"""
        """This method deletes an image or a series of images by 
        deleting the physical file(s) and then removing their entries
        in the XML file."""
        try:
            studyID = self.selectedStudy
            seriesID = self.selectedSeries
            if treeView.isAnImageSelected(self):
                imageName = self.selectedImageName
                imagePath = self.selectedImagePath
                buttonReply = QMessageBox.question(self, 
                  'Delete DICOM image', "You are about to delete image {}".format(imageName), 
                  QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                if buttonReply == QMessageBox.Ok:
                    #Delete physical file if it exists
                    if os.path.exists(imagePath):
                        os.remove(imagePath)
                    #If this image is displayed, close its subwindow
                    self.closeSubWindow(imagePath)
                    #Is this the last image in a series?
                    #Get the series containing this image and count the images it contains
                    #If it is the last image in a series then remove the
                    #whole series from XML file
                    #No it is not the last image in a series
                    #so just remove the image from the XML file 
                    images = self.objXMLReader.getImageList(studyID, seriesID)
                    if len(images) == 1:
                        #only one image, so remove the series from the xml file
                        #need to get study (parent) containing this series (child)
                        #then remove child from parent
                        self.objXMLReader.removeSeriesFromXMLFile(studyID, seriesID)
                    elif len(images) > 1:
                        #more than 1 image in the series, 
                        #so just remove the image from the xml file
                        self.objXMLReader.removeOneImageFromSeries(
                            studyID, seriesID, imagePath)
                    #Update tree view with xml file modified above
                    treeView.refreshDICOMStudiesTreeView(self)
            elif treeView.isASeriesSelected(self):
                buttonReply = QMessageBox.question(self, 
                  'Delete DICOM series', "You are about to delete series {}".format(seriesID), 
                  QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                if buttonReply == QMessageBox.Ok:
                    #Delete each physical file in the series
                    #Get a list of names of images in that series
                    imageList = self.objXMLReader.getImagePathList(studyID, 
                                                                   seriesID) 
                    #Iterate through list of images and delete each image
                    for imagePath in imageList:
                        if os.path.exists(imagePath):
                            os.remove(imagePath)
                    #Remove the series from the XML file
                    self.objXMLReader.removeSeriesFromXMLFile(studyID, seriesID)
                    self.closeSubWindow(seriesID)
                treeView.refreshDICOMStudiesTreeView(self)
        except Exception as e:
            print('Error in deleteImage: ' + str(e))
            logger.error('Error in deleteImage: ' + str(e))