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
    self.listMenus = []
    mainMenu = self.menuBar()
    objXMLToolsReader = WeaselToolsXMLReader() 
    menus = objXMLToolsReader.getMenus()
    for menu in menus:
        menuName = menu.attrib['name']
        self.topMenu = mainMenu.addMenu(menuName)
        self.listMenus.append(self.topMenu)
        for item in menu:
            buildUserDefinedToolsMenuItem(self, self.topMenu, item)


def buildUserDefinedToolsMenuItem(self, topMenu, item):
    try:
        #create action button on the fly
        logger.info("Menus.buildUserDefinedToolsMenuItem called.")
        if item.find('separator') is not None:
            self.topMenu.addSeparator()
        else:
            if item.find('icon') is not None:
                icon = item.find('icon').text
                self.menuItem = QAction(QIcon(icon), item.find('label').text, self)
            else:
                self.menuItem = QAction(item.find('label').text, self)
            if item.find('shortcut') is not None:
                self.menuItem.setShortcut(item.find('shortcut').text)
            if item.find('tooltip') is not None:
                self.menuItem.setToolTip(item.find('tooltip').text)
            if item.find('enabled') is not None:
                if item.find('enabled').text == 'True':
                    self.menuItem.setEnabled(True)
                else:
                    self.menuItem.setEnabled(False)

            moduleName = item.find('module').text

            if item.find('function') is not None:
                function = item.find('function').text
            else:
                function = "processImages"

            moduleFileName = [os.path.join(dirpath, moduleName+".py") 
                for dirpath, dirnames, filenames in os.walk(pathlib.Path().absolute()) if moduleName+".py" in filenames][0]
            spec = importlib.util.spec_from_file_location(moduleName, moduleFileName)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            objFunction = getattr(module, function)
            self.menuItem.triggered.connect(lambda : objFunction(self))

            if hasattr(module, "isSeriesOnly"):
                boolApplyBothImagesAndSeries = not getattr(module, "isSeriesOnly")(self)
            else:
                boolApplyBothImagesAndSeries = True

            self.menuItem.setData(boolApplyBothImagesAndSeries)
            topMenu.addAction(self.menuItem)
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        #filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print('Error in function Menus.buildUserDefinedToolsMenuItem at line number {}: '.format(line_number) + str(e))


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


def buildContextMenuItem(context, item, self):
    menuItem = QAction(item.find('label').text, self)
    menuItem.setEnabled(True)
    moduleName = item.find('module').text
    
    if item.find('function') is not None:
        function = item.find('function').text
    else:
        function = "processImages"
    
    moduleFileName = [os.path.join(dirpath, moduleName+".py") 
        for dirpath, dirnames, filenames in os.walk(pathlib.Path().absolute()) if moduleName+".py" in filenames][0]
    spec = importlib.util.spec_from_file_location(moduleName, moduleFileName)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    objFunction = getattr(module, function)
    menuItem.triggered.connect(lambda : objFunction(self))
    
    if hasattr(module, "isSeriesOnly"):
        boolApplyBothImagesAndSeries = not getattr(module, "isSeriesOnly")(self)
    else:
        boolApplyBothImagesAndSeries = True
    
    menuItem.setData(boolApplyBothImagesAndSeries)
    context.addAction(menuItem)
    

def displayContextMenu(self, pos):
    self.context.exec_(self.treeView.mapToGlobal(pos))


def buildContextMenu(self):
    logger.info("Menus.buildContextMenu called")
    try:
        self.context = QMenu(self)
        objXMLToolsReader = WeaselToolsXMLReader() 
        items = objXMLToolsReader.getContextMenuItems()
        for item in items:
            buildContextMenuItem(self.context, item, self)
    except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            #filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            print('Error in function Menus.buildContextMenu at line number {}: '.format(line_number) + str(e))


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