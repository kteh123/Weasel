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
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image
import numpy as np
from scipy.stats import iqr
import math
import logging
logger = logging.getLogger(__name__)

def setPgColourMap(colourTable, imv, cmbColours=None, lut=None):
    """This function converts a matplotlib colour map into
    a colour map that can be used by the pyqtGraph imageView widget.
    
    Input Parmeters
    ***************
        colourTable - name of the colour map
        imv - name of the imageView widget
        cmbColours - name of the dropdown lists of colour map names
        lut - name of the look up table containing raw colour data
    """

    try:
        if colourTable == None:
            colourTable = 'gray'

        if cmbColours:
            displayColourTableInComboBox(cmbColours, colourTable)   
        
        if colourTable == 'custom':
            colors = lut
        elif colourTable == 'gray':
            colors = [[0.0, 0.0, 0.0, 1.0], [1.0, 1.0, 1.0, 1.0]]
        else:
            cmMap = cm.get_cmap(colourTable)
            colourClassName = cmMap.__class__.__name__
            if colourClassName == 'ListedColormap':
                colors = cmMap.colors
            elif colourClassName == 'LinearSegmentedColormap':
                colors = cmMap(np.linspace(0, 1))
          
        positions = np.linspace(0, 1, len(colors))
        pgMap = pg.ColorMap(positions, colors)
        imv.setColorMap(pgMap)        
    except Exception as e:
        print('Error in DisplayImageCommon.setPgColourMap: ' + str(e))
        logger.error('Error in DisplayImageCommon.setPgColourMap: ' + str(e))


def displayColourTableInComboBox(cmbColours, colourTable):
    """
    This function causes the combobox widget cmbColours to 
    display the name of the colour table stored in the string
    variable colourTable. 

     Input Parmeters
     ****************
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


def setUpViewBoxForImage(layout, spinBoxIntensity = None, spinBoxContrast = None):
    """
    Sets up the pyqtGraph imageView widget and associated colour levels histogram
    for viewing a DICOM image.

    Input Parameters
    *****************
    layout - PyQt5 QVBoxLayout vertical layout box
    spinBoxIntensity - name of the spinbox widget that displays/sets image intensity.
    spinBoxContrast - name of the spinbox widget that displays/sets image contrast.
    """
    try:
        logger.info("DisplayImageCommon.setUpViewBoxForImage called")
        #imageViewer  = pyqtGraph Graphics Layout Used for laying out GraphicsWidgets in a grid
        imageViewer = pg.GraphicsLayoutWidget()
        plotItem = imageViewer.addPlot() 
        plotItem.getViewBox().setAspectLocked() 
        img = pg.ImageItem(border='w')
            
        imv= pg.ImageView(view=plotItem, imageItem=img)
        #imv= pg.ImageView()  #this works too
        if spinBoxIntensity and spinBoxContrast:
            histogramObject = imv.getHistogramWidget().getHistogram()
            histogramObject.sigLevelsChanged.connect(lambda: getHistogramLevels(imv, spinBoxIntensity, spinBoxContrast))
        imv.ui.roiBtn.hide()
        imv.ui.menuBtn.hide()
        layout.addWidget(imv)
 
        return img, imv, plotItem
    except Exception as e:
        print('Error in DisplayImageCommon.setUpViewBoxForImag: ' + str(e))
        logger.error('Error in DisplayImageCommon.setUpViewBoxForImag: ' + str(e))


def getHistogramLevels(imv, spinBoxIntensity, spinBoxContrast):
        """
        This function determines contrast and intensity from the image
        and set the contrast & intensity spinboxes to these values.

        Input Parameters
        *****************
        imv - pyqtGraph imageView widget
        spinBoxIntensity - name of the spinbox widget that displays/sets image intensity.
        spinBoxContrast - name of the spinbox widget that displays/sets image contrast.
        """
        minLevel, maxLevel = imv.getLevels()
        width = maxLevel - minLevel
        centre = minLevel + (width/2)
        spinBoxIntensity.setValue(centre)
        spinBoxContrast.setValue(width)


def setUpImageViewerSubWindow(self):
    """
    This function creates a subwindow with a vertical layout &
    a missing image label.

    Input Parameters
    ****************
    self - an object reference to the WEASEL interface.

    Output Parameters
    *****************
    layout - PyQt5 QVBoxLayout vertical layout box
    lblImageMissing - Label displaying the text 'Missing Image'. Hidden 
                        until WEASEL tries to display a missing image
    subWindow - An QMdiSubWindow subwindow
    """
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
        widget = QWidget()
        widget.setLayout(layout)
        subWindow.setWidget(widget)
        
        lblImageMissing = QLabel("<h4>Image Missing</h4>")
        lblImageMissing.hide()
        layout.addWidget(lblImageMissing)
        subWindow.show()
        return layout, lblImageMissing, subWindow
    except Exception as e:
            print('Error in DisplayImageCommon.setUpImageViewerSubWindow: ' + str(e))
            logger.error('Error in DisplayImageCommon.displayMultiImageSubWindow: ' + str(e))


def getPixelValue(pos, imv, pixelArray, lblPixelValue):
    """
    This function checks that the mouse pointer is over the
    image and when it is, it determines the value of the pixel
    under the mouse pointer and displays this in the label
    lblPixelValue.

    Input parameters
    ****************
    pos - X,Y coordinates of the mouse pointer
    imv - pyqtGraph imageView widget
    pixelArray - pixel array to be displayed in imv
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
            z_i = imv.currentIndex
            if (len(np.shape(pixelArray)) == 2) and y_i >= 0 and y_i < pixelArray.shape [ 1 ] \
                and x_i >= 0 and x_i < pixelArray.shape [ 0 ]: 
                lblPixelValue.setText(
                    "<h4>Pixel Value = {} @ X: {}, Y: {}</h4>"
                .format (round(pixelArray[ x_i, y_i ], 3), x_i, y_i))
            elif (len(np.shape(pixelArray)) == 3) and z_i >= 0 and z_i < pixelArray.shape [ 0 ] \
                and x_i >= 0 and x_i < pixelArray.shape [ 1 ] \
                and y_i >= 0 and y_i < pixelArray.shape [ 2 ]:
                lblPixelValue.setText(
                    "<h4>Pixel Value = {} @ X: {}, Y: {}, Z: {}</h4>"
                .format (round(pixelArray[ z_i, x_i, y_i ], 3), x_i, y_i, z_i))
            else:
                lblPixelValue.setText("<h4>Pixel Value:</h4>")
        else:
            lblPixelValue.setText("<h4>Pixel Value:</h4>")
                   
    except Exception as e:
        print('Error in DisplayImageCommon.getPixelValue: ' + str(e))
        logger.error('Error in DisplayImageCommon.getPixelValue: ' + str(e))


