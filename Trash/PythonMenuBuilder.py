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

__author__ = 'Steve Shillitoe'

class PythonMenuBuilder:
    """This class allows menus to be built using its member functions"""

    def __init__(self, pointerToWeasel, topMenuName): 
        try:
            self.topMenu = pointerToWeasel.menuBar().addMenu(topMenuName)
            self.topMenu.hovered.connect(self._actionHovered)
            pointerToWeasel.context.hovered.connect(self._actionHovered)
            pointerToWeasel.listMenus.append(self.topMenu)
            self.pointerToWeasel = pointerToWeasel
            logger.info('PythonMenuBuilder Created top menu {}'.format(topMenuName))

        except Exception as e:
            print('Error in PythonMenuBuilder.__init__: ' + str(e)) 
            logger.exception('Error in PythonMenuBuilder.__init__: ' + str(e)) 


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
                self.menuItem = QAction(QIcon(icon), label, self.pointerToWeasel)
            else:
                self.menuItem = QAction(label, self.pointerToWeasel)

            if shortcut is not None:
                self.menuItem.setShortcut(shortcut)

            if tooltip is not None:
                self.menuItem.setToolTip(tooltip)

            #Walk the directory structure until the module defined above is found
            moduleFileName = [pythonFilePath 
                              for pythonFilePath in self.pointerToWeasel.listPythonFiles 
                              if pipeline + ".py" in pythonFilePath][0]
            spec = importlib.util.spec_from_file_location(pipeline, moduleFileName)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            objFunction = getattr(module, functionName)
            self.menuItem.triggered.connect(lambda : objFunction(self.pointerToWeasel))
            self.menuItem.setEnabled(True)
            self.menuItem.setData(module)
            self.topMenu.addAction(self.menuItem)

            if context:
                self.pointerToWeasel.context.addAction(self.menuItem)
    
        except Exception as e:
            print('Error in PythonMenuBuilder.addItem when item={}: '.format(label) + str(e)) 
            logger.exception('Error in PythonMenuBuilder.addItem: ' + str(e)) 


    def separator(self):
        self.topMenu.addSeparator()


    def _actionHovered(self, action):
        tip = action.toolTip()
        QToolTip.showText(QCursor.pos(), tip)
