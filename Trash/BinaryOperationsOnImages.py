from PyQt5 import QtCore 
from PyQt5.QtCore import  Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog,                            
        QMdiArea, QMessageBox, QWidget, QGridLayout, QVBoxLayout, QSpinBox,
        QMdiSubWindow, QGroupBox, QMainWindow, QHBoxLayout, QDoubleSpinBox,
        QPushButton, QStatusBar, QLabel, QAbstractSlider, QHeaderView,
        QTreeWidgetItem, QGridLayout, QSlider, QCheckBox, QLayout, 
        QProgressBar, QComboBox, QTableWidget, QTableWidgetItem, QFrame)
from PyQt5.QtGui import QCursor, QIcon, QColor
import os
import numpy as np
import pydicom
from scipy.stats import iqr
import External.pyqtgraph as pg
import DICOM.SaveDICOM_Image as SaveDICOM_Image
import DICOM.ReadDICOM_Image as ReadDICOM_Image
import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.WEASEL.InterfaceDICOMXMLFile as interfaceDICOMXMLFile

import logging
logger = logging.getLogger(__name__)

listBinaryOperations =['Select binary Operation', 'Add', 'Divide', 
                         'Multiply', 'Subtract']


def getBinOperationFilePrefix(binaryOperation):
    if binaryOperation == 'Subtract':
        prefix = 'Sub'
    elif binaryOperation == 'Divide':
        prefix = 'Div'
    elif binaryOperation == 'Multiply':
        prefix = 'Multi'
    elif binaryOperation == 'Add':
        prefix = 'Add'
    return prefix


def returnPixelArray(imagePath1, imagePath2, binaryOperation):
    """returns the Image/Pixel array"""
    try:
        if os.path.exists(imagePath1):
            dataset1 = ReadDICOM_Image.getDicomDataset(imagePath1)
            pixelArray1 = ReadDICOM_Image.getPixelArray(dataset1)
        
        if os.path.exists(imagePath2):
            dataset2 = ReadDICOM_Image.getDicomDataset(imagePath2)
            pixelArray2 = ReadDICOM_Image.getPixelArray(dataset2)
            
        if binaryOperation == 'Add':
            pixelArray3 = np.add(pixelArray1, pixelArray2)
           
        elif binaryOperation == 'Divide':
            #If there is division by zero, then zero is returned
            pixelArray3 = np.divide(pixelArray1, pixelArray2,
            out=np.zeros_like(pixelArray1), where=pixelArray2!=0)
           
        elif binaryOperation == 'Multiply':
            pixelArray3 = np.multiply(pixelArray1, pixelArray2)
           
        elif binaryOperation == 'Subtract':
            pixelArray3 = np.subtract(pixelArray1, pixelArray2)
        
        if pixelArray3.any():
             return pixelArray3
        else:
             return np.zeros(np.array(pixelArray1).shape)
       
    except Exception as e:
        print('Error in function binaryOperationDICOM_Image.returnPixelArray: ' + str(e))


def isSeriesOnly(self):
    return True


def main(self):
    if self.isASeriesChecked:
        if len(self.checkedSeriesList)>0: 
            for series in self.checkedSeriesList:
                subjectID = series[0]
                studyID = series[1]
                seriesID = series[2]
                displayBinaryOperations(self, subjectID, studyID, seriesID)


