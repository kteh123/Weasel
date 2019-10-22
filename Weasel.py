
from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow, QLabel,
        QMdiArea, QMessageBox, QWidget, QVBoxLayout, QMdiSubWindow, QPushButton, 
        QTreeWidget, QTreeWidgetItem, QGridLayout)

import xml.etree.ElementTree as ET 
import pydicom
import pyqtgraph as pg
import os
import sys
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
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

    def setupMenus(self):    
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

    def viewImageSubWindow(self):
        try:
            getSelected = self.treeView.selectedItems()
            if getSelected:
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
        try:
            getSelected = self.treeView.selectedItems()
            if getSelected:
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
                        img.setImage(np.invert(dataset.pixel_array))

                subWindow.setObjectName("Image_Window")
                subWindow.setWindowTitle(self.getDICOMFileData() + ' Inverted')
                subWindow.setGeometry(0,0,800,600)
                self.mdiArea.addSubWindow(subWindow)
                subWindow.show()
        except Exception as e:
            print('Error in invertImageSubWindow: ' + str(e))


    def makeDICOMStudiesTreeView(self):
        try:
            defaultPath = "C:\\DICOM Files\\00000001\\"
            fullFilePath, _ = QFileDialog.getOpenFileName(parent=self, 
                    caption="Select a DICOM file", 
                    directory=defaultPath,
                    filter="*.xml")

            if os.path.exists(fullFilePath):
                self.DICOMfolderPath, _ = os.path.split(fullFilePath)
                print(self.DICOMfolderPath)
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


    def getDICOMFileData(self):
        try:
            getSelected = self.treeView.selectedItems()
            if getSelected:
                self.viewImageButton.setEnabled(True)
                self.invertImageButton.setEnabled(True)
                imageNode = getSelected[0]
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
        try:
            getSelected = self.treeView.selectedItems()
            if getSelected:
                imageNode = getSelected[0]
                imageName = imageNode.text(1)
                return imageName
        except Exception as e:
            print('Error in getDICOMFileName: ' + str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())