#This file is currently redundant but may be required in the future
#***********************************************************************
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (QAction)
from PyQt5.QtGui import  QIcon
import logging
import CoreModules.WEASEL.MenuToolBarCommon as menuToolBarCommon
logger = logging.getLogger(__name__)

FERRET_LOGO = 'images\\FERRET_LOGO.png'


def setupToolBar(self):  
    logger.info("Menus.setupToolBar called")
    launchFerretButton = QAction(QIcon(FERRET_LOGO), 'FERRET', self)
    launchFerretButton.triggered.connect(lambda: menuToolBarCommon.displayFERRET(self))
    self.toolBar = self.addToolBar("FERRET")
    self.toolBar.setIconSize(QSize(32,32))
    self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
    self.toolBar.addAction(launchFerretButton)
    