def displayBinaryOperations(self, subjectID, studyID, seriesID):
        """Displays the sub window for performing binary operations
        on 2 images"""
        try:
            logger.info("BinaryOperationsOnImages.main called")
            self.subWindow = QMdiSubWindow(self)
            self.subWindow.setAttribute(Qt.WA_DeleteOnClose)
            self.subWindow.setWindowFlags(Qt.CustomizeWindowHint
                  | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
            layout = QGridLayout()
            widget = QWidget()
            widget.setLayout(layout)
            self.subWindow.setWidget(widget)
            pg.setConfigOptions(imageAxisOrder='row-major')

            imageViewer1 = pg.GraphicsLayoutWidget()
            viewBox1 = imageViewer1.addViewBox()
            viewBox1.setAspectLocked(True)
            self.img1 = pg.ImageItem(border='w')
            viewBox1.addItem(self.img1)
            self.imv1 = pg.ImageView(view=viewBox1, imageItem=self.img1)
            self.imv1.ui.histogram.hide()
            self.imv1.ui.roiBtn.hide()
            self.imv1.ui.menuBtn.hide()

            imageViewer2 = pg.GraphicsLayoutWidget()
            viewBox2 = imageViewer2.addViewBox()
            viewBox2.setAspectLocked(True)
            self.img2 = pg.ImageItem(border='w')
            viewBox2.addItem(self.img2)
            self.imv2 = pg.ImageView(view=viewBox2, imageItem=self.img2)
            self.imv2.ui.histogram.hide()
            self.imv2.ui.roiBtn.hide()
            self.imv2.ui.menuBtn.hide()

            imageViewer3 = pg.GraphicsLayoutWidget()
            viewBox3 = imageViewer3.addViewBox()
            viewBox3.setAspectLocked(True)
            self.img3 = pg.ImageItem(border='w')
            viewBox3.addItem(self.img3)
            self.imv3 = pg.ImageView(view=viewBox3, imageItem=self.img3)
            self.imv3.ui.histogram.hide()
            self.imv3.ui.roiBtn.hide()
            self.imv3.ui.menuBtn.hide()

            
            self.lblImageMissing1 = QLabel("<h4>Image Missing</h4>")
            self.lblImageMissing2 = QLabel("<h4>Image Missing</h4>")
            self.lblImageMissing1.hide()
            self.lblImageMissing2.hide()

            self.btnSave = QPushButton('Save')
            self.btnSave.setEnabled(False)
            self.btnSave.clicked.connect(lambda: saveNewDICOMFileFromBinOp(self))

            imagePathList = self.objXMLReader.getImagePathList(subjectID, studyID, 
                                                               seriesID) 
            #form a list of image file names without extensions
            imageNameList = [os.path.splitext(os.path.basename(image))[0] 
                             for image in imagePathList]
            self.image_Name_Path_Dict = dict(zip(
                imageNameList, imagePathList))
            self.imageList1 = QComboBox()
            self.imageList2 = QComboBox()
            self.imageList1.currentIndexChanged.connect(
                lambda: displayImageForBinOp(self, 1, self.image_Name_Path_Dict))
            self.imageList1.currentIndexChanged.connect(lambda: enableBinaryOperationsCombo(self))
            self.imageList1.currentIndexChanged.connect(
                lambda: doBinaryOperation(self, self.image_Name_Path_Dict))
            
            self.imageList2.currentIndexChanged.connect(
                lambda: displayImageForBinOp(self, 2, self.image_Name_Path_Dict))
            self.imageList2.currentIndexChanged.connect(lambda: enableBinaryOperationsCombo(self))
            self.imageList2.currentIndexChanged.connect(
                lambda: doBinaryOperation(self, self.image_Name_Path_Dict))

            self.binaryOpsList = QComboBox()
            self.binaryOpsList.currentIndexChanged.connect(
                lambda: doBinaryOperation(self, self.image_Name_Path_Dict))
            self.imageList1.addItems(imageNameList)
            self.imageList2.addItems(imageNameList)
            self.binaryOpsList.addItems(listBinaryOperations)

            layout.addWidget(self.btnSave, 0, 2)
            layout.addWidget(self.imageList1, 1, 0)
            layout.addWidget(self.imageList2, 1, 1)
            layout.addWidget(self.binaryOpsList, 1, 2)
            layout.addWidget(self.lblImageMissing1, 2, 0)
            layout.addWidget(self.lblImageMissing2, 2, 1)
            layout.addWidget(self.imv1, 3, 0)
            layout.addWidget(self.imv2, 3, 1)
            layout.addWidget(self.imv3, 3, 2)
                
            self.subWindow.setObjectName('Binary_Operation')
            windowTitle = 'Binary Operations'
            self.subWindow.setWindowTitle(windowTitle)
            height, width = self.getMDIAreaDimensions()
            self.subWindow.setGeometry(0,0,width*0.5,height*0.5)
            self.mdiArea.addSubWindow(self.subWindow)
            self.subWindow.show()

        except (IndexError, AttributeError):
                subWindow.close()
                msgBox = QMessageBox()
                msgBox.setWindowTitle("Binary operations on a DICOM series")
                msgBox.setText("Select a series")
                msgBox.exec()
        except Exception as e:
            print('Error in main: ' + str(e))
            logger.error('Error in main: ' + str(e))


def saveNewDICOMFileFromBinOp(self):
        """TO DO"""
        try:
            logger.info("BinaryOperationsOnImages.saveNewDICOMFileFromBinOp called")
            suffix = '_binOp'
            imageName1 = self.imageList1.currentText()
            imagePath1 = self.image_Name_Path_Dict[imageName1]
            imageName2 = self.imageList2.currentText()
            imagePath2 = self.image_Name_Path_Dict[imageName2]
            
            binaryOperation = self.binaryOpsList.currentText()
            prefix = getBinOperationFilePrefix(binaryOperation)
            
            newImageFileName = prefix + '_' + imageName1 \
                + '_' + imageName2 
            newImageFilePath = os.path.dirname(imagePath1) + '\\' + \
                newImageFileName + '.dcm'
            #print(newImageFilePath)
            #Save pixel array to a file
            SaveDICOM_Image.saveNewSingleDicomImage(newImageFilePath, imagePath1, self.binOpArray, "_"+binaryOperation+suffix, list_refs_path=[imagePath2])
            newSeriesID = interfaceDICOMXMLFile.insertNewImageInXMLFile(self, imagePath1,
                                                            newImageFilePath, suffix)
            #print(newSeriesID)
            treeView.refreshDICOMStudiesTreeView(self, newSeriesID)
        except Exception as e:
            print('Error in saveNewDICOMFileFromBinOp: ' + str(e))
            logger.error('Error in saveNewDICOMFileFromBinOp: ' + str(e))


def doBinaryOperation(self, imageDict):
        """TO DO"""
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
                self.btnSave.setEnabled(True)
                self.binOpArray = returnPixelArray(imagePath1, imagePath2, binOp)
                minimumValue = np.amin(self.binOpArray) if (np.median(self.binOpArray) - iqr(self.binOpArray, rng=(
                    1, 99))/2) < np.amin(self.binOpArray) else np.median(self.binOpArray) - iqr(self.binOpArray, rng=(1, 99))/2
                maximumValue = np.amax(self.binOpArray) if (np.median(self.binOpArray) + iqr(self.binOpArray, rng=(
                    1, 99))/2) > np.amax(self.binOpArray) else np.median(self.binOpArray) + iqr(self.binOpArray, rng=(1, 99))/2
                self.img3.setImage(self.binOpArray, autoHistogramRange=True, levels=(minimumValue, maximumValue)) 
            else:
                self.btnSave.setEnabled(False)
        except Exception as e:
            print('Error in doBinaryOperation: ' + str(e))
            logger.error('Error in doBinaryOperation: ' + str(e))


def enableBinaryOperationsCombo(self):
        """TO DO"""
        if self.lblImageMissing1.isHidden() and \
            self.lblImageMissing2.isHidden():
            self.binaryOpsList.setEnabled(True)
        else:
            self.binaryOpsList.setEnabled(False)
            self.btnSave.setEnabled(False)


def displayImageForBinOp(self, imageNumber, imageDict):
        """TO DO"""
        try:
            objImageMissingLabel = getattr(self, 'lblImageMissing' + str(imageNumber))
            objImage = getattr(self, 'img' + str(imageNumber))
            objComboBox = getattr(self, 'imageList' + str(imageNumber))

            #get name of selected image
            imageName = objComboBox.currentText()
            imagePath = imageDict[imageName]
            pixelArray = ReadDICOM_Image.returnPixelArray(imagePath)
            if pixelArray is None:
                objImageMissingLabel.show()
                objImage.setImage(np.array([[0,0,0],[0,0,0]])) 
            else:
                objImageMissingLabel.hide()
                minimumValue = np.amin(pixelArray) if (np.median(pixelArray) - iqr(pixelArray, rng=(
                    1, 99))/2) < np.amin(pixelArray) else np.median(pixelArray) - iqr(pixelArray, rng=(1, 99))/2
                maximumValue = np.amax(pixelArray) if (np.median(pixelArray) + iqr(pixelArray, rng=(
                    1, 99))/2) > np.amax(pixelArray) else np.median(pixelArray) + iqr(pixelArray, rng=(1, 99))/2
                objImage.setImage(pixelArray, autoHistogramRange=True, levels=(minimumValue, maximumValue))  
        except Exception as e:
            print('Error in displayImageForBinOp: ' + str(e))
            logger.error('Error in displayImageForBinOp: ' + str(e))
