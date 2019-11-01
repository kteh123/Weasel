
from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QLabel,
        QMdiArea, QMessageBox, QWidget, QVBoxLayout, QMdiSubWindow, QPushButton, 
        QTreeWidget, QTreeWidgetItem, QGridLayout)

import xml.etree.ElementTree as ET 
import pydicom
import pyqtgraph as pg
import os
import sys
import re
import numpy as np
import styleSheet

__version__ = '1.0'
__author__ = 'Steve Shillitoe'

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        """Creates the MDI container."""
        QMainWindow.__init__(self, parent)
        self.setGeometry(0, 0, 2500, 1400)
        self.setWindowTitle("DICOM Prototype")
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.setLayout(QVBoxLayout(self.centralwidget))
        self.mdiArea = QMdiArea(self.centralwidget)
        self.mdiArea.tileSubWindows()
        self.centralwidget.layout().addWidget(self.mdiArea)
        self.setupMenus()
        self.treeView = QTreeWidget()
        self.DICOMfolderPath = ''
        self.ApplyStyleSheet()

    def setupMenus(self):  
        """Builds the menus in the menu bar of the MDI"""
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')

        viewDICOMStudiesButton = QAction('View DICOM Studies', self)
        viewDICOMStudiesButton.setShortcut('Ctrl+D')
        viewDICOMStudiesButton.setStatusTip('View DICOM Images')
        viewDICOMStudiesButton.triggered.connect(self.makeDICOMStudiesTreeView)
        fileMenu.addAction(viewDICOMStudiesButton)

        self.viewImageButton = QAction('View Image', self)
        self.viewImageButton.setShortcut('Ctrl+V')
        self.viewImageButton.setStatusTip('View DICOM Image')
        self.viewImageButton.triggered.connect(self.viewImageSubWindow)
        self.viewImageButton.setEnabled(False)
        toolsMenu.addAction(self.viewImageButton)

        self.invertImageButton = QAction('Invert Image', self)
        self.invertImageButton.setShortcut('Ctrl+I')
        self.invertImageButton.setStatusTip('Invert DICOM Image')
        self.invertImageButton.triggered.connect(self.invertImageSubWindow)
        self.invertImageButton.setEnabled(False)
        toolsMenu.addAction(self.invertImageButton)

    def ApplyStyleSheet(self):
        """Modifies the appearance of the GUI using CSS instructions"""
        try:
            self.setStyleSheet(styleSheet.TRISTAN_GREY)
        except Exception as e:
            print('Error in function ApplyStyleSheet: ' + str(e))
            

    def viewImageSubWindow(self):
        """Creates a subwindow that displays a DICOM image. Either executed using the 
        'View Image' Menu item in the Tools menu or by double clicking the Image name 
        in the DICOM studies tree view."""
        try:
            selectedImage = self.treeView.selectedItems()
            if selectedImage:
                subWindow = QMdiSubWindow(self)
                subWindow.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
                imageViewer = pg.GraphicsLayoutWidget()
                subWindow.setWidget(imageViewer)
                viewBox = imageViewer.addViewBox()
                viewBox.setAspectLocked(True)
                img = pg.ImageItem(border='w')
                viewBox.addItem(img)
            
                imagePath = self.DICOMfolderPath + "\\" + self.getDICOMFileName()
                if os.path.exists(imagePath):
                    dataset = pydicom.dcmread(imagePath)
                    if 'PixelData' in dataset:
                        img.setImage(dataset.pixel_array)

                subWindow.setObjectName("Image_Window")
                subWindow.setWindowTitle(self.getDICOMFileData())
                subWindow.setGeometry(0,0,800,600)
                self.mdiArea.addSubWindow(subWindow)
                subWindow.show()
        except Exception as e:
            print('Error in viewImageSubWindow: ' + str(e))

    def invertImageSubWindow(self):
        """Creates a subwindow that displays an inverted DICOM image. Executed using the 
        'Invert Image' Menu item in the Tools menu."""
        try:
            selectedImage = self.treeView.selectedItems()
            if selectedImage:
                subWindow = QMdiSubWindow(self)
                subWindow.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint |
                                        Qt.WindowMinimizeButtonHint)
                imageViewer = pg.GraphicsLayoutWidget()
                subWindow.setWidget(imageViewer)
                viewBox = imageViewer.addViewBox()
                viewBox.setAspectLocked(True)
                img = pg.ImageItem(border='w')
                viewBox.addItem(img)
            
                imagePath = self.DICOMfolderPath + "\\" + self.getDICOMFileName()
                if os.path.exists(imagePath):
                    dataset = pydicom.dcmread(imagePath)
                    if 'PixelData' in dataset:
                        invertedImage = np.invert(dataset.pixel_array)
                        img.setImage(invertedImage)
                        if invertedImage.dtype != np.uint16:
                            invertedImage = invertedImage.astype(np.uint16)
                        dataset.PixelData = invertedImage.tobytes()
                        dataset.save_as(imagePath + '_inv.dcm')
                        studyNumber, seriesNumber = self.getStudyAndSeriesNumbers(selectedImage)
                        #Record inverted image in XML file
                        #First determine if a series with parentID=seriesNumber exists
                        xPath = './study[id=' + chr(34) + studyNumber + chr(34) + \
                           ']/series[parentID=' + chr(34) + seriesNumber + chr(34) + ']'
                        series = self.root.find(xPath)
                        if series is None:
                            #Need to create a new series to hold this inverted image
                            #Get maximum series number in current study
                            studyXPath ='./study[@id=' + chr(34) + studyNumber + chr(34) + ']/series[last()]'
                            lastSeries = self.root.find(studyXPath)
                            lastSeriesID = lastSeries.attrib['id']
                            print('series id = {}'. format(lastSeriesID))
                        else:
                            #A series already exists to hold inverted images from
                            #the current parent series
                            print('add to existing series')


                subWindow.setObjectName("Image_Window")
                subWindow.setWindowTitle(self.getDICOMFileData() + ' Inverted')
                subWindow.setGeometry(0,0,800,600)
                self.mdiArea.addSubWindow(subWindow)
                subWindow.show()
                
                
        except Exception as e:
            print('Error in invertImageSubWindow: ' + str(e))


    def makeDICOMStudiesTreeView(self):
        """Uses an XML file that describes a DICOM file structure to build a
        tree view showing a visual representation of that file structure."""
        try:
            defaultPath = "C:\\DICOM Files\\00000001\\"
            fullFilePath, _ = QFileDialog.getOpenFileName(parent=self, 
                    caption="Select a DICOM file", 
                    directory=defaultPath,
                    filter="*.xml")

            if os.path.exists(fullFilePath):
                self.DICOMfolderPath, _ = os.path.split(fullFilePath)
                #print(self.DICOMfolderPath)
                self.XMLtree = ET.parse(fullFilePath)
                self.root = self.XMLtree.getroot()

                self.treeView.setColumnCount(4)
                self.treeView.setHeaderLabels(["DICOM Files", "Name", "Date", "Time"])

                # Uncomment to test XML file loaded OK
                #print(ET.tostring(self.root, encoding='utf8').decode('utf8'))
                studies = self.root.findall('./study')
                for study in studies:
                    studyID = study.attrib['id']
                    studyBranch = QTreeWidgetItem(self.treeView)
                    studyBranch.setText(0, "Study {}".format(studyID))
                    studyBranch.setFlags(studyBranch.flags() & ~Qt.ItemIsSelectable)
                    studyBranch.setExpanded(True)
                    for series in study:
                        seriesID = series.attrib['id']
                        seriesBranch = QTreeWidgetItem(studyBranch)
                        seriesBranch.setFlags(seriesBranch.flags() | Qt.ItemIsUserCheckable)
                        seriesBranch.setText(0, "Series {}".format(seriesID))
                        seriesBranch.setFlags(studyBranch.flags() & ~Qt.ItemIsSelectable)
                        seriesBranch.setExpanded(True)
                        for image in series:
                            imageName = image.find('name').text
                            imageDate = image.find('date').text
                            imageTime = image.find('time').text
                            imageLeaf = QTreeWidgetItem(seriesBranch)
                            imageLeaf.setText(0, 'Image ')
                            imageLeaf.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                            imageLeaf.setFlags(imageLeaf.flags() | Qt.ItemIsUserCheckable)
                            #Uncomment the next line to put a checkbox in front of each image
                            #imageLeaf.setCheckState(0, Qt.Unchecked)
                            imageLeaf.setText(1, imageName)
                            imageLeaf.setText(2, imageDate)
                            imageLeaf.setText(3, imageTime)
                            imageLeaf.setExpanded(True)

                self.treeView.resizeColumnToContents(0)
                self.treeView.resizeColumnToContents(1)
                self.treeView.resizeColumnToContents(2)
            
                self.treeView.itemSelectionChanged.connect(self.getDICOMFileData)
                self.treeView.itemDoubleClicked.connect(self.viewImageSubWindow)
                self.treeView.show()
        
                widget = QWidget()
                widget.setLayout(QVBoxLayout()) 
                self.lbl = QLabel()
                widget.layout().addWidget(self.treeView)
                widget.layout().addWidget(self.lbl)
        
                subWindow = QMdiSubWindow(self)
                subWindow.setWidget(widget)
                subWindow.setObjectName("New_Window")
                subWindow.setWindowTitle("DICOM Study Structure")
                subWindow.setGeometry(0,0,800,1300)
                self.mdiArea.addSubWindow(subWindow)
                subWindow.show()
        except Exception as e:
            print('Error in makeDICOMStudiesTreeView: ' + str(e))

    def getStudyAndSeriesNumbers(self, selectedImage):
        """This function assumes a series name takes the
        form 'series' space number, where number is an integer
        with one or more digits; 
        e.g., 'series 44' and returns the number as a string.
        
        Same assumption is made for the study name."""
         
        if selectedImage:
            #Extract series name from the selected image
            imageNode = selectedImage[0]
            seriesNode  = imageNode.parent()
            seriesName = seriesNode.text(0) 
            #Extract series number from the full series name
            numberList = re.findall(r'\d+', seriesName)
            seriesNumber = numberList[0]

            studyNode = seriesNode.parent()
            studyName = studyNode.text(0)
            #Extract study number from the full study name
            numberList = re.findall(r'\d+', studyName)
            studyNumber = numberList[0]
            return studyNumber, seriesNumber
        else:
            return None, None


    def getDICOMFileData(self):
        """When a DICOM images is selected in the tree view, this function
        returns its description in the form - study number: series number: image name"""
        try:
            selectedImage = self.treeView.selectedItems()
            if selectedImage:
                self.viewImageButton.setEnabled(True)
                self.invertImageButton.setEnabled(True)
                imageNode = selectedImage[0]
                seriesNode  = imageNode.parent()
                imageName = imageNode.text(1)
                series = seriesNode.text(0)
                studyNode = seriesNode.parent()
                study = studyNode.text(0)
                fullImageName = study + ': ' + series + ': Image - '  + imageName
                self.lbl.setText(fullImageName)
                return fullImageName
            else:
                self.viewImageButton.setEnabled(False)
                self.invertImageButton.setEnabled(False)
                return None
        except Exception as e:
            print('Error in getDICOMFileData: ' + str(e))

    def getDICOMFileName(self):
        """Returns the name of a DICOM image file"""
        try:
            selectedImage = self.treeView.selectedItems()
            if selectedImage:
                imageNode = selectedImage[0]
                imageName = imageNode.text(1)
                return imageName
        except Exception as e:
            print('Error in getDICOMFileName: ' + str(e))

def main():
    app = QApplication([])
    winMDI = MainWindow()
    winMDI.show()
    sys.exit(app.exec())

if __name__ == '__main__':
        main()