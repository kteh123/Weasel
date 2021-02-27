from PyQt5.QtWidgets import (QApplication,                         
        QMdiArea, QWidget, QVBoxLayout, 
        QMdiSubWindow, QMainWindow,  
        QStatusBar, QDockWidget, QLabel)
from PyQt5.QtCore import  Qt
import os
import sys
import logging
from multiprocessing import current_process

#Add folders CoreModules  Developer/ModelLibrary to the Module Search Path. 
#path[0] is the current working directory
#pathlib.Path().absolute() is the current directory where the script is located. 
#It doesn't matter if it's Python SYS or Windows SYS

sys.path.append(os.path.join(sys.path[0],'CoreModules'))
sys.path.append(os.path.join(sys.path[0],'CoreModules','WEASEL'))
sys.path.append(os.path.join(sys.path[0],'External'))
sys.path.append(os.path.join(sys.path[0],'Pipelines'))

import CoreModules.WEASEL.styleSheet as styleSheet
from CoreModules.WEASEL.weaselXMLReader import WeaselXMLReader
from CoreModules.WEASEL.weaselConfigXMLReader import WeaselConfigXMLReader
import CoreModules.WEASEL.Menus as menus
import CoreModules.WEASEL.ToolBar as toolBar
from CoreModules.Scripting import Pipelines


__version__ = '1.0'
__author__ = 'Steve Shillitoe & Joao Sousa'


#Create and configure the logger
#First delete the previous log file if there is one
LOG_FILE_NAME = "Activity_Log.log"
if os.path.exists(LOG_FILE_NAME) and current_process().name == 'MainProcess':
    os.remove(LOG_FILE_NAME)
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename=LOG_FILE_NAME, 
                level=logging.INFO, 
                format=LOG_FORMAT)
logger = logging.getLogger(__name__)


class Weasel(QMainWindow, Pipelines):
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
        self.statusBar = QStatusBar()
        self.centralwidget.layout().addWidget(self.statusBar)
        self.selectedStudy = ''
        self.selectedSeries = ''
        self.selectedImageName = ''
        self.selectedImagePath = ''
        self.checkedImageList = []
        self.checkedSeriesList = []
        self.checkedStudyList = []
        self.isAnImageChecked = False
        self.isASeriesChecked = False
        self.isAStudyChecked = False
        
         # XML reader object to process XML configuration file
        self.objConfigXMLReader = WeaselConfigXMLReader()
        menuXMLFile = self.objConfigXMLReader.getMenuFile()
        self.weaselDataFolder = self.objConfigXMLReader.getWeaselDataFolder()
        
         # XML reader object to process XML DICOM data file
        self.objXMLReader = WeaselXMLReader() 

        menus.setupMenus(self, menuXMLFile)
        menus.buildContextMenu(self, menuXMLFile)
        #toolBar.setupToolBar(self)  commented out to remove Ferret from Weasel
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
   