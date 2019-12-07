
from PyQt5 import QtCore
from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QLabel,
        QMdiArea, QMessageBox, QWidget, QVBoxLayout, QMdiSubWindow, QPushButton, 
        QTreeWidget, QTreeWidgetItem, QGridLayout, QSlider, QAbstractSlider,  QProgressBar )
from PyQt5.QtGui import QCursor

import xml.etree.ElementTree as ET 
from xml.dom import minidom
import pyqtgraph as pg
import os
import sys
import re
import styleSheet
import readDICOM_Image
import invertDICOM_Image
import WriteXMLfromDICOM 
import time
import numpy as np

__version__ = '1.0'
__author__ = 'Steve Shillitoe'

class MainWindow(QMainWindow):
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
        self.currentImagePath = ''
        #self.ApplyStyleSheet()
      

    def setupMenus(self):  
        """Builds the menus in the menu bar of the MDI"""
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')

        loadDICOM = QAction('Load DICOM Images', self)
        loadDICOM.setShortcut('Ctrl+F')
        loadDICOM.setStatusTip('Load DICOM images from a scan folder')
        loadDICOM.triggered.connect(self.loadDICOM)
        fileMenu.addAction(loadDICOM)

        closeAllSubWindowsButton = QAction('Close All Sub Windows', self)
        closeAllSubWindowsButton.setShortcut('Ctrl+C')
        closeAllSubWindowsButton.setStatusTip('Closes all sub windows')
        closeAllSubWindowsButton.triggered.connect(self.closeAllSubWindows)
        fileMenu.addAction(closeAllSubWindowsButton)

        self.deleteImageButton = QAction('Delete Image', self)
        self.deleteImageButton.setShortcut('Ctrl+D')
        self.deleteImageButton.setStatusTip('Delete a DICOM Image or series')
        self.deleteImageButton.triggered.connect(self.deleteImage)
        self.deleteImageButton.setEnabled(False)
        toolsMenu.addAction(self.deleteImageButton)

        self.invertImageButton = QAction('Invert Image', self)
        self.invertImageButton.setShortcut('Ctrl+I')
        self.invertImageButton.setStatusTip('Invert a DICOM Image or series')
        self.invertImageButton.triggered.connect(self.invertImage)
        self.invertImageButton.setEnabled(False)
        toolsMenu.addAction(self.invertImageButton)

        self.viewImageButton = QAction('View Image', self)
        self.viewImageButton.setShortcut('Ctrl+V')
        self.viewImageButton.setStatusTip('View DICOM Image or series')
        self.viewImageButton.triggered.connect(self.viewImage)
        self.viewImageButton.setEnabled(False)
        toolsMenu.addAction(self.viewImageButton)


    def ApplyStyleSheet(self):
        """Modifies the appearance of the GUI using CSS instructions"""
        try:
            self.setStyleSheet(styleSheet.TRISTAN_GREY)
        except Exception as e:
            print('Error in function ApplyStyleSheet: ' + str(e))
     

    def getScanDirectory(self):
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
                #print(self.DICOMfolderPath)
                start_time=time.time()
                self.XMLtree = ET.parse(XML_File_Path)
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
                subWindow.setObjectName("New_Window")
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
                    for series in study:
                        seriesID = series.attrib['id']
                        seriesBranch = QTreeWidgetItem(studyBranch)
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
                            imageName = os.path.basename(image.find('name').text)
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
                        #Now collapse the series branch so as to hide the images
                        seriesBranch.setExpanded(False)
                        
                self.treeView.itemSelectionChanged.connect(self.toggleToolButtons)
                self.treeView.itemDoubleClicked.connect(self.viewImage)
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


    def closeAllSubWindows(self):
        self.mdiArea.closeAllSubWindows()
        self.treeView = None


    def displayImageSubWindow(self, pixelArray, imagePath):
        """
        Creates a subwindow that displays the DICOM image contained in pixelArray. 
        """
        try:
            self.subWindow = QMdiSubWindow(self)
            self.subWindow.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
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
            #Test pixel array holds image & display it
            if pixelArray is None:
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


    def displayMultiImageSubWindow(self, imageList, studyName, seriesName):
        """
        Creates a subwindow that displays all the DICOM images in a series. 
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
            self.imageSlider.setValue(1)
            self.imageSlider.setSingleStep(1)
            self.imageSlider.setTickPosition(QSlider.TicksBothSides)
            self.imageSlider.setTickInterval(1)
            self.imageSlider.sliderReleased.connect(
                  lambda: self.imageSliderChanged(seriesName, imageList))
            #print('Num of images = {}'.format(len(imageList)))
            layout.addWidget(self.imageSlider)
            
            #Display first image
            self.currentImageNumber = 0
            self.currentImagePath = imageList[self.currentImageNumber]
            pixelArray = readDICOM_Image.returnPixelArray(self.currentImagePath)
            if pixelArray is None:
                self.lblImageMissing.show()
                self.img.setImage(np.array([[0,0,0],[0,0,0]])) 
                self.btnDeleteDICOMFile.hide()
            else:
                self.img.setImage(pixelArray) 
                self.lblImageMissing.hide()
                self.btnDeleteDICOMFile.show()
                
            self.subWindow.setObjectName(seriesName)
            
            self.subWindow.setWindowTitle(seriesName + ' - ' + os.path.basename(imageList[0]))
            self.subWindow.setGeometry(0,0,800,600)
            self.mdiArea.addSubWindow(self.subWindow)
            self.subWindow.show()
        except Exception as e:
            print('Error in displayMultiImageSubWindow: ' + str(e))


    def deleteImageInMultiImageViewer(self):
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
                #Update slider maximum value
                #self.imageSlider.setMaximum(len(self.imageList))
                #Refresh the multi-image viewer to remove deleted image
                #First close it
                self.closeSubWindow(seriesID)
                QApplication.processEvents()
                if len(self.imageList) > 0:
                    #Only redisplay the multi-image viewer if there
                    #are still images in the series to display   
                    self.displayMultiImageSubWindow(self.imageList, studyID, seriesID)

                #elif len(self.imageList) == self.imageSlider.value():
                #    #we are deleting the last image in a series, 
                #    #so move slide back to the penultimate image
                #    #self.imageSlider.triggerAction(QAbstractSlider.SliderSingleStepSub)
                #else:
                #    pass
                #    #We are deleting an image in a series, so move to next image
                #    #self.imageSlider.triggerAction(QAbstractSlider.SliderSingleStepAdd)
                
                #Is this the last image in a series?
                #Get the series containing this image and count the images it contains
                #If it is the last image in a series then remove the
                #whole series from XML file
                #If it is not the last image in a series
                # just remove the image from the XML file 
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


    def imageSliderChanged(self, seriesName, imageList):
      try:
        #print('In image slider len of image list ={}'.format(len(imageList)))
        imageNumber = self.imageSlider.value()
        self.currentImageNumber = imageNumber - 1
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
                                      + os.path.basename(imageList[imageNumber - 1]))
      except Exception as e:
            print('Error in imageSliderChanged: ' + str(e))


    def viewImage(self):
        """Creates a subwindow that displays a DICOM image. Either executed using the 
        'View Image' Menu item in the Tools menu or by double clicking the Image name 
        in the DICOM studies tree view."""
        try:
            if self.isAnImageSelected():
                imagePath = self.getImagePath()
                pixelArray = readDICOM_Image.returnPixelArray(imagePath)
                self.displayImageSubWindow(pixelArray, imagePath)
            elif self.isASeriesSelected():
                studyID, seriesID = \
                    self.getStudyAndSeriesNumbersFromSeries()
                xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                ']/series[@id=' + chr(34) + seriesID + chr(34) + ']/image'
               # print(xPath)
                images = self.root.findall(xPath)
                self.imageList = [image.find('name').text for image in images] 
                self.displayMultiImageSubWindow(self.imageList, studyID, seriesID)
        except Exception as e:
            print('Error in viewImage: ' + str(e))


    def insertInvertedImageInXMLFile(self, invertedImageFileName):
        try:
            studyID, seriesID = self.getStudyAndSeriesNumbersForImage()
            #First determine if a series with parentID=seriesID exists
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                ']/series[@parentID=' + chr(34) + seriesID + chr(34) + ']'
            series = self.root.find(xPath)
            imageName = self.getImagePath()
                    
            if series is None:
                #Need to create a new series to hold this inverted image
                newSeriesID = seriesID + '_inv'
                #Get study branch
                xPath = './study[@id=' + chr(34) + studyID + chr(34) + ']'
                currentStudy = self.root.find(xPath)
                newAttributes = {'id':newSeriesID, 'parentID':seriesID}
                   
                #Add new series to study to hold inverted images
                newSeries = ET.SubElement(currentStudy, 'series', newAttributes)
                    
                comment = ET.Comment('This series holds inverted images')
                newSeries.append(comment)
                #Get image date & time
                imageTime, imageDate = self.getImageDateTime(imageName, studyID, seriesID)
                    
                #print("image time {}, date {}".format(imageTime, imageDate))
                #Now add image element
                newInvertedImage = ET.SubElement(newSeries,'image')
                #Add child nodes of the image element
                nameInvertedImage = ET.SubElement(newInvertedImage, 'name')
                nameInvertedImage.text = invertedImageFileName
                timeInvertedImage = ET.SubElement(newInvertedImage, 'time')
                timeInvertedImage.text = imageTime
                dateInvertedImage = ET.SubElement(newInvertedImage, 'date')
                dateInvertedImage.text = imageDate
                self.XMLtree.write(self.DICOM_XML_FilePath)
            else:
                #A series already exists to hold inverted images from
                #the current parent series
                imageTime, imageDate = self.getImageDateTime(imageName, studyID, seriesID)
                newInvertedImage = ET.SubElement(series,'image')
                #Add child nodes of the image element
                nameInvertedImage = ET.SubElement(newInvertedImage, 'name')
                nameInvertedImage.text = invertedImageFileName
                timeInvertedImage = ET.SubElement(newInvertedImage, 'time')
                timeInvertedImage.text = imageTime
                dateInvertedImage = ET.SubElement(newInvertedImage, 'date')
                dateInvertedImage.text = imageDate
                self.XMLtree.write(self.DICOM_XML_FilePath)
        except Exception as e:
            print('Error in insertInvertedImageInXMLFile: ' + str(e))
    

    def insertInvertedSeriesInXMLFile(self, origImageList, invertedImageList):
        """Creates a new series to hold the series of inverted images"""
        try:
            #Get current study & series IDs
            studyID, seriesID = \
                    self.getStudyAndSeriesNumbersFromSeries()
            #Need to create a new series to hold this series of inverted images 
            newSeriesID = seriesID + '_inv'
     
            #Get study branch
            xPath = './study[@id=' + chr(34) + studyID + chr(34) + ']'
            currentStudy = self.root.find(xPath)
            newAttributes = {'id':newSeriesID, 'parentID':seriesID}
                   
            #Add new series to study to hold inverted images
            newSeries = ET.SubElement(currentStudy, 'series', newAttributes)
                    
            comment = ET.Comment('This series holds a whole series of inverted images')
            newSeries.append(comment)
            #Get image date & time from original image
            for index, image in enumerate(origImageList):
                imageTime, imageDate = self.getImageDateTime(image, studyID, seriesID)       
                newInvertedImage = ET.SubElement(newSeries,'image')
                #Add child nodes of the image element
                nameInvertedImage = ET.SubElement(newInvertedImage, 'name')
                nameInvertedImage.text = invertedImageList[index]
                timeInvertedImage = ET.SubElement(newInvertedImage, 'time')
                timeInvertedImage.text = imageTime
                dateInvertedImage = ET.SubElement(newInvertedImage, 'date')
                dateInvertedImage.text = imageDate

            self.XMLtree.write(self.DICOM_XML_FilePath)
            return  newSeriesID

        except Exception as e:
            print('Error in insertInvertedSeriesInXMLFile: ' + str(e))


    def invertImage(self):
        """Creates a subwindow that displays an inverted DICOM image. Executed using the 
        'Invert Image' Menu item in the Tools menu."""
        try:
            if self.isAnImageSelected():
                imagePath = self.getImagePath()
                pixelArray, invertedImageFileName = \
                    invertDICOM_Image.returnPixelArray(imagePath)
                self.displayImageSubWindow(pixelArray, invertedImageFileName)
                #Record inverted image in XML file
                self.insertInvertedImageInXMLFile(invertedImageFileName)
                #Update tree view with xml file modified above
                self.refreshDICOMStudiesTreeView()
            elif self.isASeriesSelected():
                #Get Series ID & Study ID
                studyID, seriesID = \
                    self.getStudyAndSeriesNumbersFromSeries()
                #Get list of image paths
                xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                ']/series[@id=' + chr(34) + seriesID + chr(34) + ']/image'
                #print(xPath)
                images = self.root.findall(xPath)
                imageList = [image.find('name').text for image in images] 
                #Iterate through list of images and invert each image
                invertedImageList = []
                for imagePath in imageList:
                    _, invertedImageFileName = \
                    invertDICOM_Image.returnPixelArray(imagePath)
                    invertedImageList.append(invertedImageFileName)

                newSeriesName= self.insertInvertedSeriesInXMLFile(imageList, \
                    invertedImageList)
                self.displayMultiImageSubWindow(invertedImageList, studyID, newSeriesName)
                self.refreshDICOMStudiesTreeView()
        except Exception as e:
            print('Error in invertImage: ' + str(e))


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


    def deleteImage(self):
        """This method deletes an image or a series of images by 
        deleting the physical file(s) and then removing their entries
        in the XML file."""
        try:
            if self.isAnImageSelected():
                imagePath = self.getImagePath()
                imageName = self.treeView.currentItem().text(0)
                buttonReply = QMessageBox.question(self, 
                  'Delete DICOM image', "You are about to delete image {}".format(imageName), 
                  QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                if buttonReply == QMessageBox.Ok:
                    #Delete physical file
                    os.remove(imagePath)
                    #If this image is displayed, close its subwindow
                    self.closeSubWindow(imagePath)
                    #Is this the last image in a series?
                    #Get the series containing this image and count the images it contains
                    #If it is the last image in a series then remove the
                    #whole series from XML file
                    #No it is not the last image in a series
                    #so just remove the image from the XML file 
                    studyID, seriesID = \
                        self.getStudyAndSeriesNumbersForImage()
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
                seriesName = self.treeView.currentItem().text(0)
                buttonReply = QMessageBox.question(self, 
                  'Delete DICOM series', "You are about to delete series {}".format(seriesName), 
                  QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
                if buttonReply == QMessageBox.Ok:
                    #Delete each physical file in the series
                    #Get a list of names of images in that series
                    studyID, seriesID = \
                    self.getStudyAndSeriesNumbersFromSeries()
                    xPath = './study[@id=' + chr(34) + studyID + chr(34) + \
                    ']/series[@id=' + chr(34) + seriesID + chr(34) + ']/image'
                    #print(xPath)
                    images = self.root.findall(xPath)
                    imageList = [image.find('name').text for image in images] 
                    #Iterate through list of images and delete each image
                    for imagePath in imageList:
                        os.remove(imagePath)
                    #Remove the series from the XML file
                    self.removeSeriesFromXMLFile(studyID, seriesID)
                    self.closeSubWindow(seriesID)
                self.refreshDICOMStudiesTreeView()
        except Exception as e:
            print('Error in deleteImage: ' + str(e))


    def getStudyAndSeriesNumbersForImage(self):
        """This function assumes a series name takes the
        form 'series' space number, where number is an integer
        with one or more digits; 
        e.g., 'series 44' and returns the number as a string.
        
        Same assumption is made for the study name."""
        try: 
            selectedImage = self.treeView.selectedItems()
            if selectedImage:
                #Extract series name from the selected image
                imageNode = selectedImage[0]
                seriesNode  = imageNode.parent()
                seriesName = seriesNode.text(0) 
                #Extract series number from the full series name
                seriesID = seriesName.replace('Series -', '')
                seriesID = seriesID.strip()                

                studyNode = seriesNode.parent()
                studyName = studyNode.text(0)
                #Extract study number from the full study name
                studyID = studyName.replace('Study -', '')
                studyID = studyID.strip()
                return studyID, seriesID
            else:
                return None, None
        except Exception as e:
            print('Error in getStudyAndSeriesNumbersForImage: ' + str(e))


    def getStudyAndSeriesNumbersFromSeries(self):
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

    def getImagePath(self):
        try:
            selectedImage = self.treeView.currentItem()
            imagePath = selectedImage.text(3)
            return imagePath
        except Exception as e:
            return None
            print('Error in isAnImageSelected: ' + str(e))


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


    def toggleToolButtons(self):
        try:
            if self.isAnImageSelected() or self.isASeriesSelected():
                self.viewImageButton.setEnabled(True)
                self.invertImageButton.setEnabled(True)
                self.deleteImageButton.setEnabled(True)
                
            else:
                self.viewImageButton.setEnabled(False)
                self.invertImageButton.setEnabled(False)
                self.deleteImageButton.setEnabled(False)
                
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


    def refreshDICOMStudiesTreeView(self):
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
                for series in study:
                    seriesID = series.attrib['id']
                    seriesBranch = QTreeWidgetItem(studyBranch)
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
                        imageLeaf.setExpanded(True)

            self.treeView.resizeColumnToContents(0)
            self.treeView.resizeColumnToContents(1)
            self.treeView.resizeColumnToContents(2)
            self.treeView.hideColumn(3)
            self.treeView.show()
        except Exception as e:
            print('Error in refreshDICOMStudiesTreeView: ' + str(e))


def main():
    app = QApplication([])
    winMDI = MainWindow()
    winMDI.show()
    sys.exit(app.exec())

if __name__ == '__main__':
        main()