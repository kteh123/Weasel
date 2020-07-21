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
import CoreModules.pyqtgraph as pg 
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image
import CoreModules.WEASEL.saveDICOM_Image as saveDICOM_Image
import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.WEASEL.DisplayImageCommon as displayImageCommon
import logging
logger = logging.getLogger(__name__)


def displayImageROISubWindow(self, derivedImagePath=None):
        """
        Creates a subwindow that displays one DICOM image and allows the creation of an ROI on it 
        """
        try:
            logger.info("DisplayImageROI displayImageROISubWindow called")
            pixelArray = readDICOM_Image.returnPixelArray(self.selectedImagePath)
            colourTable, lut = readDICOM_Image.getColourmap(self.selectedImagePath)

            imageViewer, layout, lblImageMissing, subWindow = \
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

            img, imv, viewBox = displayImageCommon.setUpViewBoxForImage(imageViewer, layout)
            
            lblPixelValue, lblROIMeanValue = setUpLabels(layout)
           
            setUpROITools(viewBox, layout, img, lblROIMeanValue)
           
            displayROIPixelArray(self, pixelArray, 0,
                          lblImageMissing, lblPixelValue,
                           colourTable,
                          imv)

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
            imageViewer, layout, lblImageMissing, subWindow = \
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

            img, imv, viewBox = displayImageCommon.setUpViewBoxForImage(imageViewer, layout) 
            lblPixelValue, lblROIMeanValue = setUpLabels(layout)
            
            setUpROITools(viewBox, layout, img, lblROIMeanValue)

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
                                                   lblImageMissing, 
                                                   lblPixelValue, 
                                                   imv, subWindow))
            imageSlider.valueChanged.connect(
                  lambda: updateROIMeanValue(getROIOject(viewBox), 
                                               img.image, 
                                               img, 
                                               lblROIMeanValue))
            #print('Num of images = {}'.format(len(imageList)))
            #Display the first image in the viewer
            imageROISliderMoved(self, seriesName, 
                                    imageList, 
                                    imageSlider.value(),
                                    lblImageMissing, 
                                    lblPixelValue, 
                                    imv, subWindow)
            
        except Exception as e:
            print('Error in displayMultiImageROISubWindow: ' + str(e))
            logger.error('Error in displayMultiImageROISubWindow: ' + str(e))



def imageROISliderMoved(self, seriesName, imageList, imageNumber,
                        lblImageMissing, lblPixelValue, 
                        imv, subWindow):
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
                colourTable, lut = readDICOM_Image.getColourmap(self.selectedImagePath)

                displayROIPixelArray(self, pixelArray, currentImageNumber,
                          lblImageMissing, lblPixelValue, colourTable,
                          imv)
                
                subWindow.setWindowTitle(seriesName + ' - ' 
                         + os.path.basename(self.selectedImagePath))
               # print("imageSliderMoved after={}".format(self.selectedImagePath))
        except Exception as e:
            print('Error in DisplayImageROI.imageROISliderMoved: ' + str(e))
            logger.error('Error in DisplayImageROI.imageROISliderMoved: ' + str(e))




def setUpLabels(layout):
        logger.info("DisplayImageROI.setUpLabels called")
        gridLayout = QGridLayout()
        layout.addLayout(gridLayout)
       
        lblROIMeanValue = QLabel("<h4>ROI Mean Value:</h4>")
        lblROIMeanValue.show()
        gridLayout.addWidget(lblROIMeanValue, 0, 0)
        
        lblPixelValue = QLabel("<h4>Pixel Value:</h4>")
        lblPixelValue.show()
        gridLayout.addWidget(lblPixelValue, 0, 1)
        return lblPixelValue, lblROIMeanValue


