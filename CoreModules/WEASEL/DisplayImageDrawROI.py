from PyQt5 import QtCore 
from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QFileDialog,                            
                            QMessageBox, 
                            QWidget, 
                            QGridLayout, 
                            QVBoxLayout, 
                            QMdiSubWindow, 
                            QGroupBox, 
                            QDoubleSpinBox,
                            QPushButton,  
                            QLabel,  
                            QSlider, 
                            QCheckBox,  
                            QComboBox)

import os
import scipy
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import CoreModules.WEASEL.styleSheet as styleSheet
import CoreModules.pyqtgraph as pg 
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image
import CoreModules.WEASEL.saveDICOM_Image as saveDICOM_Image
import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.WEASEL.DisplayImageCommon as displayImageCommon
from CoreModules.freeHandROI.GraphicsView import GraphicsView
import logging
logger = logging.getLogger(__name__)


def setLevelsSpinBoxes(layout, graphicsView):
    spinBoxIntensity = QDoubleSpinBox()
    spinBoxContrast = QDoubleSpinBox()
    
    lblIntensity = QLabel("Centre (Intensity)")
    lblContrast = QLabel("Width (Contrast)")
    lblIntensity.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    lblContrast.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    
    spinBoxIntensity.setMinimum(-100000.00)
    spinBoxContrast.setMinimum(-100000.00)
    spinBoxIntensity.setMaximum(1000000000.00)
    spinBoxContrast.setMaximum(1000000000.00)
    spinBoxIntensity.setWrapping(True)
    spinBoxContrast.setWrapping(True)
    gridLayoutLevels = QGridLayout()
    gridLayoutLevels.addWidget(lblIntensity, 0,0)
    gridLayoutLevels.addWidget(spinBoxIntensity, 0, 1)
    gridLayoutLevels.addWidget(lblContrast, 0,2)
    gridLayoutLevels.addWidget(spinBoxContrast, 0,3)
    
    spinBoxIntensity.valueChanged.connect(lambda:
            graphicsView.graphicsItem.updateImageLevels(
                spinBoxIntensity.value(), spinBoxContrast.value()))
    spinBoxContrast.valueChanged.connect(lambda: 
            graphicsView.graphicsItem.updateImageLevels(
                spinBoxIntensity.value(), spinBoxContrast.value()))
    
    layout.addLayout(gridLayoutLevels) 
    return spinBoxIntensity, spinBoxContrast
    

def setUpPixelDataLabels(layout):
    pixelDataLabel = QLabel("Pixel data")
    roiMeanLabel = QLabel("ROI Mean Value")
    layout.addWidget(pixelDataLabel)
    layout.addWidget(roiMeanLabel)
    return pixelDataLabel, roiMeanLabel


def displayImageROISubWindow(self, derivedImagePath=None):
        """
        Creates a subwindow that displays one DICOM image and allows the creation of an ROI on it 
        """
        try:
            logger.info("DisplayImageROI displayImageROISubWindow called")
            pixelArray = readDICOM_Image.returnPixelArray(self.selectedImagePath)
        
            layout, lblImageMissing, subWindow = \
                displayImageCommon.setUpImageViewerSubWindow(self)
            windowTitle = displayImageCommon.getDICOMFileData(self)
            subWindow.setWindowTitle(windowTitle)

            if derivedImagePath:
                lblHiddenImagePath = QLabel(derivedImagePath)
            else:
                lblHiddenImagePath = QLabel(self.selectedImagePath)
            lblHiddenImagePath.hide()
            lblHiddenStudyID = QLabel()
            lblHiddenStudyID.hide()
            lblHiddenSeriesID = QLabel()
            lblHiddenSeriesID.hide()
            
            layout.addWidget(lblHiddenSeriesID)
            layout.addWidget(lblHiddenStudyID)
            layout.addWidget(lblHiddenImagePath)

            graphicsView = GraphicsView()
            if pixelArray is None:
                lblImageMissing.show()
                graphicsView.setImage(np.array([[0,0,0],[0,0,0]]))  
            else:
                graphicsView.setImage(pixelArray)
            layout.addWidget(graphicsView)

            pixelDataLabel, roiMeanLabel = setUpPixelDataLabels(layout)

            graphicsView.graphicsItem.sigMouseHovered.connect(
            lambda: displayImageDataUnderMouse(graphicsView, pixelDataLabel))
            graphicsView.graphicsItem.sigMaskCreated.connect(lambda: print("Mask created"))

            spinBoxIntensity, spinBoxContrast = setLevelsSpinBoxes(layout, graphicsView)
            spinBoxIntensity.setValue(graphicsView.graphicsItem.intensity)
            spinBoxContrast.setValue(graphicsView.graphicsItem.contrast)
            setUpROITools(layout, graphicsView)

        except (IndexError, AttributeError):
                subWindow.close()
                msgBox = QMessageBox()
                msgBox.setWindowTitle("View a DICOM series or image with an ROI")
                msgBox.setText("Select either a series or an image")
                msgBox.exec()
        except Exception as e:
            print('Error in DisplayImageROI.displayImageROISubWindow: ' + str(e))
            logger.error('Error in DisplayImageROI.displayImageROISubWindow: ' + str(e)) 


