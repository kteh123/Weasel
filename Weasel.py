from PyQt5.QtWidgets import (QApplication,                         
        QMdiArea, QWidget, QVBoxLayout, 
        QMdiSubWindow, QMainWindow,  
        QStatusBar)

import os
import sys
import logging

#Add folders CoreModules  Developer/ModelLibrary to the Module Search Path. 
#path[0] is the current working directory
#pathlib.Path().absolute() is the current directory where the script is located. 
#It doesn't matter if it's Python SYS or Windows SYS
sys.path.append(os.path.join(sys.path[0],'Developer//WEASEL//Tools//'))
sys.path.append(os.path.join(sys.path[0],
        'Developer//WEASEL//Tools//FERRET_Files//'))
sys.path.append(os.path.join(sys.path[0],'CoreModules'))
sys.path.append(os.path.join(sys.path[0],'CoreModules//WEASEL//'))

import CoreModules.styleSheet as styleSheet
from CoreModules.weaselXMLReader import WeaselXMLReader
import CoreModules.WEASEL.Menus  as menus
import CoreModules.WEASEL.ToolBar  as toolBar


__version__ = '1.0'
__author__ = 'Steve Shillitoe'


#Create and configure the logger
#First delete the previous log file if there is one
LOG_FILE_NAME = "WEASEL1.log"
if os.path.exists(LOG_FILE_NAME):
    os.remove(LOG_FILE_NAME) 
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename=LOG_FILE_NAME, 
                level=logging.INFO, 
                format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class Weasel(QMainWindow):
    def __init__(self): 
        """Creates the MDI container."""
        super (). __init__ () 
        self.showFullScreen()
        self.setWindowTitle("WEASEL")
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.setLayout(QVBoxLayout(self.centralwidget))
        self.mdiArea = QMdiArea(self.centralwidget)
        self.mdiArea.tileSubWindows()
        self.centralwidget.layout().addWidget(self.mdiArea)
        self.currentImagePath = ''
        self.statusBar = QStatusBar()
        self.centralwidget.layout().addWidget(self.statusBar)
        self.selectedStudy = ''
        self.selectedSeries = ''
        self.selectedImageName = ''
        self.overRideSavedColourmapAndLevels = False #Set to True if the user checks the Apply Selection tick box
        self.applyUserSelection = False
        self.userSelectionList = []
        
         # XML reader object to process XML configuration file
        self.objXMLReader = WeaselXMLReader() 

        menus.setupMenus(self)
        toolBar.setupToolBar(self)
        self.setStyleSheet(styleSheet.TRISTAN_GREY)
        logger.info("WEASEL GUI created successfully.")
  

    def getMDIAreaDimensions(self):
      return self.mdiArea.height(), self.mdiArea.width() 

def main():
    app = QApplication(sys . argv )
    winMDI = Weasel()
    winMDI.showMaximized()
    sys.exit(app.exec())

if __name__ == '__main__':
        main()


        