from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QAction, QApplication, QMessageBox, QMenu)
from PyQt5.QtGui import  QIcon
import os
import sys
import pathlib
import importlib
import CoreModules.WEASEL.TreeView  as treeView
from CoreModules.WEASEL.weaselToolsXMLReader import WeaselToolsXMLReader
import Developer.WEASEL.Tools.copyDICOM_Image as copyDICOM_Image
import Developer.WEASEL.Tools.BinaryOperationsOnImages as binaryOperationsOnImages
import Developer.WEASEL.Tools.ViewMetaData  as viewMetaData
import CoreModules.WEASEL.LoadDICOM  as loadDICOMFile
import CoreModules.WEASEL.DisplayImageColour  as displayImageColour
import CoreModules.WEASEL.DisplayImageCommon as displayImageCommon
import CoreModules.WEASEL.DisplayImageROI as displayImageROI
import CoreModules.WEASEL.MenuToolBarCommon as menuToolBarCommon


import logging
logger = logging.getLogger(__name__)

FERRET_LOGO = 'images\\FERRET_LOGO.png'

class NoTreeViewItemSelected(Exception):
   """Raised when the name of the function corresponding 
   to a model is not returned from the XML configuration file."""
   pass

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


def buildContextMenu(self, pos):
    context = QMenu(self)

    viewImageButton = returnViewAction(self)
    context.addAction(viewImageButton)

    viewImageROIButton = returnViewROIAction(self)
    context.addAction(viewImageROIButton)

    viewMetaDataButton =  returnViewMetaDataAction(self)
    context.addAction(viewMetaDataButton)

    #copySeriesButton =  returnCopySeriesAction(self)
    #context.addAction(copySeriesButton)

    #deleteImageButton =  returnDeleteImageAction(self)
    #context.addAction(deleteImageButton)
    #binaryOperationsButton = returnBinaryOperationsAction(self)
    #context.addAction(binaryOperationsButton)

    context.exec_(self.treeView.mapToGlobal(pos))


def returnViewAction(self, bothImagesAndSeries = True):
    self.viewImageButton = QAction('&View Image', self)
    self.viewImageButton.setShortcut('Ctrl+V')
    self.viewImageButton.setStatusTip('View DICOM Image or series')
    self.viewImageButton.triggered.connect(lambda: viewImage(self))
    self.viewImageButton.setData(bothImagesAndSeries)
    return self.viewImageButton


def returnViewROIAction(self, bothImagesAndSeries = True):
    self.viewImageROIButton = QAction('View Image with &ROI', self)
    self.viewImageROIButton.setShortcut('Ctrl+R')
    self.viewImageROIButton.setStatusTip('View DICOM Image or series with the ROI tool')
    self.viewImageROIButton.triggered.connect(lambda: viewROIImage(self))
    self.viewImageROIButton.setData(bothImagesAndSeries)
    return self.viewImageROIButton


def returnViewMetaDataAction(self, bothImagesAndSeries = True):
    self.viewMetaDataButton = QAction('&View Metadata', self)
    self.viewMetaDataButton.setShortcut('Ctrl+M')
    self.viewMetaDataButton.setStatusTip('View DICOM Image or series metadata')
    self.viewMetaDataButton.triggered.connect(lambda: viewMetaData.viewMetadata(self))
    self.viewMetaDataButton.setData(bothImagesAndSeries)
    return self.viewMetaDataButton


def returnDeleteImageAction(self, bothImagesAndSeries = True):
    self.deleteImageButton = QAction('&Delete Series/Image', self)
    self.deleteImageButton.setShortcut('Ctrl+D')
    self.deleteImageButton.setStatusTip('Delete a DICOM Image or series')
    self.deleteImageButton.triggered.connect(lambda: deleteImage(self))
    self.deleteImageButton.setData(bothImagesAndSeries)
    return self.deleteImageButton


def returnCopySeriesAction(self, bothImagesAndSeries = False):
    self.copySeriesButton = QAction('&Copy Series', self)
    self.copySeriesButton.setShortcut('Ctrl+C')
    self.copySeriesButton.setStatusTip('Copy a DICOM series') 
    self.copySeriesButton.setData(bothImagesAndSeries)
    self.copySeriesButton.triggered.connect(
        lambda:copyDICOM_Image.copySeries(self))
    return self.copySeriesButton


def returnBinaryOperationsAction(self, bothImagesAndSeries = False):
    self.binaryOperationsButton = QAction('&Binary Operations', self)
    self.binaryOperationsButton.setShortcut('Ctrl+B')
    self.binaryOperationsButton.setStatusTip(
        'Performs binary operations on two images')
    self.binaryOperationsButton.setData(bothImagesAndSeries)
    self.binaryOperationsButton.triggered.connect(
        lambda: binaryOperationsOnImages.displayBinaryOperationsWindow(self))
    return self.binaryOperationsButton


