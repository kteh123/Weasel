from PyQt5.QtWidgets import (QApplication,                         
        QMdiArea, QWidget, QVBoxLayout, 
        QMdiSubWindow, QMainWindow,  
        QStatusBar, QDockWidget, QLabel)
from PyQt5.QtCore import  Qt
import os
import sys
import logging
from multiprocessing import current_process

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

#Add folders CoreModules  Developer/ModelLibrary to the Module Search Path. 
#path[0] is the current working directory
#pathlib.Path().absolute() is the current directory where the script is located. 
#It doesn't matter if it's Python SYS or Windows SYS

sys.path.append(os.path.join(sys.path[0],'CoreModules'))
sys.path.append(os.path.join(sys.path[0],'CoreModules','WEASEL'))
sys.path.append(os.path.join(sys.path[0],'External'))
sys.path.append(os.path.join(sys.path[0],'Pipelines'))
sys.path.append(os.path.join(sys.path[0],'Scripting'))
sys.path.append(os.path.dirname(sys.path[0])) # Add the parent directory to sys

import CoreModules.WEASEL.StyleSheet as styleSheet
from CoreModules.WEASEL.weaselXMLReader import WeaselXMLReader
from CoreModules.WEASEL.weaselConfigXMLReader import WeaselConfigXMLReader
import CoreModules.WEASEL.Menus as menus
import CoreModules.WEASEL.ToolBar as toolBar
from Scripting.Scripting import Pipelines


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
        #Add scroll bars as needed when the subwindows are tiled
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.tileSubWindows()
        self.centralwidget.layout().addWidget(self.mdiArea)
        self.statusBar = QStatusBar()
        self.centralwidget.layout().addWidget(self.statusBar)
        self.DICOMFolder = ''
        self.checkedImageList = []
        self.checkedSeriesList = []
        self.checkedStudyList = []
        self.checkedSubjectList = []
        self.treeView = None
        
        self.treeViewColumnWidths = { 1: 0, 2: 0, 3: 0}
        
         # XML reader object to process XML configuration file
        self.objConfigXMLReader = WeaselConfigXMLReader()
        menuXMLFile = self.objConfigXMLReader.getMenuFile()
        #print("menuXMLFile = {}".format(menuXMLFile))
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


    @property
    def isAnImageChecked(self):
        flag = False
        root = self.treeView.invisibleRootItem()
        subjectCount = root.childCount()
        checkedImagesList = []
        for i in range(subjectCount):
            subject = root.child(i)
            studyCount = subject.childCount()
            for j in range(studyCount):
                study = subject.child(j)
                seriesCount = study.childCount()
                for n in range(seriesCount):
                    series = study.child(n)
                    imagesCount = series.childCount()
                    for k in range(imagesCount):
                        image = series.child(k)
                        if image.checkState(0) == Qt.Checked:
                            flag = True
                            break
        return flag


    @property
    def isASeriesChecked(self):
        flag = False
        root = self.treeView.invisibleRootItem()
        subjectCount = root.childCount()
        checkedSeriesList = []
        for i in range(subjectCount):
            subject = root.child(i)
            studyCount = subject.childCount()
            for j in range(studyCount):
                study = subject.child(j)
                seriesCount = study.childCount()
                for n in range(seriesCount):
                    series = study.child(n)
                    if series.checkState(0) == Qt.Checked:
                        flag = True
                        break
        return flag
     

    @property
    def isAStudyChecked(self):
        flag = False
        root = self.treeView.invisibleRootItem()
        subjectCount = root.childCount()
        checkedStudiesList = []
        for i in range(subjectCount):
            subject = root.child(i)
            studyCount = subject.childCount()
            for j in range(studyCount):
                study = subject.child(j)   
                if study.checkState(0) == Qt.Checked:
                    flag = True
                    break
        return flag


    @property
    def isASubjectChecked(self):
        flag = False
        root = self.treeView.invisibleRootItem()
        subjectCount = root.childCount()
        checkedSubjectsList = []
        for i in range(subjectCount):
            subject = root.child(i)
            if subject.checkState(0) == Qt.Checked:
                flag = True
                break
        return flag

def main():
    app = QApplication(sys . argv )
    winMDI = Weasel()
    winMDI.showMaximized()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
   