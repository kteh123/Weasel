"""This module contains helper functions used by functions in modules 
DisplayImageColour.py & DisplayImageROI.py"""
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

from matplotlib import cm
import CoreModules.pyqtgraph as pg 
import numpy as np
import math
import logging
logger = logging.getLogger(__name__)

def setPgColourMap(cm_name, imv, cmbColours=None, lut=None):
    """This function converts a matplotlib colour map into
    a colour map that can be used by pyqtGraph imageView widget. 
    Input Parmeters
    ***************
        cm_name - name of the colour map
        imv - name of the imageView widget
        cmbColours - name of the dropdown lists of colour map names
        lut - name of the look up table containing raw colour data
    """

    try:
        if cm_name == None:
            cm_name = 'gray'

        if cmbColours:
            displayColourTableInComboBox(cmbColours, cm_name)   
        
        if cm_name == 'custom':
            colors = lut
        else:
            cmMap = cm.get_cmap(cm_name)
            colourClassName = cmMap.__class__.__name__
            if colourClassName == 'ListedColormap':
                colors = cmMap.colors
            elif colourClassName == 'LinearSegmentedColormap':
                numberOfValues = np.sqrt(len(imv.image.flatten()))
                colors = cmMap(np.linspace(0, 1, numberOfValues))

        positions = np.linspace(0, 1, len(colors))
        pgMap = pg.ColorMap(positions, colors)
        imv.setColorMap(pgMap)        
    except Exception as e:
        print('Error in DisplayImageCommon.setPgColourMap: ' + str(e))
        logger.error('Error in DisplayImageCommon.setPgColourMap: ' + str(e))


def displayColourTableInComboBox(cmbColours, colourTable):
    """
    cmbColours - name of the dropdown lists of colour map names
    colourTable - String variable containing the name of a colour table
    """
    try:
        cmbColours.blockSignals(True)
        index = cmbColours.findText(colourTable)
        if index >= 0:
            cmbColours.setCurrentIndex(index)
        cmbColours.blockSignals(False)
    except Exception as e:
            print('Error in DisplayImageCommon.displayColourTableInComboBox: ' + str(e))
            logger.error('Error in DisplayImageCommon.displayColourTableInComboBox: ' + str(e))


def setUpViewBoxForImage(imageViewer, layout, spinBoxCentre = None, spinBoxWidth = None):
    try:
        logger.info("DisplayImageCommon.setUpViewBoxForImage called")
        plotItem = imageViewer.addPlot() 
        plotItem.getViewBox().setAspectLocked() 
        img = pg.ImageItem(border='w')
            
        imv= pg.ImageView(view=plotItem, imageItem=img)
        if spinBoxCentre and spinBoxWidth:
            histogramObject = imv.getHistogramWidget().getHistogram()
            histogramObject.sigLevelsChanged.connect(lambda: getHistogramLevels(imv, spinBoxCentre, spinBoxWidth))
        imv.ui.roiBtn.hide()
        imv.ui.menuBtn.hide()
        layout.addWidget(imv)
 
        return img, imv, plotItem
    except Exception as e:
        print('Error in DisplayImageCommon.setUpViewBoxForImag: ' + str(e))
        logger.error('Error in DisplayImageCommon.setUpViewBoxForImag: ' + str(e))


def getHistogramLevels(imv, spinBoxCentre, spinBoxWidth):
        minLevel, maxLevel = imv.getLevels()
        width = maxLevel - minLevel
        centre = minLevel + (width/2)
        spinBoxCentre.setValue(centre)
        spinBoxWidth.setValue(width)


def setUpImageViewerSubWindow(self):
    try:
        logger.info("DisplayImageCommon.setUpImageViewerSubWindow called")
        pg.setConfigOptions(imageAxisOrder='row-major')
        subWindow = QMdiSubWindow(self)
        subWindow.setObjectName = 'image_viewer'
        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.setWindowFlags(Qt.CustomizeWindowHint | 
                                      Qt.WindowCloseButtonHint | 
                                      Qt.WindowMinimizeButtonHint)
        
        
        height, width = self.getMDIAreaDimensions()
        subWindow.setGeometry(0,0,width*0.6,height)
        self.mdiArea.addSubWindow(subWindow)
        
        layout = QVBoxLayout()
        imageViewer = pg.GraphicsLayoutWidget()
        widget = QWidget()
        widget.setLayout(layout)
        subWindow.setWidget(widget)
        
        lblImageMissing = QLabel("<h4>Image Missing</h4>")
        lblImageMissing.hide()
        layout.addWidget(lblImageMissing)
        subWindow.show()
        return imageViewer, layout, lblImageMissing, subWindow
    except Exception as e:
            print('Error in DisplayImageCommon.setUpImageViewerSubWindow: ' + str(e))
            logger.error('Error in DisplayImageCommon.displayMultiImageSubWindow: ' + str(e))


def getPixelValue(pos, imv, pixelArray, lblPixelValue):
    """

    lblPixelValue - Label widget that displays the value of the pixel under the mouse pointer
                and the X,Y coordinates of the mouse pointer.
    """
    try:
        #print ("Image position: {}".format(pos))
        container = imv.getView()
        if container.sceneBoundingRect().contains(pos): 
            mousePoint = container.getViewBox().mapSceneToView(pos) 
            x_i = math.floor(mousePoint.x())
            y_i = math.floor(mousePoint.y()) 
            z_i = imv.currentIndex + 1
            if (len(np.shape(pixelArray)) == 2) and y_i > 0 and y_i < pixelArray.shape [ 0 ] \
                and x_i > 0 and x_i < pixelArray.shape [ 1 ]: 
                lblPixelValue.setText(
                    "<h4>Pixel Value = {} @ X: {}, Y: {}</h4>"
                .format (round(pixelArray[ x_i, y_i ], 3), x_i, y_i))
            elif (len(np.shape(pixelArray)) == 3) and z_i > 0 and z_i < pixelArray.shape [ 0 ] \
                and y_i > 0 and y_i < pixelArray.shape [ 1 ] \
                and x_i > 0 and x_i < pixelArray.shape [ 2 ]: 
                lblPixelValue.setText(
                    "<h4>Pixel Value = {} @ X: {}, Y: {}, Z: {}</h4>"
                .format (round(pixelArray[ z_i, y_i, x_i ], 3), x_i, y_i, z_i))
            else:
                lblPixelValue.setText("<h4>Pixel Value:</h4>")
        else:
            lblPixelValue.setText("<h4>Pixel Value:</h4>")
                   
    except Exception as e:
        print('Error in DisplayImageCommon.getPixelValue: ' + str(e))
        logger.error('Error in DisplayImageCommon.getPixelValue: ' + str(e))


def getDICOMFileData(self):
        """When a DICOM image is selected in the tree view, this function
        returns its description in the form - study number: series number: image name"""
        try:
            logger.info("DisplayImageCommon.getDICOMFileData called.")
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
            print('Error in DisplayImageCommon.getDICOMFileData: ' + str(e))
            logger.error('Error in DisplayImageCommon.getDICOMFileData: ' + str(e))


def closeSubWindow(self, objectName):
        """Closes a particular sub window in the MDI"""
        logger.info("WEASEL closeSubWindow called for {}".format(objectName))
        for subWin in self.mdiArea.subWindowList():
            if subWin.objectName() == objectName:
                QApplication.processEvents()
                subWin.close()
                QApplication.processEvents()
                break


def closeAllSubWindows(self):
        """Closes all the sub windows open in the MDI"""
        logger.info("WEASEL closeAllSubWindows called")
        self.mdiArea.closeAllSubWindows()
        self.treeView = None  