def setUpROITools(viewBox, layout, img, lblROIMeanValue):
        try:
            groupBoxROI = QGroupBox('ROI')
            gridLayoutROI = QGridLayout()
            groupBoxROI.setLayout(gridLayoutROI)
            layout.addWidget(groupBoxROI)

            btnCircleROI = QPushButton('Circle') 
            btnCircleROI.setToolTip('Creates/Resets a circular ROI')
            btnCircleROI.clicked.connect(lambda: 
                   createCircleROI(viewBox, img, lblROIMeanValue))
        
            btnEllipseROI = QPushButton('Ellipse') 
            btnEllipseROI.setToolTip('Creates/Resets an ellipical ROI')
            btnEllipseROI.clicked.connect(lambda: 
                   createEllipseROI(viewBox, img, lblROIMeanValue))

            btnMultiRectROI = QPushButton('Multi-Rect') 
            btnMultiRectROI.setToolTip(
                'Creates/Resets a chain of rectangular ROIs connected by handles')
            btnMultiRectROI.clicked.connect(lambda: 
                   createMultiRectROI(viewBox, img, lblROIMeanValue))

            btnPolyLineROI = QPushButton('PolyLine')
            btnPolyLineROI.setToolTip(
                'Allows the user to draw paths of multiple line segments')
            btnPolyLineROI.clicked.connect(lambda: 
                   createPolyLineROI(viewBox, img, lblROIMeanValue))

            btnRectROI = QPushButton('Rectangle') 
            btnRectROI.setToolTip('Creates/Resets a rectangular ROI')
            btnRectROI.clicked.connect(lambda: 
                   createRectangleROI(viewBox, img, lblROIMeanValue))

            #btnDrawROI = QPushButton('Draw') 
            #btnDrawROI.setToolTip('Allows the user to draw around a ROI')

            btnRemoveROI = QPushButton('Clear')
            btnRemoveROI.setToolTip('Clears the ROI from the image')
            btnRemoveROI.clicked.connect(lambda: removeROI(viewBox, 
                                                       lblROIMeanValue))

            btnSaveROI = QPushButton('Save')
            btnSaveROI.setToolTip('Saves the ROI in DICOM format')
            #btnSaveROI.clicked.connect(lambda: self.resetROI(viewBox))

            gridLayoutROI.addWidget(btnCircleROI,0,0)
            gridLayoutROI.addWidget(btnEllipseROI,0,1)
            gridLayoutROI.addWidget(btnMultiRectROI,0,2)
            gridLayoutROI.addWidget(btnPolyLineROI,0,3)
            gridLayoutROI.addWidget(btnRectROI,1,0)
            #gridLayoutROI.addWidget(btnDrawROI,1,1)
            gridLayoutROI.addWidget(btnRemoveROI,1,1)
            gridLayoutROI.addWidget(btnSaveROI,1,2)
        except Exception as e:
            print('Error in setUpROITools: ' + str(e))
            logger.error('Error in setUpROITools: ' + str(e))


def addROIToViewBox(objROI, viewBox, img, lblROIMeanValue):
        try:
            logger.info("DisplayImageROI.addROIToViewBox called")
            viewBox.addItem(objROI)
            objROI.sigRegionChanged.connect(
                lambda: updateROIMeanValue(objROI, 
                                               img.image, 
                                               img, 
                                               lblROIMeanValue))
        except Exception as e:
            print('Error in addROIToViewBox: ' + str(e))
            logger.error('Error in addROIToViewBox: ' + str(e))


def createMultiRectROI(viewBox, img, lblROIMeanValue):
        try:
            logger.info("DisplayImageROI.createMultiRectROI called")
            #Remove existing ROI if there is one
            removeROI(viewBox, lblROIMeanValue)
            objROI = pg.MultiRectROI([[20, 90], [50, 60], [60, 90]],
                                 pen=pg.mkPen(pg.mkColor('r'),
                                           width=5,
                                          style=QtCore.Qt.SolidLine), 
                                 width=5,
                               removable=True)
            addROIToViewBox(objROI, viewBox, img, lblROIMeanValue)
        except Exception as e:
            print('Error in createMultiRectROI: ' + str(e))
            logger.error('Error in createMultiRectROI: ' + str(e))


def createPolyLineROI(viewBox, img, lblROIMeanValue):
        try:
            logger.info("DisplayImageROI.createPolyLineROI called")
            #Remove existing ROI if there is one
            removeROI(viewBox, lblROIMeanValue)
            objROI = pg.PolyLineROI([[80, 60], [90, 30], [60, 40]],
                                 pen=pg.mkPen(pg.mkColor('r'),
                                           width=5,
                                          style=QtCore.Qt.SolidLine), 
                                 closed=True,
                                 removable=True)
            addROIToViewBox(objROI, viewBox, img, lblROIMeanValue)
        except Exception as e:
            print('Error in createPolyLineROI: ' + str(e))
            logger.error('Error in createPolyLineROI: ' + str(e))


def createRectangleROI(viewBox, img, lblROIMeanValue):
        try:
            logger.info("DisplayImageROI.createRectangleROI called")
            #Remove existing ROI if there is one
            removeROI(viewBox, lblROIMeanValue)
            objROI = pg.RectROI(
                                [20, 20], 
                                [20, 20],
                                 pen=pg.mkPen(pg.mkColor('r'),
                                           width=4,
                                          style=QtCore.Qt.SolidLine), 
                               removable=True)
            addROIToViewBox(objROI, viewBox, img, lblROIMeanValue)
        except Exception as e:
            print('Error in createRectangleRO: ' + str(e))
            logger.error('Error in createRectangleRO: ' + str(e))


def createCircleROI(viewBox, img, lblROIMeanValue):
        try:
            logger.info("DisplayImageROI.createCircleROI called")
            #Remove existing ROI if there is one
            removeROI(viewBox, lblROIMeanValue)
            objROI = pg.CircleROI([20, 20], 
                                  [20, 20],  
                                  pen=pg.mkPen(pg.mkColor('r'),
                                           width=4,
                                          style=QtCore.Qt.SolidLine),
                                  removable=True)
            addROIToViewBox(objROI, viewBox, img, lblROIMeanValue)
        except Exception as e:
            print('Error in createCircleROI: ' + str(e))
            logger.error('Error in createCircleROI: ' + str(e))


