from PyQt5.QtCore import  Qt
from PyQt5 import QtCore 
from PyQt5.QtWidgets import QAction, QApplication, QMessageBox, QMenu, QToolTip 
from PyQt5.QtGui import QCursor, QIcon 
import os
import sys
import pathlib
import importlib
import logging
logger = logging.getLogger(__name__)

from CoreModules.WEASEL.WeaselMenuXMLReader import WeaselMenuXMLReader


def setupMenus(pointerToWeasel, menuXMLFile):
    """Builds the menus in the menu bar of the MDI"""
    try:
        logger.info("Menus.setupMenus")
        mainMenu = pointerToWeasel.menuBar()
        objXMLMenuReader = WeaselMenuXMLReader(menuXMLFile) 
        menus = objXMLMenuReader.getMenus()
        for menu in menus:
            menuName = menu.attrib['name']
            pointerToWeasel.topMenu = mainMenu.addMenu(menuName)
            pointerToWeasel.topMenu.hovered.connect(_actionHovered)
            pointerToWeasel.listMenus.append(pointerToWeasel.topMenu)
            for item in menu:
                buildUserDefinedToolsMenuItem(pointerToWeasel, pointerToWeasel.topMenu, item, pointerToWeasel.listPythonFiles)
    except Exception as e:
            print('Error in Menus.setupMenus: ' + str(e)) 
            logger.exception('Error in Menus.setupMenus: ' + str(e)) 


def buildUserDefinedToolsMenuItem(pointerToWeasel, topMenu, item, pythonFiles):
    try:
        #create action button on the fly
        logger.info("Menus.buildUserDefinedToolsMenuItem called.")
        if item.find('separator') is not None:
            pointerToWeasel.topMenu.addSeparator()
        else:
            if item.find('icon') is not None:
                icon = item.find('icon').text
                pointerToWeasel.menuItem = QAction(QIcon(icon), item.find('label').text, pointerToWeasel)
            else:
                pointerToWeasel.menuItem = QAction(item.find('label').text, pointerToWeasel)
            if item.find('shortcut') is not None:
                pointerToWeasel.menuItem.setShortcut(item.find('shortcut').text)
            if item.find('tooltip') is not None:
                pointerToWeasel.menuItem.setToolTip(item.find('tooltip').text)

            moduleName = item.find('module').text

            if item.find('function') is not None:
                function = item.find('function').text
            else:
                function = "main"
                
            #Walk the directory structure until the modules defined the menu XML are found
            #moduleFileName = [os.path.join(dirpath, moduleName+".py") 
            #    for dirpath, dirnames, filenames in os.walk(pathlib.Path().absolute().parent) if moduleName+".py" in filenames][0]
            moduleFileName = [pythonFilePath for pythonFilePath in pythonFiles if moduleName+".py" in pythonFilePath][0]
            spec = importlib.util.spec_from_file_location(moduleName, moduleFileName)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            objFunction = getattr(module, function)
            pointerToWeasel.menuItem.triggered.connect(lambda : objFunction(pointerToWeasel))
            #pointerToWeasel.menuItem.triggered.connect(lambda : pointerToWeasel.refresh())

            if hasattr(module, "isSeriesOnly"):
                boolApplyBothImagesAndSeries = not getattr(module, "isSeriesOnly")(pointerToWeasel)
            else:
                boolApplyBothImagesAndSeries = True

            pointerToWeasel.menuItem.setData(boolApplyBothImagesAndSeries)

            if hasattr(module, "isEnabled"):
                pointerToWeasel.menuItem.setEnabled(getattr(module, "isEnabled")(pointerToWeasel))
            else:
                pointerToWeasel.menuItem.setEnabled(False)
            
            topMenu.addAction(pointerToWeasel.menuItem)
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        #filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print('Error in function Menus.buildUserDefinedToolsMenuItem at line number {} when {}: '.format(line_number, item.find('label').text) + str(e))
        logger.exception('Error in Menus.buildUserDefinedToolsMenuItem at line number {} when {}: '.format(line_number, item.find('label').text) + str(e)) 


def buildContextMenuItem(pointerToWeasel, context, item, pythonFiles):
    try:
        menuItem = QAction(item.find('label').text, pointerToWeasel)
        menuItem.setEnabled(True)
        moduleName = item.find('module').text
    
        if item.find('function') is not None:
            function = item.find('function').text
        else:
            function = "main"
    
        #moduleFileName = [os.path.join(dirpath, moduleName+".py") 
        #    for dirpath, dirnames, filenames in os.walk(pathlib.Path().absolute()) if moduleName+".py" in filenames][0]
        moduleFileName = [pythonFilePath for pythonFilePath in pythonFiles if moduleName+".py" in pythonFilePath][0]
        spec = importlib.util.spec_from_file_location(moduleName, moduleFileName)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        objFunction = getattr(module, function)
        menuItem.triggered.connect(lambda : objFunction(pointerToWeasel))
        #menuItem.triggered.connect(lambda : pointerToWeasel.refresh())
    
        if hasattr(module, "isSeriesOnly"):
            boolApplyBothImagesAndSeries = not getattr(module, "isSeriesOnly")(pointerToWeasel)
        else:
            boolApplyBothImagesAndSeries = True
    
        menuItem.setData(boolApplyBothImagesAndSeries)
        context.addAction(menuItem)
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        #filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print('Error in function Menus.buildContextMenuItem at line number {} when {}: '.format(line_number, item.find('label').text) + str(e))
        logger.exception('Error in Menus.buildContextMenuItem at line number {} when {}: '.format(line_number, item.find('label').text) + str(e)) 


def _actionHovered(action):
        tip = action.toolTip()
        QToolTip.showText(QCursor.pos(), tip)


def buildContextMenu(pointerToWeasel, menuXMLFile):
    logger.info("Menus.buildContextMenu called")
    try:
        pointerToWeasel.context.hovered.connect(_actionHovered)

        objXMLMenuReader = WeaselMenuXMLReader(menuXMLFile) 
        items = objXMLMenuReader.getContextMenuItems()
        for item in items:
            buildContextMenuItem(pointerToWeasel, pointerToWeasel.context, item, pointerToWeasel.listPythonFiles)

    except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            #filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            print('Error in function Menus.buildContextMenu at line number {}: '.format(line_number) + str(e))
            logger.exception('Error in function Menus.buildContextMenu at line number {}: '.format(line_number) + str(e))