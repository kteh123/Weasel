
from PyQt5.QtWidgets import (QAction)
from PyQt5.QtGui import  QIcon
import logging
import CoreModules.WEASEL.MenuToolBarCommon as menuToolBarCommon
logger = logging.getLogger(__name__)

FERRET_LOGO = 'images\\FERRET_LOGO.png'


def setupToolBar(self):  
    logger.info("Menus.setupToolBar called")
    launchFerretButton = QAction(QIcon(FERRET_LOGO), '&FERRET', self)
    launchFerretButton.triggered.connect(lambda: menuToolBarCommon.displayFERRET(self))
    self.toolBar = self.addToolBar("FERRET")
    self.toolBar.addAction(launchFerretButton)
