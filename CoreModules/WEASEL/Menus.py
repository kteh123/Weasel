from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QAction, QApplication, QMessageBox, QMenu)
from PyQt5.QtGui import  QIcon
import os
import sys
import pathlib
import importlib
import CoreModules.WEASEL.TreeView  as treeView
from CoreModules.WEASEL.weaselMenuXMLReader import WeaselMenuXMLReader
import logging
logger = logging.getLogger(__name__)


def setupMenus(self, menuXMLFile):
    """Builds the menus in the menu bar of the MDI"""
    logger.info("Menus.setupMenus")
    self.listMenus = []
    mainMenu = self.menuBar()
    objXMLMenuReader = WeaselMenuXMLReader(menuXMLFile) 
    menus = objXMLMenuReader.getMenus()
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
                function = "main"

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
        print('Error in function Menus.buildUserDefinedToolsMenuItem at line number {} when {}: '.format(line_number, item.find('label').text) + str(e))


#def closeAllImageWindows(self):
#        """Closes all the sub windows in the MDI except for
#        the sub window displaying the DICOM file tree view"""
#        logger.info("Menus closeAllImageWindows called")
#        for subWin in self.mdiArea.subWindowList():
#            if subWin.objectName() == 'tree_view':
#                continue
#            subWin.close()


#def tileAllSubWindows(self):
#    logger.info("Menus.tileAllSubWindow called")
#    height, width = self.getMDIAreaDimensions()
#    for subWin in self.mdiArea.subWindowList():
#        if subWin.objectName() == 'tree_view':
#            subWin.setGeometry(0, 0, width * 0.4, height)
#        elif subWin.objectName() == 'Binary_Operation':
#            subWin.setGeometry(0,0,width*0.5,height*0.5)
#        elif subWin.objectName() == 'metaData_Window':
#            subWin.setGeometry(width * 0.4,0,width*0.6,height)
#        elif subWin.objectName() == 'image_viewer':
#            subWin.setGeometry(width * 0.4,0,width*0.3,height*0.5)
#        self.mdiArea.tileSubWindows()


def buildContextMenuItem(context, item, self):
    menuItem = QAction(item.find('label').text, self)
    menuItem.setEnabled(True)
    moduleName = item.find('module').text
    
    if item.find('function') is not None:
        function = item.find('function').text
    else:
        function = "main"
    
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


def buildContextMenu(self, menuXMLFile):
    logger.info("Menus.buildContextMenu called")
    try:
        self.context = QMenu(self)
        objXMLMenuReader = WeaselMenuXMLReader(menuXMLFile) 
        items = objXMLMenuReader.getContextMenuItems()
        for item in items:
            buildContextMenuItem(self.context, item, self)
    except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            #filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            print('Error in function Menus.buildContextMenu at line number {}: '.format(line_number) + str(e))