def displayMultiImageROISubWindow(self, imageList, studyName, 
                     seriesName, sliderPosition = -1):
        """
        Creates a subwindow that displays all the DICOM images in a series. 
        A slider allows the user to navigate  through the images.  
        The user may create an ROI on the series of images.
        """
        try:
            logger.info("DisplayImageROI.displayMultiImageROISubWindow called")
            layout, lblImageMissing, subWindow = \
                displayImageCommon.setUpImageViewerSubWindow(self)

            #Study ID & Series ID are stored locally on the
            #sub window in case the user wishes to delete an
            #image in the series.  They may have several series
            #open at once, so the selected series on the treeview
            #may not the same as that from which the image is
            #being deleted.

            lblHiddenImagePath = QLabel('')
            lblHiddenImagePath.hide()
            lblHiddenStudyID = QLabel(studyName)
            lblHiddenStudyID.hide()
            lblHiddenSeriesID = QLabel(seriesName)
            lblHiddenSeriesID.hide()
           
            layout.addWidget(lblHiddenImagePath)
            layout.addWidget(lblHiddenSeriesID)
            layout.addWidget(lblHiddenStudyID)
           
            imageSlider = QSlider(Qt.Horizontal)

            graphicsView = GraphicsView()
            layout.addWidget(graphicsView)
            pixelDataLabel, roiMeanLabel = setUpPixelDataLabels(layout)
            spinBoxIntensity, spinBoxContrast = setLevelsSpinBoxes(layout, graphicsView)
            setUpROITools(layout, graphicsView)

            imageSlider.setMinimum(1)
            imageSlider.setMaximum(len(imageList))
            if sliderPosition == -1:
                imageSlider.setValue(1)
            else:
                imageSlider.setValue(sliderPosition)
            imageSlider.setSingleStep(1)
            imageSlider.setTickPosition(QSlider.TicksBothSides)
            imageSlider.setTickInterval(1)
            layout.addWidget(imageSlider)
            imageSlider.valueChanged.connect(
                  lambda: imageROISliderMoved(self, seriesName, 
                                                   imageList, 
                                                   imageSlider.value(),
                                                   lblImageMissing, pixelDataLabel,
                                                   spinBoxIntensity, 
                                                   spinBoxContrast,
                                                   graphicsView, subWindow))
           
            imageROISliderMoved(self, seriesName, 
                                    imageList, 
                                    imageSlider.value(),
                                    lblImageMissing, pixelDataLabel,
                                    spinBoxIntensity, 
                                    spinBoxContrast,
                                    graphicsView, subWindow)
            
        except (IndexError, AttributeError):
                subWindow.close()
                msgBox = QMessageBox()
                msgBox.setWindowTitle("View a DICOM series or image with an ROI")
                msgBox.setText("Select either a series or an image")
                msgBox.exec()    
        except Exception as e:
            print('Error in displayMultiImageROISubWindow: ' + str(e))
            logger.error('Error in displayMultiImageROISubWindow: ' + str(e))


