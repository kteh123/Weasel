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
import logging
logger = logging.getLogger(__name__)

def setPgColourMap(cm_name, imv, cmbColours=None, lut=None):
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
        print('Error in displayImage.setPgColourMap: ' + str(e))
        logger.error('Error in displayImage.setPgColourMap: ' + str(e))


def displayColourTableInComboBox(cmbColours, colourTable):
    try:
        cmbColours.blockSignals(True)
        index = cmbColours.findText(colourTable)
        if index >= 0:
            cmbColours.setCurrentIndex(index)
        cmbColours.blockSignals(False)
    except Exception as e:
            print('Error in displayImage.displayColourTableInComboBox: ' + str(e))
            logger.error('Error in displayImage.displayColourTableInComboBox: ' + str(e))


def setUpViewBoxForImage(imageViewer, layout, spinBoxCentre = None, spinBoxWidth = None):
    try:
        logger.info("displyImage.setUpViewBoxForImage called")
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
        print('Error in displayImage.setUpViewBoxForImag: ' + str(e))
        logger.error('Error in displayImage.setUpViewBoxForImag: ' + str(e))


def getHistogramLevels(imv, spinBoxCentre, spinBoxWidth):
        minLevel, maxLevel = imv.getLevels()
        width = maxLevel - minLevel
        centre = minLevel + (width/2)
        spinBoxCentre.setValue(centre)
        spinBoxWidth.setValue(width)


def setUpImageViewerSubWindow(self):
    try:
        logger.info("displyImage.setUpImageViewerSubWindow called")
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
            print('Error in displyImage.setUpImageViewerSubWindow: ' + str(e))
            logger.error('Error in displayImage.displayMultiImageSubWindow: ' + str(e))
