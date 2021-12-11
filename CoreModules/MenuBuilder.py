   
import CoreModules.XMLMenuBuilder as xmlMenuBuilder

from PyQt5.QtWidgets import QAction, QMenu, QToolTip 
from PyQt5.QtGui import QCursor, QIcon 
import os
import sys
import pathlib
import importlib
import logging
logger = logging.getLogger(__name__)


class MenuBuilder():

    def __init__(self, weasel):

        self.weasel = weasel
        self.context = QMenu(weasel)
        self.listMenus = []
        self.listPythonFiles = returnListPythonFiles()

    def buildMenus(self):
        try:
            menuConfigFile = self.weasel.objConfigXMLReader.getMenuConfigFile()
            if menuConfigFile:
                #a menu config file has been defined
                if isPythonFile(menuConfigFile):
                    moduleFileName = [pythonFilePath 
                                        for pythonFilePath in self.listPythonFiles 
                                        if menuConfigFile in pythonFilePath][0]
                    spec = importlib.util.spec_from_file_location(menuConfigFile, moduleFileName)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    objFunction = getattr(module, "main")
                    #execute python functions to build the menus and menu items
                    objFunction(self.weasel)
                elif isXMLFile(menuConfigFile):
                    xmlMenuBuilder.setupMenus(self.weasel, menuConfigFile)
                    xmlMenuBuilder.buildContextMenu(self.weasel, menuConfigFile)
        except Exception as e:
            print('Error in MenuBuilder.buildMenus: ' + str(e)) 
            logger.exception('Error in MenuBuilder.buildMenus: ' + str(e)) 

    def newSubMenu(self, label):
        return SubMenuBuilder(self.weasel, label)


class SubMenuBuilder:
    """This class allows menus to be built using its member functions"""

    def __init__(self, weasel, topMenuName): 
        try:
            self.topMenu = weasel.menuBar().addMenu(topMenuName)
            self.topMenu.hovered.connect(self._actionHovered)
            weasel.menuBuilder.context.hovered.connect(self._actionHovered)
            weasel.menuBuilder.listMenus.append(self.topMenu)
            self.weasel = weasel
            logger.info('PythonMenuBuilder Created top menu {}'.format(topMenuName))

        except Exception as e:
            print('Error in SubMenuBuilder.__init__: ' + str(e)) 
            logger.exception('Error in SubMenuBuilder.__init__: ' + str(e)) 


    def __repr__(self):
       return '{}, {!r}'.format(
           self.__class__.__name__,
           self.topMenu.title())


    def item(self, label = 'Pipeline',
               shortcut = None,
               tooltip = None,
               pipeline = None,
               functionName = 'main', 
               context = False,
               icon = None):
        try:
            if icon is not None:
                if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                    if os.path.exists(os.path.join(sys._MEIPASS, icon)): icon_path = os.path.join(sys._MEIPASS, icon)
                    else: icon_path = icon
                else: icon_path = icon
                self.menuItem = QAction(QIcon(icon_path), label, self.weasel)
            else:
                self.menuItem = QAction(label, self.weasel)

            if shortcut is not None:
                self.menuItem.setShortcut(shortcut)

            if tooltip is not None:
                self.menuItem.setToolTip(tooltip)

            #Walk the directory structure until the module defined above is found
            moduleFileName = [pythonFilePath 
                              for pythonFilePath in self.weasel.menuBuilder.listPythonFiles 
                              if pipeline + ".py" in pythonFilePath][0]
            spec = importlib.util.spec_from_file_location(pipeline, moduleFileName)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            objFunction = getattr(module, functionName)
            self.menuItem.triggered.connect(lambda : objFunction(self.weasel))
            self.menuItem.setEnabled(True)
            self.menuItem.setData(module)
            self.topMenu.addAction(self.menuItem)
            if context:
                self.weasel.menuBuilder.context.addAction(self.menuItem)
    
        except Exception as e:
            print('Error in MenuBuilder.item when item={}: '.format(label) + str(e)) 
            logger.exception('Error in MenuBuilder.item: ' + str(e)) 

    def separator(self):
        self.topMenu.addSeparator()

    def _actionHovered(self, action):
        tip = action.toolTip()
        QToolTip.showText(QCursor.pos(), tip)



def returnListPythonFiles():
    listPythonFiles = []
    for dirpath, _, filenames in os.walk(pathlib.Path().absolute().parent):
        for individualFile in filenames:
            if individualFile.endswith(".py"):
                listPythonFiles.append(os.path.join(dirpath, individualFile))
    
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        search_directory = pathlib.Path(sys._MEIPASS)
        for dirpath, _, filenames in os.walk(search_directory):
            for individualFile in filenames:
                if individualFile.endswith(".py"):
                    listPythonFiles.append(os.path.join(dirpath, individualFile))
                    
    return listPythonFiles

def isPythonFile(fileName):
    flag = False
    if fileName.split(".")[-1].lower()  == 'py':
        flag = True
    return flag

def isXMLFile(fileName):
    flag = False
    if fileName.split(".")[-1].lower()  == 'xml':
        flag = True
    return flag

