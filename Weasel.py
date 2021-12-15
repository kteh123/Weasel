"""Weasel.py is the start-up file of the Weasel application. 

It contains the definition of:

1. The Weasel class that inherits from PyQt5's QMainWindow class 
in order to create the Multiple Document Interface (MDI)
that forms the backbone of the Weasel GUI.

2. The Weasel_CMD class that is used when Weasel is run as a 
command line program. 
"""

from PyQt5.QtWidgets import (QApplication,                         
        QMdiArea, QWidget, QVBoxLayout, 
        QMdiSubWindow, QMainWindow, QMenu,
        QStatusBar, QDockWidget, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
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


#os.chdir(os.path.dirname(sys.argv[0]))
sys.path.append(os.path.dirname(sys.argv[0]))
sys.path.append(os.path.join(sys.path[0],'API'))
sys.path.append(os.path.join(sys.path[0],'CoreModules'))
sys.path.append(os.path.join(sys.path[0],'External'))
sys.path.append(os.path.join(sys.path[0],'Pipelines'))
sys.path.append(os.path.join(sys.path[0],'Displays'))
sys.path.append(os.path.join(sys.path[0],'Displays', 'ImageViewers', 'ComponentsUI'))
sys.path.append(os.path.join(sys.path[0],'Displays', 'ImageViewers', 'ComponentsUI', 'FreeHandROI'))
sys.path.append(os.path.dirname(sys.path[0])) # Add the parent directory to sys

import CoreModules.StyleSheet as styleSheet
from CoreModules.XMLConfigReader import XMLConfigReader
from CoreModules.WeaselXMLReader import WeaselXMLReader
from CoreModules.TreeView import TreeView
from CoreModules.MenuBuilder import MenuBuilder
from API.Main import WeaselProgrammingInterface

__version__ = '0.2'
__author__ = 'Steve Shillitoe & Joao Sousa'


#Create and configure the logger
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
LOG_FILE_NAME = os.path.join(os.path.dirname(sys.argv[0]), "Activity_Log.log")
logging.basicConfig(filename=LOG_FILE_NAME, filemode='w', format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class Weasel(QMainWindow, WeaselProgrammingInterface):

    def __init__(self): 
        """Creates the MDI container that forms the Weasel GUI."""
        super().__init__()
        print("=====================================")
        print("MESSAGE TO THE USER:")
        print("=====================================")
        print("This terminal window is required to be open for Weasel to run and should not be closed.")
        print("Weasel should take approximately 30 seconds to start.")
        self.cmd = False
        self.showFullScreen()
        self.setWindowTitle("Weasel")
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

        self.objConfigXMLReader = XMLConfigReader()
        self.menuBuilder = MenuBuilder(self)
        self.objXMLReader = None 

        self.weaselDataFolder = self.objConfigXMLReader.getWeaselDataFolder()
        self.menuBuilder.buildMenus()
        
        self.setStyleSheet(styleSheet.WEASEL_GREY)
        logger.info("Weasel GUI created successfully.")


    def __repr__(self):
        """Returns a string representation of objects of this class""" 
        return '{}'.format(self.__class__.__name__)



class Weasel_CMD(WeaselProgrammingInterface):

    def __init__(self, arguments):
        """Creates the Weasel Command-line class."""
        print("=====================================")
        print("Weasel Command-line Mode")
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

                logger.info("Weasel CMD created successfully.")
            else:
                print("=====================================")
                print("Invalid input arguments given.")
                print("See --help flag for more information.")
                print("=====================================")
                self.XMLDicomFile = None
                self.PythonFile = None
                logger.info("Weasel CMD not created due to invalid arguments.")
        else:
            print("=====================================")
            print("Invalid input arguments given.")
            print("See --help flag for more information.")
            print("=====================================")
            self.XMLDicomFile = None
            self.PythonFile = None
            logger.info("Weasel CMD not created due to invalid arguments.")

    def __repr__(self):
        """Returns a string representation of objects of this class""" 
        return '{}'.format(self.__class__.__name__)

    def run(self):
        """Runs Weasel in command-line mode"""
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
    """Creates an object of one of the following classes:
        1. Weasel class to create the Weasel GUI or
         
        2. Weasel_CMD class to run Weasel in command-line mode.
    """

    example_text = example_text = '''example usage:
        python Weasel.py -c -d "path/to/xml/dicom.xml" -s "path/to/analyis/script.py"
        Weasel.exe -c -d "path/to/xml/dicom.xml" -s "path/to/analyis/script.py"'''
    parser = argparse.ArgumentParser(prog='Weasel',
                                 description='Weasel Command-line Mode',
                                 epilog=example_text,
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 usage='Weasel.py/.exe [-h] [-c] [-d] XML_DATA_PATH [-s] PYTHON_SCRIPT_PATH' )
    parser.add_argument('-c', '--command-line', action='store_true', help='Start Weasel in command-line mode')
    parser.add_argument('-d', '--xml-dicom', type=str, metavar='', required=False, help='Path to the XML file with the DICOM filepaths')
    parser.add_argument('-s', '--python-script', type=str, metavar='', required=False, help='Path to the Python file with the analysis script (menu) to process')
    args = parser.parse_args()
    if args.command_line:
        app = QApplication(sys.argv)
        weaselCommandLine = Weasel_CMD(args)
        weaselCommandLine.run()
    else:
        app = QApplication(sys.argv)
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'): base_path = sys._MEIPASS
        else: base_path = "."
        app.setWindowIcon(QIcon(os.path.join(base_path, "Documents","images","favicon.ico")))
        winMDI = Weasel()
        winMDI.showMaximized()
        sys.exit(app.exec())

if __name__ == '__main__':
    freeze_support()
    main()