def createEllipseROI(viewBox, img, lblROIMeanValue):
        try:
            logger.info("DisplayImageROI.createEllipseROI called")
            #Remove existing ROI if there is one
            removeROI(viewBox, lblROIMeanValue)
            objROI = pg.EllipseROI(
                                [20, 20], 
                                [30, 20], 
                                pen=pg.mkPen(pg.mkColor('r'),
                                           width=4,
                                          style=QtCore.Qt.SolidLine),
                                removable=True)
            addROIToViewBox(objROI, viewBox, img, lblROIMeanValue)
        except Exception as e:
            print('Error in createEllipseROI: ' + str(e))
            logger.error('Error in createEllipseROI: ' + str(e))


def getROIOject(viewBox):
        try:
            logger.info("DisplayImageROI.getROIOject called")
            for item in viewBox.items:
                if 'graphicsItems.ROI' in str(type(item)):
                    return item
                    break
        except Exception as e:
            print('Error in getROIOject: ' + str(e))
            logger.error('Error in getROIOject: ' + str(e))
        
        
def removeROI(viewBox, lblROIMeanValue):
        try:
            logger.info("DisplayImageROI.removeROI called")
            objROI = getROIOject(viewBox)
            viewBox.removeItem(objROI) 
            lblROIMeanValue.setText("<h4>ROI Mean Value:</h4>")
        except Exception as e:
            print('Error in DisplayImageROI.removeROI: ' + str(e))
            logger.error('Error in DisplayImageROI.removeROI: ' + str(e))           


def displayROIPixelArray(self, pixelArray, currentImageNumber,
                          lblImageMissing, lblPixelValue, colourTable,
                          imv):
        try:
            logger.info("DisplayImageROI.displayROIPixelArray called")

            #Check that pixel array holds an image & display it
            if pixelArray is None:
                lblImageMissing.show()
                imv.setImage(np.array([[0,0,0],[0,0,0]]))  
            else:
                try:
                    dataset = readDICOM_Image.getDicomDataset(self.selectedImagePath)
                    slope = float(getattr(dataset, 'RescaleSlope', 1))
                    intercept = float(getattr(dataset, 'RescaleIntercept', 0))
                    centre = dataset.WindowCenter * slope + intercept
                    width = dataset.WindowWidth * slope
                    maximumValue = centre + width/2
                    minimumValue = centre - width/2
                except:
                    minimumValue = np.amin(pixelArray) if (np.median(pixelArray) - iqr(pixelArray, rng=(
                    1, 99))/2) < np.amin(pixelArray) else np.median(pixelArray) - iqr(pixelArray, rng=(1, 99))/2
                    maximumValue = np.amax(pixelArray) if (np.median(pixelArray) + iqr(pixelArray, rng=(
                    1, 99))/2) > np.amax(pixelArray) else np.median(pixelArray) + iqr(pixelArray, rng=(1, 99))/2

                
                imv.setImage(pixelArray, autoHistogramRange=True, levels=(minimumValue, maximumValue))
                displayImageCommon.setPgColourMap(colourTable, imv)
                lblImageMissing.hide()   
  
                imv.getView().scene().sigMouseMoved.connect(
                   lambda pos: displayImageCommon.getPixelValue(pos, imv, pixelArray, lblPixelValue))

        except Exception as e:
            print('Error in DisplayImageROI.displayROIPixelArray: ' + str(e))
            logger.error('Error in DisplayImageROI.displayROIPixelArray: ' + str(e))


def updateROIMeanValue(roi, pixelArray, imgItem, lbl):
        try:
            logger.info("DisplayImageROI.updateROIMeanValue called")
            #As image's axis order is set to
            #'row-major', then the axes are specified 
            #in (y, x) order, axes=(1,0)
            if roi is not None:
                arrRegion = roi.getArrayRegion(pixelArray, imgItem, 
                                axes=(1,0))
                #, returnMappedCoords=True
                #print('Mouse move')
                #print(arrRegion)
                #roiMean = round(np.mean(arrRegion[0]), 3)
                roiMean = round(np.mean(arrRegion), 3)
                lbl.setText("<h4>ROI Mean Value = {}</h4>".format(str(roiMean)))
                if len(arrRegion[0]) <4:
                    print(arrRegion[0])
                    print ('Coords={}'.format(arrRegion[1]))

        except Exception as e:
            print('Error in DisplayImageROI.updateROIMeanValue: ' + str(e))
            logger.error('Error in DisplayImageROI.updateROIMeanValue: ' + str(e)) 
