
from PyQt5 import QtCore
from PyQt5.QtCore import  Qt, pyqtSignal
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QLabel,
        QMdiArea, QMessageBox, QWidget, QGridLayout, QVBoxLayout, QMdiSubWindow, 
        QPushButton, QStatusBar,
        QTreeWidget, QTreeWidgetItem, QGridLayout, QSlider, QAbstractSlider,  
        QProgressBar, QComboBox )
from PyQt5.QtGui import QCursor, QIcon

import xml.etree.ElementTree as ET 
#from xml.dom import minidom
import pyqtgraph as pg
import os
import sys
import time
import numpy as np
from datetime import datetime
from datetime import date
import logging

#Add folders CoreModules & Developer/ModelLibrary to the Module Search Path. 
#path[0] is the current working directory
sys.path.append(os.path.join(sys.path[0],'Developer//Tools//'))
sys.path.append(os.path.join(sys.path[0],'CoreModules'))
import readDICOM_Image
import buildToolsMenu
import saveDICOM_Image
import WriteXMLfromDICOM 
import binaryOperationDICOM_Image
import styleSheet
from FERRET import FERRET as ferret


#Create and configure the logger
#First delete the previous log file if there is one
LOG_FILE_NAME = "WEASEL.log"
if os.path.exists(LOG_FILE_NAME):
   os.remove(LOG_FILE_NAME) 
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename=LOG_FILE_NAME, 
                    level=logging.INFO, 
                    format=LOG_FORMAT)
logger = logging.getLogger(__name__)


__version__ = '1.0'
__author__ = 'Steve Shillitoe'

FERRET_LOGO = 'images\\FERRET_LOGO.png'

