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

import CoreModules.WEASEL.TreeView as treeView

__author__ = 'Steve Shillitoe'

class MenuBuilder:
    """description of class"""

    def __init__(self, pointerToWeasel, topMenuName): 
        try:
            self.topMenu = pointerToWeasel.menuBar().addMenu(topMenuName)
            self.topMenu.hovered.connect(self._actionHovered)
            pointerToWeasel.context.hovered.connect(self._actionHovered)
            pointerToWeasel.listMenus.append(self.topMenu)
            self.pointerToWeasel = pointerToWeasel
            logger.info('Created top menu {}'.format(topMenuName))

        except Exception as e:
            print('Error in MenuBuilder.__init__: ' + str(e)) 
            logger.exception('Error in MenuBuilder.__init__: ' + str(e)) 

    
    def addItem(self, itemLabel = 'Label not defined',
               shortcut = None,
               tooltip = None,
               moduleName = None,
               functionName = 'main', 
               context=False,
               iconFilePath = None):
        try:
            if iconFilePath is not None:
                self.menuItem = QAction(QIcon(iconFilePath), itemLabel, self.pointerToWeasel)
            else:
                self.menuItem = QAction(itemLabel, self.pointerToWeasel)

            if shortcut is not None:
                self.menuItem.setShortcut(shortcut)

            if tooltip is not None:
                self.menuItem.setToolTip(tooltip)

            #Walk the directory structure until the module defined above is found
            moduleFileName = [pythonFilePath 
                              for pythonFilePath in self.pointerToWeasel.listPythonFiles 
                              if moduleName+".py" in pythonFilePath][0]
            spec = importlib.util.spec_from_file_location(moduleName, moduleFileName)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            objFunction = getattr(module, functionName)
            self.menuItem.triggered.connect(lambda : objFunction(self.pointerToWeasel))
            self.menuItem.triggered.connect(lambda : self.pointerToWeasel.refresh())

            if hasattr(module, "isSeriesOnly"):
                boolApplyBothImagesAndSeries = not getattr(module, "isSeriesOnly")(self)
            else:
                boolApplyBothImagesAndSeries = True

            self.menuItem.setData(boolApplyBothImagesAndSeries)

            if hasattr(module, "isEnabled"):
                self.menuItem.setEnabled(getattr(module, "isEnabled")(self))
            else:
                self.menuItem.setEnabled(False)
   
            self.topMenu.addAction(self.menuItem)

            if context:
                self.pointerToWeasel.context.addAction(self.menuItem)
    
        except Exception as e:
            print('Error in MenuBuilder.addItem: ' + str(e)) 
            logger.exception('Error in MenuBuilder.addItem: ' + str(e)) 


    def addSeparator(self):
        self.topMenu.addSeparator()


    def _actionHovered(self, action):
        tip = action.toolTip()
        QToolTip.showText(QCursor.pos(), tip)