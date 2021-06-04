from PyQt5.QtWidgets import (QApplication,                         
        QMdiArea, QWidget, QVBoxLayout, 
        QMdiSubWindow, QMainWindow, QMenu,
        QStatusBar, QDockWidget, QLabel)
from PyQt5.QtCore import  Qt
import os
import sys
import pathlib
import importlib
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

#os.chdir(os.path.dirname(sys.argv[0]))
sys.path.append(os.path.dirname(sys.argv[0]))
sys.path.append(os.path.join(sys.path[0],'CoreModules'))
sys.path.append(os.path.join(sys.path[0],'CoreModules','WEASEL'))
sys.path.append(os.path.join(sys.path[0],'External'))
sys.path.append(os.path.join(sys.path[0],'Pipelines'))
sys.path.append(os.path.join(sys.path[0],'Scripting'))
sys.path.append(os.path.dirname(sys.path[0])) # Add the parent directory to sys

import CoreModules.WEASEL.StyleSheet as styleSheet
from CoreModules.WEASEL.WeaselXMLReader import WeaselXMLReader
from CoreModules.WEASEL.WeaselConfigXMLReader import WeaselConfigXMLReader
import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.XMLMenuBuilder as xmlMenuBuilder
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
        self.listMenus = []
        self.listPythonFiles = self.returnListPythonFiles()

        #print("self.listPythonFiles={}".format(self.listPythonFiles))
        
        self.treeViewColumnWidths = { 1: 0, 2: 0, 3: 0}
        
         # XML reader object to process XML configuration file
        self.objConfigXMLReader = WeaselConfigXMLReader()

        #build menus from either xml or python config file
        self.buildMenus()

        self.weaselDataFolder = self.objConfigXMLReader.getWeaselDataFolder()
        
         # XML reader object to process XML DICOM data file
        self.objXMLReader = WeaselXMLReader() 
        
        #toolBar.setupToolBar(self)  commented out to remove Ferret from Weasel
        self.setStyleSheet(styleSheet.TRISTAN_GREY)
        logger.info("WEASEL GUI created successfully.")


    def __repr__(self):
       return '{}'.format(
           self.__class__.__name__)


    def buildMenus(self):
        try:
            logger.info("Weasel.buildMenus called.")
            menuConfigFile = self.objConfigXMLReader.getMenuConfigFile()
        
            #create context menu to display with the tree view
            self.context = QMenu(self)
            #add Reset Tree View to context menu
            xmlMenuBuilder.createFileMenuItem("Reset Tree View", "Ctrl+E", 
            "Uncheck all checkboxes on the tree view.",
            True, treeView, self, "callUnCheckTreeViewItems", context=True)

            #even if a menu config file is not defined, 
            #create the default File menu
            xmlMenuBuilder.setUpFileMenu(self.menuBar(), self)

            if menuConfigFile:
                #a menu config file has been defined
                if self.isPythonFile(menuConfigFile):
                    moduleFileName = [pythonFilePath 
                                      for pythonFilePath in self.listPythonFiles 
                                      if menuConfigFile in pythonFilePath][0]
                    spec = importlib.util.spec_from_file_location(menuConfigFile, moduleFileName)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    objFunction = getattr(module, "main")
                    #execute python functions to build the menus and menu items
                    objFunction(self)
                elif self.isXMLFile(menuConfigFile):
                    xmlMenuBuilder.setupMenus(self, menuConfigFile)
                    xmlMenuBuilder.buildContextMenu(self, menuConfigFile)
        except Exception as e:
            print('Error in Weasel.buildMenus: ' + str(e)) 
            logger.exception('Error in Weasel.buildMenus: ' + str(e)) 


    def getMDIAreaDimensions(self):
      return self.mdiArea.height(), self.mdiArea.width() 


    @staticmethod
    def isPythonFile(fileName):
        flag = False
        if fileName.split(".")[-1].lower()  == 'py':
            flag = True
        return flag


    @staticmethod
    def isXMLFile(fileName):
        flag = False
        if fileName.split(".")[-1].lower()  == 'xml':
            flag = True
        return flag


    @staticmethod
    def returnListPythonFiles():
        listPythonFiles = []
        for dirpath, _, filenames in os.walk(pathlib.Path().absolute().parent):
            for individualFile in filenames:
                if individualFile.endswith(".py"):
                    sys.path.append(os.path.dirname(dirpath))
                    listPythonFiles.append(os.path.join(dirpath, individualFile))
        return listPythonFiles

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
   