def getDICOMFileData(self):
        """When a DICOM image is selected in the tree view, this function
        returns its description in the form - study number: series number: image name
        
         Input Parameters
        ****************
            self - an object reference to the WEASEL interface.


        Output Parameters
        *****************
        fullImageName - string containing the full description of a DICOM image
        """
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


def readLevelsFromDICOMImage(self, pixelArray): 
        """Reads levels directly from the DICOM image
        
        Input Parmeters
        ***************
        self - an object reference to the WEASEL interface.
        pixelArray - pixel array to be displayed

        Output Parameters
        *****************
        centre - Image intensity
        width - Image contrast
        maximumValue - Maximum pixel value in the image
        minimumValue - Minimum pixel value in the image
        """
        try:
            logger.info("DisplayImageCommon.readLevelsFromDICOMImage called")
            #set default values
            centre = -1 
            width = -1 
            maximumValue = -1  
            minimumValue = -1 
            dataset = readDICOM_Image.getDicomDataset(self.selectedImagePath)
            if dataset and hasattr(dataset, 'WindowCenter') and hasattr(dataset, 'WindowWidth'):
                slope = float(getattr(dataset, 'RescaleSlope', 1))
                intercept = float(getattr(dataset, 'RescaleIntercept', 0))
                centre = dataset.WindowCenter * slope + intercept
                width = dataset.WindowWidth * slope
                maximumValue = centre + width/2
                minimumValue = centre - width/2
            elif dataset and hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
                # In Enhanced MRIs, this display will retrieve the centre and width values of the first slice
                slope = dataset.PerFrameFunctionalGroupsSequence[0].PixelValueTransformationSequence[0].RescaleSlope
                intercept = dataset.PerFrameFunctionalGroupsSequence[0].PixelValueTransformationSequence[0].RescaleIntercept
                centre = dataset.PerFrameFunctionalGroupsSequence[0].FrameVOILUTSequence[0].WindowCenter * slope + intercept
                width = dataset.PerFrameFunctionalGroupsSequence[0].FrameVOILUTSequence[0].WindowWidth * slope
                maximumValue = centre + width/2
                minimumValue = centre - width/2 
            else:
                minimumValue = np.amin(pixelArray) if (np.median(pixelArray) - iqr(pixelArray, rng=(
                1, 99))/2) < np.amin(pixelArray) else np.median(pixelArray) - iqr(pixelArray, rng=(1, 99))/2
                maximumValue = np.amax(pixelArray) if (np.median(pixelArray) + iqr(pixelArray, rng=(
                1, 99))/2) > np.amax(pixelArray) else np.median(pixelArray) + iqr(pixelArray, rng=(1, 99))/2
                centre = minimumValue + (abs(maximumValue) - abs(minimumValue))/2
                width = maximumValue - abs(minimumValue)

            return centre, width, maximumValue, minimumValue
        except Exception as e:
            print('Error in DisplayImageCommon.readLevelsFromDICOMImage: ' + str(e))
            logger.error('Error in DisplayImageCommon.readLevelsFromDICOMImage: ' + str(e))


def closeSubWindow(self, objectName):
        """Closes a particular sub window in the MDI
        
        Input Parmeters
        ***************
        self - an object reference to the WEASEL interface.
        objectName - object name of the subwindow to be closed
        """
        logger.info("WEASEL closeSubWindow called for {}".format(objectName))
        for subWin in self.mdiArea.subWindowList():
            if subWin.objectName() == objectName:
                QApplication.processEvents()
                subWin.close()
                QApplication.processEvents()
                break