def displayImageDataUnderMouse(graphicsView, pixelDataLabel):
        xCoord = graphicsView.graphicsItem.xMouseCoord
        yCoord = graphicsView.graphicsItem.yMouseCoord
        pixelColour = graphicsView.graphicsItem.pixelColour
        pixelValue = graphicsView.graphicsItem.pixelValue
        str ="pixel value {}, pixel colour {} @ X = {}, Y = {}".format(pixelValue, pixelColour,
                                                                      xCoord, yCoord, )
        pixelDataLabel.setText(str)


def imageROISliderMoved(self, seriesName, imageList, imageNumber,
                        lblImageMissing, pixelDataLabel,
                        spinBoxIntensity, spinBoxContrast,  
                        graphicsView, subWindow):
        """On the Multiple Image with ROI Display sub window, this
        function is called when the image slider is moved. 
        It causes the next image in imageList to be displayed"""
        try:
            logger.info("DisplayImageROI.imageROISliderMoved called")
            #imageNumber = self.imageSlider.value()
            currentImageNumber = imageNumber - 1
            if currentImageNumber >= 0:
                self.selectedImagePath = imageList[currentImageNumber]
                #print("imageSliderMoved before={}".format(self.selectedImagePath))
                pixelArray = readDICOM_Image.returnPixelArray(self.selectedImagePath)

                if pixelArray is None:
                    lblImageMissing.show()
                    imv.setImage(np.array([[0,0,0],[0,0,0]]))  
                else:
                    graphicsView.setImage(pixelArray)
                    spinBoxIntensity.setValue(graphicsView.graphicsItem.intensity)
                    spinBoxContrast.setValue(graphicsView.graphicsItem.contrast)
                    graphicsView.graphicsItem.sigMouseHovered.connect(
                    lambda: displayImageDataUnderMouse(graphicsView, pixelDataLabel))
                    graphicsView.graphicsItem.sigMaskCreated.connect(lambda: print("Mask created"))

                subWindow.setWindowTitle(seriesName + ' - ' 
                         + os.path.basename(self.selectedImagePath))
               # print("imageSliderMoved after={}".format(self.selectedImagePath))
        except Exception as e:
            print('Error in DisplayImageROI.imageROISliderMoved: ' + str(e))
            logger.error('Error in DisplayImageROI.imageROISliderMoved: ' + str(e))


def setUpROITools(layout, graphicsView):
        try:
            groupBoxROI = QGroupBox('ROI')
            gridLayoutROI = QGridLayout()
            groupBoxROI.setLayout(gridLayoutROI)
            layout.addWidget(groupBoxROI)

            btnDrawROI = QPushButton('Draw') 
            btnDrawROI.setToolTip('Allows the user to draw around a ROI')
            btnDrawROI.setCheckable(True)
            btnDrawROI.clicked.connect(lambda checked: drawROI( checked, 
                                                               graphicsView, 
                                                               btnDrawROI))

            btnRemoveROI = QPushButton('Clear')
            btnRemoveROI.setToolTip('Clears the ROI from the image')
            #btnRemoveROI.clicked.connect(lambda: removeROI(viewBox, 
             #                                          lblROIMeanValue))

            btnSaveROI = QPushButton('Save')
            btnSaveROI.setToolTip('Saves the ROI in DICOM format')
            #btnSaveROI.clicked.connect(lambda: self.resetROI(viewBox))

            gridLayoutROI.addWidget(btnDrawROI,0,0)
            gridLayoutROI.addWidget(btnRemoveROI,0,1)
            gridLayoutROI.addWidget(btnSaveROI,0,2)
        except Exception as e:
            print('Error in setUpROITools: ' + str(e))
            logger.error('Error in setUpROITools: ' + str(e))


def drawROI(checked, graphicsView, btnDrawROI):
        if checked:
           graphicsView.graphicsItem.drawRoi = True
           btnDrawROI.setStyleSheet("background-color: rgb(0,0,255); color: rgb(255,0,0);")
        else:
           graphicsView.graphicsItem.drawRoi = False
           btnDrawROI.setStyleSheet(styleSheet.TRISTAN_GREY)