def buildToolsMenu(self):
    try:
        bothImagesAndSeries = True  #delete later?
        self.viewAction = returnViewAction(self)
        self.viewAction.setEnabled(False)
        self.toolsMenu.addAction(self.viewAction)

        self.viewImageROIButton  = returnViewROIAction(self)
        self.viewImageROIButton.setEnabled(False)
        self.toolsMenu.addAction(self.viewImageROIButton)

        self.viewMetaDataButton = returnViewMetaDataAction(self)
        self.viewMetaDataButton.setEnabled(False)
        self.toolsMenu.addAction(self.viewMetaDataButton)
        
        self.deleteImageButton = returnDeleteImageAction(self)
        self.deleteImageButton.setEnabled(False)
        self.toolsMenu.addAction(self.deleteImageButton)
        
        
        self.copySeriesButton =  returnCopySeriesAction(self)
        self.copySeriesButton.setEnabled(False)
        self.toolsMenu.addAction(self.copySeriesButton)
        

        self.toolsMenu.addSeparator()
      
        self.binaryOperationsButton = returnBinaryOperationsAction(self)
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
        #function = "saveImage"
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
            studyName = self.selectedStudy 
            seriesName = self.selectedSeries
            if treeView.isAnImageSelected(self):
                displayImageColour.displayImageSubWindow(self, studyName, seriesName)
            elif treeView.isASeriesSelected(self):
                self.imageList = self.objXMLReader.getImagePathList(studyName, seriesName)
                displayImageColour.displayMultiImageSubWindow(self, self.imageList, studyName, seriesName)
        except Exception as e:
            print('Error in Menus.viewImage: ' + str(e))
            logger.error('Error in Menus.viewImage: ' + str(e))


def viewROIImage(self):
    """Creates a subwindow that displays a DICOM image with ROI creation functionality. 
    Executed using the 'View Image with ROI' Menu item in the Tools menu."""
    try:
        logger.info("Menus.viewROIImage called")
        #print('treeView.isAnItemSelected(self)={}'.format(treeView.isAnItemSelected(self)))
        #print('treeView.isAnImageSelected(self)={}'.format(treeView.isAnImageSelected(self)))
        #print('treeView.isASeriesSelected(self)={}'.format(treeView.isASeriesSelected(self)))
        
        if treeView.isAnItemSelected(self) == False:
            raise NoTreeViewItemSelected

        if treeView.isAnImageSelected(self):
            displayImageROI.displayImageROISubWindow(self)
        elif treeView.isASeriesSelected(self):
            studyName = self.selectedStudy 
            seriesName = self.selectedSeries
            self.imageList = self.objXMLReader.getImagePathList(studyName, seriesName)
            displayImageROI.displayMultiImageROISubWindow(self, self.imageList, studyName, seriesName)

    except NoTreeViewItemSelected:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("View DICOM series or image with ROI")
            msgBox.setText("Select either a series or an image")
            msgBox.exec()
    except Exception as e:
        print('Error in Menus.viewROIImage: ' + str(e))
        logger.error('Error in Menus.viewROIImage: ' + str(e))


def deleteImage(self):
        """This method deletes an image or a series of images by 
        deleting the physical file(s) and then removing their entries
        in the XML file."""
        logger.info("Menus.deleteImage called")
        try:
            if treeView.isAnItemSelected(self) == False:
                raise NoTreeViewItemSelected

            studyName = self.selectedStudy
            seriesName = self.selectedSeries
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
                    displayImageCommon.closeSubWindow(self, imagePath)
                    #Is this the last image in a series?
                    #Get the series containing this image and count the images it contains
                    #If it is the last image in a series then remove the
                    #whole series from XML file
                    #No it is not the last image in a series
                    #so just remove the image from the XML file 
                    images = self.objXMLReader.getImageList(studyName, seriesName)
                    if len(images) == 1:
                        #only one image, so remove the series from the xml file
                        #need to get study (parent) containing this series (child)
                        #then remove child from parent
                        self.objXMLReader.removeSeriesFromXMLFile(studyName, seriesName)
                    elif len(images) > 1:
                        #more than 1 image in the series, 
                        #so just remove the image from the xml file
                        self.objXMLReader.removeOneImageFromSeries(
                            studyName, seriesName, imagePath)
                    #Update tree view with xml file modified above
                    treeView.refreshDICOMStudiesTreeView(self)
            elif treeView.isASeriesSelected(self):
                buttonReply = QMessageBox.question(self, 
                  'Delete DICOM series', "You are about to delete series {}".format(seriesName), 
                  QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                if buttonReply == QMessageBox.Ok:
                    #Delete each physical file in the series
                    #Get a list of names of images in that series
                    imageList = self.objXMLReader.getImagePathList(studyName, 
                                                                   seriesName) 
                    #Iterate through list of images and delete each image
                    for imagePath in imageList:
                        if os.path.exists(imagePath):
                            os.remove(imagePath)
                    #Remove the series from the XML file
                    self.objXMLReader.removeSeriesFromXMLFile(studyName, seriesName)
                    displayImageCommon.closeSubWindow(self, seriesName)
                treeView.refreshDICOMStudiesTreeView(self)
        except NoTreeViewItemSelected:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Delete a DICOM series or image")
            msgBox.setText("Select either a series or an image")
            msgBox.exec()
        except Exception as e:
            print('Error in Menus.deleteImage: ' + str(e))
            logger.error('Error in Menus.deleteImage: ' + str(e))