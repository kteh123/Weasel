from PyQt5.QtWidgets import (QApplication,                         
        QMdiArea, QWidget, QVBoxLayout, 
        QMdiSubWindow, QMainWindow, QMenu,
        QStatusBar, QDockWidget, QLabel)
from PyQt5.QtCore import  Qt
import os
import sys
import argparse
import importlib
import logging
from multiprocessing import current_process, freeze_support

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
sys.path.append(os.path.join(sys.path[0],'API'))
sys.path.append(os.path.dirname(sys.path[0])) # Add the parent directory to sys

import CoreModules.WEASEL.StyleSheet as styleSheet
from CoreModules.WEASEL.WeaselConfigXMLReader import WeaselConfigXMLReader
from CoreModules.WEASEL.TreeView import TreeView
import CoreModules.WEASEL.XMLMenuBuilder as xmlMenuBuilder
from CoreModules.WEASEL.WeaselXMLReader import WeaselXMLReader
#import Trash.ToolBar as toolBar
from API.Main import WeaselProgrammingInterface

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


class Weasel(QMainWindow, WeaselProgrammingInterface):

    def __init__(self): 
        """Creates the MDI container."""
        super().__init__()
        self.cmd = False
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
        self.treeView = None
        self.listMenus = []
        self.listPythonFiles = self.returnListPythonFiles()

         # XML reader object to process XML configuration file
        self.objConfigXMLReader = WeaselConfigXMLReader()
        #build menus from either xml or python config file
        self.buildMenus()
        self.weaselDataFolder = self.objConfigXMLReader.getWeaselDataFolder()
        self.objXMLReader = WeaselXMLReader(self) 
        
        #toolBar.setupToolBar(self)  commented out to remove Ferret from Weasel
        self.setStyleSheet(styleSheet.TRISTAN_GREY)
        logger.info("WEASEL GUI created successfully.")


    def __repr__(self):
       return '{}'.format(self.__class__.__name__)

    def buildMenus(self):
        try:
            logger.info("Weasel.buildMenus called.")
            menuConfigFile = self.objConfigXMLReader.getMenuConfigFile()
        
            #create context menu to display with the tree view
            self.context = QMenu(self)

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

class Weasel_CMD(WeaselProgrammingInterface):

    def __init__(self, arguments):
        """Creates the WEASEL Command-line class."""
        print("=====================================")
        print("WEASEL Command-line Mode")
        print("=====================================")
        if arguments.xml_dicom and arguments.python_script:
            if arguments.xml_dicom.endswith(".xml") and arguments.python_script.endswith(".py"):
                super().__init__()
                self.cmd = True
                self.tqdm_prog = None
                self.weaselDataFolder = os.path.dirname(sys.argv[0])
                self.XMLDicomFile = arguments.xml_dicom
                self.PythonFile = arguments.python_script

                self.objXMLReader = WeaselXMLReader() 

                # XML reader object to process XML DICOM data file
                self.treeView = TreeView(self, arguments.xml_dicom)

                logger.info("WEASEL CMD created successfully.")
            else:
                print("=====================================")
                print("Invalid input arguments given.")
                print("Running the GUI version of WEASEL.")
                print("See --help flag for more information.")
                print("=====================================")
                self.XMLDicomFile = None
                self.PythonFile = None
                logger.info("WEASEL CMD not created due to invalid arguments.")
        else:
            print("=====================================")
            print("Invalid input arguments given.")
            print("Running the GUI version of WEASEL.")
            print("See --help flag for more information.")
            print("=====================================")
            self.XMLDicomFile = None
            self.PythonFile = None
            logger.info("WEASEL CMD not created due to invalid arguments.")

    def __repr__(self):
       return '{}'.format(self.__class__.__name__)

    def run(self):
        if self.XMLDicomFile and self.PythonFile:
            print("=====================================")
            print("Script in " + self.PythonFile + " started ...")
            print("=====================================")
            moduleName = os.path.basename(self.PythonFile)
            spec = importlib.util.spec_from_file_location(moduleName, self.PythonFile)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            objFunction = getattr(module, 'main')
            objFunction(self)
        else:
            print("=====================================")
            print("No script was started")
            print("=====================================")
        return

def main():
    example_text = example_text = '''example usage:
        python Weasel.py -c -d "path/to/xml/dicom.xml" -s "path/to/analyis/script.py"
        Weasel.exe -c -d "path/to/xml/dicom.xml" -s "path/to/analyis/script.py"'''
    parser = argparse.ArgumentParser(prog='base_maker',
                                 description='WEASEL Command-line Mode',
                                 epilog=example_text,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-c', '--command-line', action='store_true', help='Start WEASEL in command-line mode')
    parser.add_argument('-d', '--xml-dicom', type=str, metavar='', required=False, help='Path to the XML file with the DICOM filepaths')
    parser.add_argument('-s', '--python-script', type=str, metavar='', required=False, help='Path to the Python file with the analysis script (menu) to process')
    args = parser.parse_args()
    if args.command_line:
        app = QApplication(sys.argv)
        weaselCommandLine = Weasel_CMD(args)
        weaselCommandLine.run()
    else:
        app = QApplication(sys.argv)
        winMDI = Weasel()
        winMDI.showMaximized()
        sys.exit(app.exec())

if __name__ == '__main__':
    freeze_support()
    main()
