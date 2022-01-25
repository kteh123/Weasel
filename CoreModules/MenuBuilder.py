"""
Class for building the menus in the menu bar of Weasel.

MenuBuilder generates the menus defined either in an XML file or a Python script.
"""
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
    """
    This class creates the top-level menus and submenus in the Weasel GUI, 
    using the menus defined in either a Python or XML file.

    If the menu definition file is Python, then the SubMenuBuilder function is used to build the menus. 
    If the menu file is XML, then the module `XMLMenuBuilder.py` 
    is used to build the menu in the Weasel GUI.
    """
    def __init__(self, weasel):
        """
        Initiates the MenuBuilder object.
        """
        self.weasel = weasel
        self.context = QMenu(weasel)
        self.listMenus = []
        self.listPythonFiles = returnListPythonFiles()


    def buildMenus(self):
        """
        This function builds the menus in the menu bar of Weasel.

        The name of the menu configuration file in the 
        <menu_config_file> element in the Weasel configuration file,
        config.xml is retrieved.  Its type, Python or XML is determined
        and the menu definitions it contains are used to build the menu.
        """
        try:
            menuConfigFile = self.weasel.objConfigXMLReader.getMenuConfigFile()
            if menuConfigFile:
                #a menu config file has been defined
                # If it's a Python menu
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
                # If it's an XML menu
                elif isXMLFile(menuConfigFile):
                    xmlMenuBuilder.setupMenus(self.weasel, menuConfigFile)
                    xmlMenuBuilder.buildContextMenu(self.weasel, menuConfigFile)
        except Exception as e:
            print('Error in MenuBuilder.buildMenus: ' + str(e)) 
            logger.exception('Error in MenuBuilder.buildMenus: ' + str(e)) 


    def newSubMenu(self, label):
        """
        Returns an object based on the SubMenuBuilder class.
        """
        return SubMenuBuilder(self.weasel, label)


class SubMenuBuilder:
    """
    This class allows menus to be added to the menu bar in the Weasel GUI 
    using the definitions in Python menu files.
    """
    def __init__(self, weasel, topMenuName): 
        """
        Initialises a menu called topMenuName.
        """
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
        """Represents this class's objects as a string"""
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
        """
        This function is used to define a menu item in a Python file. 

        Input arguments
        ***************
        label - a string containing the name of the menu item
        shortcut - a string containing the menu item shortcut
        tooltip - a string containing the menu item tool tip
        pipeline  - a string containing the name of module that 
                contains the function called functionName
        functionName - a string containing the name of the function
            executed when the menu item is selected.  By convention
            this should always be 'main'.
        context - boolean indicating if this menu item should also be
            included in a context menu.
        icon - a string containing the file path of an icon that will 
            displayed in front of the menu item name
        """
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
        """
        Add a separator line to a menu.
        """
        self.topMenu.addSeparator()


    def _actionHovered(self, action):
        """
        Allows a menu item to display a tool tip when the mouse
        pointer hovers over it.
        """
        tip = action.toolTip()
        QToolTip.showText(QCursor.pos(), tip)


def returnListPythonFiles():
    """
    This function returns a list of the Python files in the parent 
    folder of Weasel.
    """
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
    """
    This function returns True if a file is a Python file,
    otherwise it returns False.

    If the file name extension is 'py' it is a Python file.

    Input Argument
    **************
    fileName - a string containing the name of a file and its extension.
    """
    flag = False
    if fileName.split(".")[-1].lower()  == 'py':
        flag = True
    return flag


def isXMLFile(fileName):
    """
    This function returns True if a file is an XML file,
    otherwise it returns False.

    If the file name extension is 'xml' it is an XML file.

    Input Argument
    **************
    fileName - a string containing the name of a file and its extension.
    """
    flag = False
    if fileName.split(".")[-1].lower()  == 'xml':
        flag = True
    return flag