class Weasel(QMainWindow):
    def __init__(self, parent=None):
        """Creates the MDI container."""
        QMainWindow.__init__(self, parent)
        
        self.setGeometry(0, 0, 2500, 1400)
        self.setWindowTitle("WEASEL")
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.setLayout(QVBoxLayout(self.centralwidget))
        self.mdiArea = QMdiArea(self.centralwidget)
        self.mdiArea.tileSubWindows()
        self.centralwidget.layout().addWidget(self.mdiArea)
        self.setupMenus()
        self.setupToolBar()
        self.currentImagePath = ''
        self.statusBar = QStatusBar()
        self.centralwidget.layout().addWidget(self.statusBar)
        self.selectedStudy = ''
        self.selectedSeries = ''
        self.selectedImagePath = ''
        self.selectedImageName = ''
        self.ApplyStyleSheet()
        loggerWEASEL.info("WEASEL GUI created successfully.")

    def setupMenus(self):  

        """Builds the menus in the menu bar of the MDI"""
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')

        #File Menu
        loadDICOM = QAction('&Load DICOM Images', self)
        loadDICOM.setShortcut('Ctrl+L')
        loadDICOM.setStatusTip('Load DICOM images from a scan folder')
        loadDICOM.triggered.connect(self.loadDICOM)
        fileMenu.addAction(loadDICOM)

        closeAllImageWindowsButton = QAction('Close &All Image Windows', self)
        closeAllImageWindowsButton.setShortcut('Ctrl+A')
        closeAllImageWindowsButton.setStatusTip('Closes all image sub windows')
        closeAllImageWindowsButton.triggered.connect(self.closeAllImageWindows)
        fileMenu.addAction(closeAllImageWindowsButton)

        closeAllSubWindowsButton = QAction('&Close All Sub Windows', self)
        closeAllSubWindowsButton.setShortcut('Ctrl+X')
        closeAllSubWindowsButton.setStatusTip('Closes all sub windows')
        closeAllSubWindowsButton.triggered.connect(self.closeAllSubWindows)
        fileMenu.addAction(closeAllSubWindowsButton)

        #Tools Menu
        self.viewImageButton = QAction('&View Image', self)
        self.viewImageButton.setShortcut('Ctrl+V')
        self.viewImageButton.setStatusTip('View DICOM Image or series')
        self.viewImageButton.triggered.connect(self.viewImage)
        self.viewImageButton.setEnabled(False)
        toolsMenu.addAction(self.viewImageButton)

        self.deleteImageButton = QAction('&Delete Image', self)
        self.deleteImageButton.setShortcut('Ctrl+D')
        self.deleteImageButton.setStatusTip('Delete a DICOM Image or series')
        self.deleteImageButton.triggered.connect(self.deleteImage)
        self.deleteImageButton.setEnabled(False)
        toolsMenu.addAction(self.deleteImageButton)
        toolsMenu.addSeparator()
        buildToolsMenu.buildToolsMenu(self, toolsMenu)
        
        toolsMenu.addSeparator()
        self.launchFerretButton = QAction(QIcon(FERRET_LOGO), '&FERRET', self)
        self.launchFerretButton.setShortcut('Ctrl+F')
        self.launchFerretButton.setStatusTip('Launches the FERRET application')
        self.launchFerretButton.triggered.connect(self.displayFERRET)
        self.launchFerretButton.setEnabled(True)
        toolsMenu.addAction(self.launchFerretButton)

    def setupToolBar(self):  
        self.launchFerretButton = QAction(QIcon(FERRET_LOGO), '&FERRET', self)
        self.launchFerretButton.triggered.connect(self.displayFERRET)
        
        self.toolBar = self.addToolBar("FERRET")
        self.toolBar.addAction(self.launchFerretButton)


    def ApplyStyleSheet(self):
        """Modifies the appearance of the GUI using CSS instructions"""
        try:
            self.setStyleSheet(styleSheet.TRISTAN_GREY)
            #logger.info('Style Sheet applied.')
        except Exception as e:
            print('Error in function ApplyStyleSheet: ' + str(e))
     

    def getScanDirectory(self):
        """Displays an open folder dialog window to allow the
        user to select the folder holding the DICOM files"""
        try:
            cwd = os.getcwd()
            scan_directory = QFileDialog.getExistingDirectory(
               self,
               'Select the directory containing the scan', 
               cwd, 
               QFileDialog.ShowDirsOnly)
            return scan_directory
        except Exception as e:
            print('Error in function getScanDirectory: ' + str(e))


    def displayMessageSubWindow(self, message):
        """
        Creates a subwindow that displays a message to the user about the 
        progress of making an XML file from the contents of a DICOM folder. 
        """
        try:
            for subWin in self.mdiArea.subWindowList():
                if subWin.objectName() == "Msg_Window":
                    subWin.close()
                    
            widget = QWidget()
            widget.setLayout(QVBoxLayout()) 
            self.msgSubWindow = QMdiSubWindow(self)
            self.msgSubWindow.setAttribute(Qt.WA_DeleteOnClose)
            self.msgSubWindow.setWidget(widget)
            self.msgSubWindow.setObjectName("Msg_Window")
            self.msgSubWindow.setWindowTitle("Loading DICOM files")
            self.msgSubWindow.setGeometry(0,0,900,200)
            self.mdiArea.addSubWindow(self.msgSubWindow)
            self.lblMsg = QLabel('<H4>' + message + '</H4>')
            widget.layout().addWidget(self.lblMsg)
            self.msgSubWindow.show()
            QApplication.processEvents()
        except Exception as e:
            print('Error in : displayMessageSubWindow' + str(e))


    def makeDICOM_XML_File(self, scan_directory):
        """Creates an XML file that describes the contents of the scan folder,
        scan_directory.  Returns the full file path of the resulting XML file,
        which takes it's name from the scan folder."""
        try:
            if scan_directory:
                start_time=time.time()
                numFiles, numFolders = WriteXMLfromDICOM.get_files_info(scan_directory)
                if numFolders == 0:
                    folder = os.path.basename(scan_directory) + ' folder.'
                else:
                    folder = os.path.basename(scan_directory) + ' folder and {} '.format(numFolders) \
                        + 'subdirectory(s)'

                self.displayMessageSubWindow(
                    "Collecting {} DICOM files from the {}".format(numFiles, folder))
                scans, paths = WriteXMLfromDICOM.get_scan_data(scan_directory)
                self.displayMessageSubWindow("<H4>Reading data from each DICOM file</H4>")
                dictionary = WriteXMLfromDICOM.get_studies_series(scans)
                self.displayMessageSubWindow("<H4>Writing DICOM data to an XML file</H4>")
                xml = WriteXMLfromDICOM.open_dicom_to_xml(dictionary, scans, paths)
                self.displayMessageSubWindow("<H4>Saving XML file</H4>")
                fullFilePath = WriteXMLfromDICOM.create_XML_file(xml, scan_directory)
                self.msgSubWindow.close()
                end_time=time.time()
                xmlCreationTime = end_time - start_time 
                print('XML file creation time = {}'.format(xmlCreationTime))
            return fullFilePath
        except Exception as e:
            print('Error in function makeDICOM_XML_File: ' + str(e))
 

    def existsDICOMXMLFile(self, scanDirectory):
        """This function returns True if an XML file of scan images already
        exists in the scan directory."""
        try:
            flag = False
            with os.scandir(scanDirectory) as entries:
                    for entry in entries:
                        if entry.is_file():
                            if entry.name.lower() == \
                                os.path.basename(scanDirectory).lower() + ".xml":
                                flag = True
                                break
            return flag                   
        except Exception as e:
            print('Error in function existsDICOMXMLFile: ' + str(e))


    def loadDICOM(self):
        """This function is executed when the Load DICOM menu item is selected.
        It displays a folder dialog box.  After the user has selected the folder
        containing the DICOM file, an existing XML is searched for.  If one is 
        found then the user is given the option of using it, rather than build
        a new one from scratch.
        """
        try:
            self.closeAllSubWindows()
            #browse to DICOM folder and get DICOM folder name
            scan_directory = self.getScanDirectory()
            if scan_directory:
                #look inside DICOM folder for XML file with same name as DICOM folder
                if self.existsDICOMXMLFile(scan_directory):
                    #an XML file exists, so ask user if they wish to use it or create new one
                    buttonReply = QMessageBox.question(self, 
                        'Load DICOM images', 
                        'An XML file exists for this DICOM folder. Would you like to use it?', 
                            QMessageBox.Yes| QMessageBox.No, QMessageBox.Yes)
                    if buttonReply == QMessageBox.Yes:
                        XML_File_Path = scan_directory + '//' + os.path.basename(scan_directory) + '.xml'
                    else:
                        #the user wishes to create a new xml file,
                        #thus overwriting the old one
                        QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
                        XML_File_Path = self.makeDICOM_XML_File(scan_directory)
                        QApplication.restoreOverrideCursor()
                else:
                    #if there is no XML file, create one
                    QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
                    XML_File_Path = self.makeDICOM_XML_File(scan_directory)
                    QApplication.restoreOverrideCursor()

                QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
                self.makeDICOMStudiesTreeView(XML_File_Path)
                QApplication.restoreOverrideCursor()

        except Exception as e:
            print('Error in function loadDICOM: ' + str(e))

            
    def getNumberItemsInTreeView(self):
        """Counts the number of elements in the DICOM XML file to
        determine the number of items forming the tree view"""
        try:
            numStudies = len(self.root.findall('./study'))
            numSeries = len(self.root.findall('./study/series'))
            numImages = len(self.root.findall('./study/series/image'))
            numItems = numStudies + numSeries + numImages
            return numStudies, numSeries, numImages, numItems
        except Exception as e:
            print('Error in function getNumberItemsInTreeView: ' + str(e))


    def makeDICOMStudiesTreeView(self, XML_File_Path):
        """Uses an XML file that describes a DICOM file structure to build a
        tree view showing a visual representation of that file structure."""
        try:
            if os.path.exists(XML_File_Path):
                self.DICOM_XML_FilePath = XML_File_Path
                self.DICOMfolderPath, _ = os.path.split(XML_File_Path)
                start_time=time.time()
                #self.root = self.objXMLReader.parseXMLFile(XML_File_Path)
                self.XMLtree = ET.parse(self.DICOM_XML_FilePath)
                self.root = self.XMLtree.getroot()
                end_time=time.time()
                XMLParseTime = end_time - start_time
                print('XML Parse Time = {}'.format(XMLParseTime))

                start_time=time.time()
                numStudies, numSeries, numImages, numTreeViewItems \
                    = self.getNumberItemsInTreeView()

                QApplication.processEvents()
                widget = QWidget()
                widget.setLayout(QVBoxLayout()) 
                subWindow = QMdiSubWindow(self)
                subWindow.setWidget(widget)
                subWindow.setObjectName("tree_view")
                subWindow.setWindowTitle("DICOM Study Structure")
                subWindow.setGeometry(0,0,800,300)
                self.mdiArea.addSubWindow(subWindow)

                self.lblLoading = QLabel('<H4>You are loading {} study(s), with {} series containing {} images</H4>'
                 .format(numStudies, numSeries, numImages))
                self.lblLoading.setWordWrap(True)

                widget.layout().addWidget(self.lblLoading)
                self.progBar = QProgressBar(self)
                widget.layout().addWidget(self.progBar)
                widget.layout().setAlignment(Qt.AlignTop)
                self.progBar.show()
                self.progBar.setMaximum(numTreeViewItems)
                self.progBar.setValue(0)
                subWindow.show()

                QApplication.processEvents()
                self.treeView = QTreeWidget()
                self.treeView.setUniformRowHeights(True)
                self.treeView.setColumnCount(4)
                self.treeView.setHeaderLabels(["DICOM Files", "Date", "Time", "Path"])
                
                # Uncomment to test XML file loaded OK
                #print(ET.tostring(self.root, encoding='utf8').decode('utf8'))
                treeWidgetItemCounter = 0 
                studies = self.root.findall('./study')
                for study in studies:
                    studyID = study.attrib['id']
                    studyBranch = QTreeWidgetItem(self.treeView)
                    treeWidgetItemCounter += 1
                    self.progBar.setValue(treeWidgetItemCounter)
                    studyBranch.setText(0, "Study - {}".format(studyID))
                    studyBranch.setFlags(studyBranch.flags() & ~Qt.ItemIsSelectable)
                    studyBranch.setExpanded(True)
                    self.seriesBranchList = []
                    for series in study:
                        seriesID = series.attrib['id']
                        seriesBranch = QTreeWidgetItem(studyBranch)
                        self.seriesBranchList.append(seriesBranch)
                        treeWidgetItemCounter += 1
                        self.progBar.setValue(treeWidgetItemCounter)
                        #seriesBranch.setFlags(seriesBranch.flags() | Qt.ItemIsUserCheckable)
                        seriesBranch.setText(0, "Series - {}".format(seriesID))
                        seriesBranch.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                        #Expand this series branch, so that the 3 resizeColumnToContents
                        #commands can work
                        seriesBranch.setExpanded(True)
                        for image in series:
                            #Extract filename from file path
                            if image.find('name').text:
                                imageName = os.path.basename(image.find('name').text)
                            else:
                                imageName = 'Name missing'
                            #print (imageName)
                            imageDate = image.find('date').text
                            imageTime = image.find('time').text
                            imagePath = image.find('name').text
                            imageLeaf = QTreeWidgetItem(seriesBranch)
                            treeWidgetItemCounter += 1
                            self.progBar.setValue(treeWidgetItemCounter)
                            imageLeaf.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                            #Uncomment the next 2 lines to put a checkbox in front of each image
                            #imageLeaf.setFlags(imageLeaf.flags() | Qt.ItemIsUserCheckable)
                            #imageLeaf.setCheckState(0, Qt.Unchecked)
                            imageLeaf.setText(0, 'Image - ' + imageName)
                            imageLeaf.setText(1, imageDate)
                            imageLeaf.setText(2, imageTime)
                            imageLeaf.setText(3, imagePath)
                self.treeView.resizeColumnToContents(0)
                self.treeView.resizeColumnToContents(1)
                self.treeView.resizeColumnToContents(2)
                #self.treeView.resizeColumnToContents(3)
                self.treeView.hideColumn(3)
                
                #Now collapse all series branches so as to hide the images
                for branch in self.seriesBranchList:
                    branch.setExpanded(False)
                self.treeView.itemSelectionChanged.connect(self.toggleToolButtons)
                self.treeView.itemDoubleClicked.connect(self.viewImage)
                self.treeView.itemClicked.connect(self.onTreeViewItemClicked)
                self.treeView.show()
                end_time=time.time()
                TreeViewTime = end_time - start_time
                print('Tree View create Time = {}'.format(TreeViewTime))
                
                self.lblLoading.clear()
                self.progBar.hide()
                self.progBar.reset()
                subWindow.setGeometry(0,0,800,1300)
                widget.layout().addWidget(self.treeView)   
        except Exception as e:
            print('Error in makeDICOMStudiesTreeView: ' + str(e))      


    @QtCore.pyqtSlot(QTreeWidgetItem, int)
    def onTreeViewItemClicked(self, item, col):
        selectedText = item.text(0)
        if 'study' in selectedText.lower():
            studyID = selectedText.replace('Study -', '').strip()
            self.selectedStudy = studyID
            self.selectedSeries = ''
            self.selectedImagePath = ''
            self.selectedImageName = ''
            self.statusBar.showMessage('Study - ' + studyID + ' selected.')
        elif 'series' in selectedText.lower():
            seriesID = selectedText.replace('Series -', '').strip()
            studyID = item.parent().text(0).replace('Study -', '').strip()
            self.selectedStudy = studyID
            self.selectedSeries = seriesID
            self.selectedImagePath = ''
            self.selectedImageName = ''
            fullSeriesID = studyID + ': ' + seriesID + ': no image selected.'
            self.statusBar.showMessage('Study and series - ' +  fullSeriesID)
        elif 'image' in selectedText.lower():
            imageID = selectedText.replace('Image -', '')
            imagePath =item.text(3)
            seriesID = item.parent().text(0).replace('Series -', '').strip()
            studyID = item.parent().parent().text(0).replace('Study -', '').strip()
            self.selectedStudy = studyID
            self.selectedSeries = seriesID
            self.selectedImagePath = imagePath.strip()
            self.selectedImageName = imageID.strip()
            fullImageID = studyID + ': ' + seriesID + ': '  + imageID
            self.statusBar.showMessage('Image - ' + fullImageID + ' selected.')


    def closeAllSubWindows(self):
        self.mdiArea.closeAllSubWindows()
        self.treeView = None

    def displayFERRET(self):
        """
        Displays FERRET in a sub window 
        """
        try:
            self.closeAllSubWindows()
            self.subWindow = QMdiSubWindow(self)
            self.subWindow.setAttribute(Qt.WA_DeleteOnClose)
            self.subWindow.setWindowFlags(Qt.CustomizeWindowHint | 
                                          Qt.WindowCloseButtonHint)
            
            ferretWidget = ferret(self.subWindow, self.statusBar)
            self.subWindow.setWidget(ferretWidget.returnFerretWidget())
            
            self.subWindow.setWindowTitle('FERRET')
            self.subWindow.setWindowIcon(QIcon(FERRET_LOGO))
            self.mdiArea.addSubWindow(self.subWindow)
            self.subWindow.showMaximized()
           
        except Exception as e:
            print('Error in displayFERRET: ' + str(e))


    def displayImageSubWindow(self, pixelArray, imagePath):
        """
        Creates a subwindow that displays the DICOM image contained in pixelArray. 
        """
        try:
            self.subWindow = QMdiSubWindow(self)
            self.subWindow.setAttribute(Qt.WA_DeleteOnClose)
            self.subWindow.setWindowFlags(Qt.CustomizeWindowHint | 
                                          Qt.WindowCloseButtonHint | 
                                          Qt.WindowMinimizeButtonHint)
            layout = QVBoxLayout()
            imageViewer = pg.GraphicsLayoutWidget()
            widget = QWidget()
            widget.setLayout(layout)
            self.subWindow.setWidget(widget)
            self.lblImageMissing = QLabel("<h4>Image Missing</h4>")
            self.lblImageMissing.hide()
            layout.addWidget(self.lblImageMissing)
            layout.addWidget(imageViewer)
            viewBox = imageViewer.addViewBox()
            viewBox.setAspectLocked(True)
            self.img = pg.ImageItem(border='w')
            viewBox.addItem(self.img)
            #Check that pixel array holds an image & display it
            if pixelArray is None:
                #Missing image, perhaps deleted,
                #so display a missing image label 
                self.lblImageMissing.show()
                #Display a black box
                self.img.setImage(np.array([[0,0,0],[0,0,0]])) 
            else:
                self.img.setImage(pixelArray) 
                self.lblImageMissing.hide()
                
            self.subWindow.setObjectName(imagePath)
            windowTitle = self.getDICOMFileData()
            self.subWindow.setWindowTitle(windowTitle)
            self.subWindow.setGeometry(0,0,800,600)
            self.mdiArea.addSubWindow(self.subWindow)
            self.subWindow.show()
        except Exception as e:
            print('Error in displayImageSubWindow: ' + str(e))


    def displayMultiImageSubWindow(self, imageList, studyName, 
                     seriesName, sliderPosition = -1):
        """
        Creates a subwindow that displays all the DICOM images in a series. 
        A slider allows the user to navigate  through the images.  A delete
        button allows the user to delete the image they are viewing.
        """
        try:
            self.subWindow = QMdiSubWindow(self)
            self.subWindow.setAttribute(Qt.WA_DeleteOnClose)
            self.subWindow.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
            layout = QVBoxLayout()
            imageViewer = pg.GraphicsLayoutWidget()
            widget = QWidget()
            widget.setLayout(layout)
            self.subWindow.setWidget(widget)
            self.lblHiddenStudyID = QLabel(studyName)
            self.lblHiddenStudyID.hide()
            self.lblHiddenSeriesID = QLabel(seriesName)
            self.lblHiddenSeriesID.hide()
            self.lblImageMissing = QLabel("<h4>Image Missing</h4>")
            self.lblImageMissing.hide()
            self.btnDeleteDICOMFile = QPushButton('Delete DICOM Image')
            self.btnDeleteDICOMFile.setToolTip(
            'Deletes the DICOM image being viewed')
            self.btnDeleteDICOMFile.hide()
            self.btnDeleteDICOMFile.clicked.connect(self.deleteImageInMultiImageViewer)
            layout.addWidget(self.lblImageMissing)
            layout.addWidget(self.lblHiddenSeriesID)
            layout.addWidget(self.lblHiddenStudyID)
            layout.addWidget(self.btnDeleteDICOMFile)
            layout.addWidget(imageViewer)
            viewBox = imageViewer.addViewBox()
            viewBox.setAspectLocked(True)
            self.img = pg.ImageItem(border='w')
            viewBox.addItem(self.img)

            self.imageSlider = QSlider(Qt.Horizontal)
            self.imageSlider.setMinimum(1)
            self.imageSlider.setMaximum(len(imageList))
            if sliderPosition == -1:
                self.imageSlider.setValue(1)
            else:
                self.imageSlider.setValue(sliderPosition)
            self.imageSlider.setSingleStep(1)
            self.imageSlider.setTickPosition(QSlider.TicksBothSides)
            self.imageSlider.setTickInterval(1)
            self.imageSlider.valueChanged.connect(
                  lambda: self.imageSliderMoved(seriesName, imageList))
            #print('Num of images = {}'.format(len(imageList)))
            layout.addWidget(self.imageSlider)
            
            #Display the first image in the viewer
            self.imageSliderMoved(seriesName, imageList)
            
            self.subWindow.setObjectName(seriesName)
            self.subWindow.setGeometry(0,0,800,600)
            self.mdiArea.addSubWindow(self.subWindow)
            self.subWindow.show()
        except Exception as e:
            print('Error in displayMultiImageSubWindow: ' + str(e))


    def deleteImageInMultiImageViewer(self):
        """When the Delete button is clicked on the multi image viewer,
        this function deletes the physical image and removes the 
        reference to it in the XML file."""
        try:
            imageName = os.path.basename(self.currentImagePath)
            studyID = self.lblHiddenStudyID.text()
            seriesID = self.lblHiddenSeriesID.text()

            buttonReply = QMessageBox.question(self, 
                'Delete DICOM image', "You are about to delete image {}".format(imageName), 
                QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)

            if buttonReply == QMessageBox.Ok:
                #Delete physical file
                deletedFilePath = self.currentImagePath
                os.remove(deletedFilePath)
                #Remove deleted image from the list
                self.imageList.remove(deletedFilePath)
                lastSliderPosition = self.imageSlider.value()

                #Refresh the multi-image viewer to remove deleted image
                #First close it
                self.closeSubWindow(seriesID)
                
                if len(self.imageList) == 0:
                    #Only redisplay the multi-image viewer if there
                    #are still images in the series to display
                    #The image list is empty, so do not redisplay
                    #multi image viewer 
                    pass   
                elif len(self.imageList) == 1:
                    #There is only one image left in the display
                    self.displayMultiImageSubWindow(self.imageList, studyID, seriesID)
                elif len(self.imageList) + 1 == lastSliderPosition:    
                     #we are deleting the nth image in a series of n images
                     #so move the slider back to penultimate image in list 
                    self.displayMultiImageSubWindow(self.imageList, 
                                      studyID, seriesID, len(self.imageList))
                else:
                    #We are deleting an image at the start of the list
                    #or in the body of the list. Move slider forwards to 
                    #the next image in the list.
                    self.displayMultiImageSubWindow(self.imageList, 
                                      studyID, seriesID, lastSliderPosition)
     
                #Now update XML file
                #Get the series containing this image and count the images it contains
                #If it is the last image in a series then remove the
                #whole series from XML file
                #If it is not the last image in a series
                #just remove the image from the XML file 
                xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                ']/series[@id=' + chr(34) + seriesID + chr(34) + ']/image'
                #print(xPath)
                images = self.root.findall(xPath)
                if len(images) == 1:
                    #only one image, so remove the series from the xml file
                    #need to get study (parent) containing this series (child)
                    #then remove child from parent
                    self.removeSeriesFromXMLFile(studyID, seriesID)
                elif len(images) > 1:
                    #more than 1 image in the series, 
                    #so just remove the image from the xml file
                    #need to get the series (parent) containing this image (child)
                    #then remove child from parent
                    xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                    ']/series[@id=' + chr(34) + seriesID + chr(34) + ']'
                    series = self.root.find(xPath)
                    #print('XML = {}'.format(ET.tostring(series)))
                    for image in series:
                        if image.find('name').text == deletedFilePath:
                            series.remove(image)
                            self.XMLtree.write(self.DICOM_XML_FilePath)
                            break
                #Update tree view with xml file modified above
                self.refreshDICOMStudiesTreeView()
        except Exception as e:
            print('Error in deleteImageInMultiImageViewer: ' + str(e))


    def imageSliderMoved(self, seriesName, imageList):
      try:
        imageNumber = self.imageSlider.value()
        self.currentImageNumber = imageNumber - 1
        if self.currentImageNumber >= 0:
            self.currentImagePath = imageList[self.currentImageNumber]
            pixelArray = readDICOM_Image.returnPixelArray(self.currentImagePath)
            if pixelArray is None:
                self.lblImageMissing.show()
                self.btnDeleteDICOMFile.hide()
                self.img.setImage(np.array([[0,0,0],[0,0,0]]))  
            else:
                self.img.setImage(pixelArray) 
                self.lblImageMissing.hide()
                self.btnDeleteDICOMFile.show()

            self.subWindow.setWindowTitle(seriesName + ' - ' 
                     + os.path.basename(self.currentImagePath))
      except Exception as e:
            print('Error in imageSliderMoved: ' + str(e))


    def viewImage(self):
        """Creates a subwindow that displays a DICOM image. Either executed using the 
        'View Image' Menu item in the Tools menu or by double clicking the Image name 
        in the DICOM studies tree view."""
        try:
            if self.isAnImageSelected():
                imagePath = self.selectedImagePath
                pixelArray = readDICOM_Image.returnPixelArray(imagePath)
                self.displayImageSubWindow(pixelArray, imagePath)
            elif self.isASeriesSelected():
                studyID = self.selectedStudy 
                seriesID = self.selectedSeries
                self.imageList = self.getImagePathList(studyID, seriesID)
                self.displayMultiImageSubWindow(self.imageList, studyID, seriesID)
        except Exception as e:
            print('Error in viewImage: ' + str(e))


    def insertNewBinOpImageInXMLFile(self, newImageFileName, suffix):
        try:
            studyID = self.selectedStudy 
            seriesID = self.selectedSeries

            #First determine if a series with parentID=seriesID exists
            #and typeID=suffix for a binary operation
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                ']/series[@parentID=' + chr(34) + seriesID + chr(34) + ']' \
               '[@typeID=' + chr(34) + suffix + chr(34) +']'
            series = self.root.find(xPath)
            #image date & time are set to current date and time
            now = datetime.now()
            imageTime = now.strftime("%H:%M:%S")
            imageDate = now.strftime("%d/%m/%Y")        
            if series is None:
                #Need to create a new series to hold this new image
                newSeriesID = seriesID + suffix
                #Get study branch
                xPath = './study[@id=' + chr(34) + studyID + chr(34) + ']'
                currentStudy = self.root.find(xPath)
                newAttributes = {'id':newSeriesID, 
                                 'parentID':seriesID, 
                                 'typeID':suffix}
                   
                #Add new series to study to hold new images
                newSeries = ET.SubElement(currentStudy, 'series', newAttributes)
                    
                comment = ET.Comment('This series holds images derived from binary operations on 2 images')
                newSeries.append(comment)   
                
                #Now add image element
                newImage = ET.SubElement(newSeries,'image')
                #Add child nodes of the image element
                nameNewImage = ET.SubElement(newImage, 'name')
                nameNewImage.text = newImageFileName
                timeNewImage = ET.SubElement(newImage, 'time')
                timeNewImage.text = imageTime
                dateNewImage = ET.SubElement(newImage, 'date')
                dateNewImage.text = imageDate
                self.XMLtree.write(self.DICOM_XML_FilePath)
                return newSeriesID
            else:
                #A series already exists to hold new images from
                #the current parent series
                newImage = ET.SubElement(series,'image')
                #Add child nodes of the image element
                nameNewImage = ET.SubElement(newImage, 'name')
                nameNewImage.text = newImageFileName
                timeNewImage = ET.SubElement(newImage, 'time')
                timeNewImage.text = imageTime
                dateNewImage = ET.SubElement(newImage, 'date')
                dateNewImage.text = imageDate
                self.XMLtree.write(self.DICOM_XML_FilePath)
                return series.attrib['id']
        except Exception as e:
            print('Error in insertNewBinOpImageInXMLFile: ' + str(e))


    def insertNewImageInXMLFile(self, newImageFileName, suffix):
        try:
            studyID = self.selectedStudy 
            seriesID = self.selectedSeries
            imagePath = self.selectedImagePath

            #First determine if a series with parentID=seriesID exists
            #and typeID=suffix
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                ']/series[@parentID=' + chr(34) + seriesID + chr(34) + ']' \
               '[@typeID=' + chr(34) + suffix + chr(34) +']'
            series = self.root.find(xPath)
                    
            if series is None:
                #Need to create a new series to hold this new image
                newSeriesID = seriesID + suffix
                #Get study branch
                xPath = './study[@id=' + chr(34) + studyID + chr(34) + ']'
                currentStudy = self.root.find(xPath)
                newAttributes = {'id':newSeriesID, 
                                 'parentID':seriesID, 
                                 'typeID':suffix}
                   
                #Add new series to study to hold new images
                newSeries = ET.SubElement(currentStudy, 'series', newAttributes)
                    
                comment = ET.Comment('This series holds new images')
                newSeries.append(comment)
                #Get image date & time
                imageTime, imageDate = self.getImageDateTime(imagePath, 
                                   studyID, seriesID)
                    
                #print("image time {}, date {}".format(imageTime, imageDate))
                #Now add image element
                newImage = ET.SubElement(newSeries,'image')
                #Add child nodes of the image element
                nameNewImage = ET.SubElement(newImage, 'name')
                nameNewImage.text = newImageFileName
                timeNewImage = ET.SubElement(newImage, 'time')
                timeNewImage.text = imageTime
                dateNewImage = ET.SubElement(newImage, 'date')
                dateNewImage.text = imageDate
                self.XMLtree.write(self.DICOM_XML_FilePath)
                return newSeriesID
            else:
                #A series already exists to hold new images from
                #the current parent series
                imageTime, imageDate = self.getImageDateTime(imagePath, 
                          studyID, seriesID)
                newImage = ET.SubElement(series,'image')
                #Add child nodes of the image element
                nameNewImage = ET.SubElement(newImage, 'name')
                nameNewImage.text = newImageFileName
                timeNewImage = ET.SubElement(newImage, 'time')
                timeNewImage.text = imageTime
                dateNewImage = ET.SubElement(newImage, 'date')
                dateNewImage.text = imageDate
                self.XMLtree.write(self.DICOM_XML_FilePath)
                return series.attrib['id']
        except Exception as e:
            print('Error in insertNewImageInXMLFile: ' + str(e))


    def getNewSeriesName(self, studyID, seriesID, suffix):
        """This function uses recursion to find the next available
        series name.  A new series name is created by adding a suffix
        at the end of an existing series name. """
        try:
            seriesID = seriesID + suffix
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
            ']/series[@id=' + chr(34) + seriesID + chr(34) + ']/image'
            #print(xPath)
            imageList = self.root.findall(xPath)
            if imageList:
                #A series of images already exists 
                #for the series called seriesID
                #so make another new series ID 
                #by adding the suffix to the previous
                #new series ID
                return self.getNewSeriesName(studyID, seriesID, suffix)
            else:
                return seriesID
        except Exception as e:
            print('Error in getNewSeriesName: ' + str(e))


    def insertNewSeriesInXMLFile(self, origImageList, newImageList, suffix):
        """Creates a new series to hold the series of New images"""
        try:
            #Get current study & series IDs
            studyID = self.selectedStudy 
            seriesID = self.selectedSeries 
            #Get a new series ID
            newSeriesID = self.getNewSeriesName(studyID, seriesID, suffix)
            #Get study branch
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + ']'
            currentStudy = self.root.find(xPath)
            newAttributes = {'id':newSeriesID, 
                             'parentID':seriesID,
                             'typeID':suffix}
                   
            #Add new series to study to hold new images
            newSeries = ET.SubElement(currentStudy, 'series', newAttributes)
                    
            comment = ET.Comment('This series holds a whole series of new images')
            newSeries.append(comment)
            #Get image date & time from original image
            for index, image in enumerate(origImageList):
                imageTime, imageDate = self.getImageDateTime(image, studyID, seriesID)       
                newImage = ET.SubElement(newSeries,'image')
                #Add child nodes of the image element
                nameNewImage = ET.SubElement(newImage, 'name')
                nameNewImage.text = newImageList[index]
                timeNewImage = ET.SubElement(newImage, 'time')
                timeNewImage.text = imageTime
                dateNewImage = ET.SubElement(newImage, 'date')
                dateNewImage.text = imageDate

            self.XMLtree.write(self.DICOM_XML_FilePath)
            self.statusBar.showMessage('New series created: - ' + newSeriesID)
            return  newSeriesID

        except Exception as e:
            print('Error in insertNewSeriesInXMLFile: ' + str(e))


    def removeSeriesFromXMLFile(self, studyID, seriesID):
        try:
            xPath = './study[@id=' + chr(34) + studyID + chr(34) +']' 
            study = self.root.find(xPath)
            #print('XML = {}'.format(ET.tostring(study)))
            for series in study:
                if series.attrib['id'] == seriesID:
                    study.remove(series)
                    self.XMLtree.write(self.DICOM_XML_FilePath)
                    break
        except Exception as e:
            print('Error in removeSeriesFromXMLFile: ' + str(e))


    def closeSubWindow(self, objectName):
        for subWin in self.mdiArea.subWindowList():
            if subWin.objectName() == objectName:
                QApplication.processEvents()
                subWin.close()
                QApplication.processEvents()
                break

    def closeAllImageWindows(self):
        for subWin in self.mdiArea.subWindowList():
            if subWin.objectName() == 'tree_view':
                continue
            subWin.close()
            QApplication.processEvents()
               

    def displayBinaryOperationsWindow(self):
        try:
            self.subWindow = QMdiSubWindow(self)
            self.subWindow.setAttribute(Qt.WA_DeleteOnClose)
            self.subWindow.setWindowFlags(Qt.CustomizeWindowHint
                  | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
            layout = QGridLayout()
            widget = QWidget()
            widget.setLayout(layout)
            self.subWindow.setWidget(widget)

            imageViewer1 = pg.GraphicsLayoutWidget()
            viewBox1 = imageViewer1.addViewBox()
            viewBox1.setAspectLocked(True)
            self.img1 = pg.ImageItem(border='w')
            viewBox1.addItem(self.img1)

            imageViewer2 = pg.GraphicsLayoutWidget()
            viewBox2 = imageViewer2.addViewBox()
            viewBox2.setAspectLocked(True)
            self.img2 = pg.ImageItem(border='w')
            viewBox2.addItem(self.img2)

            imageViewer3 = pg.GraphicsLayoutWidget()
            viewBox3 = imageViewer3.addViewBox()
            viewBox3.setAspectLocked(True)
            self.img3 = pg.ImageItem(border='w')
            viewBox3.addItem(self.img3)

            studyID = self.selectedStudy 
            seriesID = self.selectedSeries
            self.lblImageMissing1 = QLabel("<h4>Image Missing</h4>")
            self.lblImageMissing2 = QLabel("<h4>Image Missing</h4>")
            self.lblImageMissing1.hide()
            self.lblImageMissing2.hide()

            self.btnSave = QPushButton('Save')
            self.btnSave.setEnabled(False)
            self.btnSave.clicked.connect(self.saveNewDICOMFileFromBinOp)

            studyID = self.selectedStudy 
            seriesID = self.selectedSeries
            imagePathList = self.getImagePathList(studyID, seriesID)
            #form a list of image file names without extensions
            imageNameList = [os.path.splitext(os.path.basename(image))[0] 
                             for image in imagePathList]
            self.image_Name_Path_Dict = dict(zip(
                imageNameList, imagePathList))
            self.imageList1 = QComboBox()
            self.imageList2 = QComboBox()
            self.imageList1.currentIndexChanged.connect(
                lambda:self.displayImageForBinOp(1, self.image_Name_Path_Dict))
            self.imageList1.currentIndexChanged.connect(
                self.enableBinaryOperationsCombo)
            self.imageList1.currentIndexChanged.connect(
                lambda:self.doBinaryOperation(self.image_Name_Path_Dict))
            
            self.imageList2.currentIndexChanged.connect(
                lambda:self.displayImageForBinOp(2, self.image_Name_Path_Dict))
            self.imageList2.currentIndexChanged.connect(
                self.enableBinaryOperationsCombo)
            self.imageList2.currentIndexChanged.connect(
                lambda:self.doBinaryOperation(self.image_Name_Path_Dict))

            self.binaryOpsList = QComboBox()
            self.binaryOpsList.currentIndexChanged.connect(
                lambda:self.doBinaryOperation(self.image_Name_Path_Dict))
            self.imageList1.addItems(imageNameList)
            self.imageList2.addItems(imageNameList)
            self.binaryOpsList.addItems(
                binaryOperationDICOM_Image.listBinaryOperations)

            layout.addWidget(self.btnSave, 0, 2)
            layout.addWidget(self.imageList1, 1, 0)
            layout.addWidget(self.imageList2, 1, 1)
            layout.addWidget(self.binaryOpsList, 1, 2)
            layout.addWidget(self.lblImageMissing1, 2, 0)
            layout.addWidget(self.lblImageMissing2, 2, 1)
            layout.addWidget(imageViewer1, 3, 0)
            layout.addWidget(imageViewer2, 3, 1)
            layout.addWidget(imageViewer3, 3, 2)
                
            self.subWindow.setObjectName('Binary_Operation')
            windowTitle = 'Binary Operations'
            self.subWindow.setWindowTitle(windowTitle)
            self.subWindow.setGeometry(0,0,1600,800)
            self.mdiArea.addSubWindow(self.subWindow)
            self.subWindow.show()
        except Exception as e:
            print('Error in displayBinaryOperationsWindow: ' + str(e))

    
    def saveNewDICOMFileFromBinOp(self):
        try:
            suffix = '_binOp'
            imageName1 = self.imageList1.currentText()
            imagePath1 = self.image_Name_Path_Dict[imageName1]
            imageName2 = self.imageList2.currentText()
            imagePath2 = self.image_Name_Path_Dict[imageName2]
            
            binaryOperation = self.binaryOpsList.currentText()
            prefix = binaryOperationDICOM_Image.getBinOperationFilePrefix(
                                     binaryOperation)
            
            newImageFileName = prefix + '_' + imageName1 \
                + '_' + imageName2 
            newImageFilePath = os.path.dirname(imagePath1) + '\\' + \
                newImageFileName + '.dcm'
            #print(newImageFilePath)
            #Save pixel array to a file
            saveDICOM_Image.save_dicom_binOpResult(imagePath1, imagePath2, self.binOpArray, newImageFilePath, binaryOperation+suffix)
            newSeriesID = self.insertNewBinOpImageInXMLFile(newImageFilePath, suffix)
            print(newSeriesID)
            self.refreshDICOMStudiesTreeView(newSeriesID)
        except Exception as e:
            print('Error in saveNewDICOMFileFromBinOp: ' + str(e))


    def doBinaryOperation(self, imageDict):
        try:
            #Get file path of image1
            imageName = self.imageList1.currentText()
            if imageName != '':
                imagePath1 = imageDict[imageName]

            #Get file path of image2
            imageName = self.imageList2.currentText()
            if imageName != '':
                imagePath2 = imageDict[imageName]

            #Get binary operation to be performed
            binOp = self.binaryOpsList.currentText()
            if binOp != 'Select binary Operation' \
                and binOp != '':
                self.binOpArray = binaryOperationDICOM_Image.returnPixelArray(
                    imagePath1, imagePath2, binOp)
                self.img3.setImage(self.binOpArray)
        except Exception as e:
            print('Error in doBinaryOperation: ' + str(e))


    def enableBinaryOperationsCombo(self):
        if self.lblImageMissing1.isHidden() and \
            self.lblImageMissing2.isHidden():
            self.binaryOpsList.setEnabled(True)
            self.btnSave.setEnabled(True)
        else:
            self.binaryOpsList.setEnabled(False)
            self.btnSave.setEnabled(False)


    def displayImageForBinOp(self, imageNumber, imageDict):
        try:
            objImageMissingLabel = getattr(self, 'lblImageMissing' + str(imageNumber))
            objImage = getattr(self, 'img' + str(imageNumber))
            objComboBox = getattr(self, 'imageList' + str(imageNumber))

            #get name of selected image
            imageName = objComboBox.currentText()
            imagePath = imageDict[imageName]
            pixelArray = readDICOM_Image.returnPixelArray(imagePath)
            if pixelArray is None:
                objImageMissingLabel.show()
                objImage.setImage(np.array([[0,0,0],[0,0,0]])) 
            else:
                objImageMissingLabel.hide()
                objImage.setImage(pixelArray) 
        except Exception as e:
            print('Error in displayImageForBinOp: ' + str(e))


    def getImagePathList(self, studyID, seriesID):
        try:
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
            ']/series[@id=' + chr(34) + seriesID + chr(34) + ']/image'
            #print(xPath)
            images = self.root.findall(xPath)
            imageList = [image.find('name').text for image in images]
            return imageList
        except Exception as e:
            print('Error in getImagePathList: ' + str(e))


    def deleteImage(self):
        """This method deletes an image or a series of images by 
        deleting the physical file(s) and then removing their entries
        in the XML file."""
        try:
            studyID = self.selectedStudy
            seriesID = self.selectedSeries
            if self.isAnImageSelected():
                imageName = self.selectedImageName
                imagePath = self.selectedImagePath
                buttonReply = QMessageBox.question(self, 
                  'Delete DICOM image', "You are about to delete image {}".format(imageName), 
                  QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                if buttonReply == QMessageBox.Ok:
                    #Delete physical file if it exists
                    if os.path.exists(imagePath):
                        os.remove(imagePath)
                    #If this image is displayed, close its subwindow
                    self.closeSubWindow(imagePath)
                    #Is this the last image in a series?
                    #Get the series containing this image and count the images it contains
                    #If it is the last image in a series then remove the
                    #whole series from XML file
                    #No it is not the last image in a series
                    #so just remove the image from the XML file 
                    xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                    ']/series[@id=' + chr(34) + seriesID + chr(34) + ']/image'
                    #print(xPath)
                    images = self.root.findall(xPath)
                    if len(images) == 1:
                        #only one image, so remove the series from the xml file
                        #need to get study (parent) containing this series (child)
                        #then remove child from parent
                        self.removeSeriesFromXMLFile(studyID, seriesID)
                    elif len(images) > 1:
                        #more than 1 image in the series, 
                        #so just remove the image from the xml file
                        #need to get the series (parent) containing this image (child)
                        #then remove child from parent
                        xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                        ']/series[@id=' + chr(34) + seriesID + chr(34) + ']'
                        series = self.root.find(xPath)
                        #print('XML = {}'.format(ET.tostring(series)))
                        for image in series:
                            if image.find('name').text == imagePath:
                                series.remove(image)
                                self.XMLtree.write(self.DICOM_XML_FilePath)
                    #Update tree view with xml file modified above
                    self.refreshDICOMStudiesTreeView()
            elif self.isASeriesSelected():
                buttonReply = QMessageBox.question(self, 
                  'Delete DICOM series', "You are about to delete series {}".format(seriesID), 
                  QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                if buttonReply == QMessageBox.Ok:
                    #Delete each physical file in the series
                    #Get a list of names of images in that series
                    imageList = self.getImagePathList(studyID, seriesID) 
                    #Iterate through list of images and delete each image
                    for imagePath in imageList:
                        if os.path.exists(imagePath):
                            os.remove(imagePath)
                    #Remove the series from the XML file
                    self.removeSeriesFromXMLFile(studyID, seriesID)
                    self.closeSubWindow(seriesID)
                self.refreshDICOMStudiesTreeView()
        except Exception as e:
            print('Error in deleteImage: ' + str(e))


    def getImageDateTime(self, imageName, studyID, seriesID):
        try:
            #Get reference to image element time of the image

            xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                    ']/series[@id=' + chr(34) + seriesID + chr(34) + ']' + \
                    '/image[name=' + chr(34) + imageName + chr(34) +']/time'
            imageTime = self.root.find(xPath)
            
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                    ']/series[@id=' + chr(34) + seriesID + chr(34) + ']' + \
                    '/image[name=' + chr(34) + imageName + chr(34) +']/date'
            imageDate = self.root.find(xPath)

            return imageTime.text, imageDate.text           
        except Exception as e:
            print('Error in getImageDateTime: ' + str(e))


    def isAnImageSelected(self):
        try:
            selectedItem = self.treeView.currentItem()
            if 'image' in selectedItem.text(0).lower():
                return True
            else:
                return False
        except Exception as e:
            print('Error in isAnImageSelected: ' + str(e))
    
    
    def isASeriesSelected(self):
        try:
            selectedItem = self.treeView.currentItem()
            if 'series' in selectedItem.text(0).lower():
                return True
            else:
                return False
        except Exception as e:
            print('Error in isASeriesSelected: ' + str(e))


    def setEnabledSeriesOnlyTools(self, flag):
        try:
            for tool in buildToolsMenu.seriesOnlyTools:
                button = getattr(self, tool)
                button.setEnabled(flag)
        except Exception as e:
            print('Error in setEnabledSeriesOnlyTools: ' + str(e))


    def setEnabledImageAndSeriesTools(self, flag):
        try:
            for tool in buildToolsMenu.imageAndSeriesTools:
                button = getattr(self, tool)
                button.setEnabled(flag)
        except Exception as e:
            print('Error in setEnabledImageAndSeriesTools: ' + str(e))


    def toggleToolButtons(self):
        try:
            if self.isASeriesSelected():
                self.setEnabledSeriesOnlyTools(True)
            else:
                self.setEnabledSeriesOnlyTools(False)

            if self.isAnImageSelected() or self.isASeriesSelected():
                self.viewImageButton.setEnabled(True)
                self.deleteImageButton.setEnabled(True)
                self.setEnabledImageAndSeriesTools(True)
            else:
                self.viewImageButton.setEnabled(False)
                self.deleteImageButton.setEnabled(False)
                self.setEnabledImageAndSeriesTools(False)
        except Exception as e:
            print('Error in toggleToolButtons: ' + str(e))


    def getDICOMFileData(self):
        """When a DICOM image is selected in the tree view, this function
        returns its description in the form - study number: series number: image name"""
        try:
            selectedImage = self.treeView.selectedItems()
            if selectedImage:
                imageNode = selectedImage[0]
                seriesNode  = imageNode.parent()
                imageName = imageNode.text(0)
                series = seriesNode.text(0)
                studyNode = seriesNode.parent()
                study = studyNode.text(0)
                fullImageName = study + ': ' + series + ': '  + imageName
                return fullImageName
            else:
                return ''
        except Exception as e:
            print('Error in getDICOMFileData: ' + str(e))


    def expandTreeViewBranch(self, branchText = ''):
        try:
            for branch in self.seriesBranchList:
                seriesID = branch.text(0).replace('Series -', '')
                seriesID = seriesID.strip()
                if seriesID == branchText:
                    branch.setExpanded(True)
                else:
                    branch.setExpanded(False)
        except Exception as e:
            print('Error in expandTreeViewBranch: ' + str(e))


    def refreshDICOMStudiesTreeView(self, newSeriesName = ''):
        """Uses an XML file that describes a DICOM file structure to build a
        tree view showing a visual representation of that file structure."""
        try:
            self.XMLtree = ET.parse(self.DICOM_XML_FilePath)
            self.root = self.XMLtree.getroot()
            self.treeView.clear()
            self.treeView.setColumnCount(3)
            self.treeView.setHeaderLabels(["DICOM Files", "Date", "Time", "Path"])
                
            # Uncomment to test XML file loaded OK
            #print(ET.tostring(self.root, encoding='utf8').decode('utf8'))
            studies = self.root.findall('./study')
            for study in studies:
                studyID = study.attrib['id']
                studyBranch = QTreeWidgetItem(self.treeView)
                studyBranch.setText(0, "Study - {}".format(studyID))
                studyBranch.setFlags(studyBranch.flags() & ~Qt.ItemIsSelectable)
                studyBranch.setExpanded(True)
                self.seriesBranchList.clear()
                for series in study:
                    seriesID = series.attrib['id']
                    seriesBranch = QTreeWidgetItem(studyBranch)
                    self.seriesBranchList.append(seriesBranch)
                    seriesBranch.setFlags(seriesBranch.flags() | Qt.ItemIsUserCheckable)
                    seriesBranch.setText(0, "Series - {}".format(seriesID))
                    seriesBranch.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    seriesBranch.setExpanded(True)
                    for image in series:
                        #Extract filename from file path
                        imageName = os.path.basename(image.find('name').text)
                        imageDate = image.find('date').text
                        imageTime = image.find('time').text
                        imagePath = image.find('name').text
                        imageLeaf = QTreeWidgetItem(seriesBranch)
                        imageLeaf.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                        imageLeaf.setFlags(imageLeaf.flags() | Qt.ItemIsUserCheckable)
                        #Uncomment the next line to put a checkbox in front of each image
                        #imageLeaf.setCheckState(0, Qt.Unchecked)
                        imageLeaf.setText(0, ' Image - ' +imageName)
                        imageLeaf.setText(1, imageDate)
                        imageLeaf.setText(2, imageTime)
                        imageLeaf.setText(3, imagePath)
            self.treeView.resizeColumnToContents(0)
            self.treeView.resizeColumnToContents(1)
            self.treeView.resizeColumnToContents(2)
            #Now collapse all series branches so as to hide the images
            #except the new series branch that has been created
            self.expandTreeViewBranch(newSeriesName)
            self.treeView.hideColumn(3)
            self.treeView.show()
        except Exception as e:
            print('Error in refreshDICOMStudiesTreeView: ' + str(e))

      #self
    def getStudyAndSeriesNumbersFromSeries():
        """This function returns the study and series IDs
        from the selected series in a tree view."""
        try: 
            selectedSeries = self.treeView.selectedItems()
            if selectedSeries:
                #Extract series name from the selected image
                seriesNode = selectedSeries[0]
                seriesName = seriesNode.text(0) 
                #Extract series number from the full series name
                seriesID = seriesName.replace('Series - ', '')
                seriesID = seriesID.strip() 

                studyNode = seriesNode.parent()
                studyName = studyNode.text(0)
                #Extract study number from the full study name
                studyID = studyName.replace('Study - ', '')
                studyID = studyID.strip()
                return studyID, seriesID
            else:
                return None, None
        except Exception as e:
            print('Error in getStudyAndSeriesNumbersFromSeries: ' + str(e))

    def getImagePathList_Copy():
        try:
            studyID, seriesID = \
            getStudyAndSeriesNumbersFromSeries() #self.
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
            ']/series[@id=' + chr(34) + seriesID + chr(34) + ']/image'
            #print(xPath)
            images = self.root.findall(xPath)
            imageList = [image.find('name').text for image in images]
            return imageList, studyID, seriesID
        except Exception as e:
            print('Error in getImagePathList: ' + str(e))

def main():
    app = QApplication([])
    winMDI = Weasel()
    winMDI.showMaximized()
    sys.exit(app.exec())

if __name__ == '__main__':
        main()