from PyQt5 import QtCore 
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QIcon, QCursor
from PyQt5.QtCore import (Qt, pyqtSignal)
from PyQt5.QtWidgets import (QApplication,
                            QFileDialog,                            
                            QMessageBox, 
                            QWidget, 
                            QGridLayout, 
                            QVBoxLayout, 
                            QHBoxLayout, 
                            QMdiSubWindow, 
                            QGroupBox, 
                            QDoubleSpinBox,
                            QPushButton,  
                            QLabel,  
                            QSlider, 
                            QCheckBox,
                            QSpacerItem,
                            QComboBox)

import os
import scipy
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from scipy.ndimage.morphology import binary_dilation, binary_closing
from scipy.stats import iqr
import CoreModules.WEASEL.ReadDICOM_Image as ReadDICOM_Image
import CoreModules.WEASEL.SaveDICOM_Image as SaveDICOM_Image
import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.DisplayImageCommon as displayImageCommon
import CoreModules.WEASEL.MessageWindow as messageWindow
import Trash.InputDialog as inputDialog # obsolete - replace by user_input
import CoreModules.WEASEL.InterfaceDICOMXMLFile as interfaceDICOMXMLFile
from CoreModules.FreeHandROI.GraphicsView import GraphicsView
from CoreModules.FreeHandROI.ROI_Storage import ROIs 
import CoreModules.FreeHandROI.Resources as icons
from CoreModules.WEASEL.ImageSliders import ImageSliders as imageSliders
from CoreModules.WEASEL.ImageLevelsSpinBoxes import ImageLevelsSpinBoxes as imageLevelsSpinBoxes

import logging
logger = logging.getLogger(__name__)

#Subclassing QSlider so that the direction (Forward, Backward) of 
#slider travel is returned to the calling function
class Slider(QSlider):
    Nothing, Forward, Backward = 0, 1, -1
    directionChanged = pyqtSignal(int)
    def __init__(self, parent=None):
        QSlider.__init__(self, parent)
        self._direction = Slider.Nothing
        self.last = self.value()/self.maximum()
        self.valueChanged.connect(self.onValueChanged)

    def onValueChanged(self, value):
        current = value/self.maximum()
        direction = Slider.Forward if self.last < current else Slider.Backward
        if self._direction != direction:
            self.directionChanged.emit(direction)
            self._direction = direction
        self.last = current

    def direction(self):
        return self._direction


class ImageViewerROI(QMdiSubWindow):
    """This class creates a subwindow for viewing an image or series of images with
    the facility to draw a ROI on the image.  It also has multiple
    sliders for browsing series of images."""

    def __init__(self,  pointerToWeasel, subjectID, 
                 studyID, seriesID, imagePathList): 
        try:
            super().__init__()
            self.subjectID = subjectID
            self.studyID = studyID
            self.seriesID = seriesID
            self.imagePathList = imagePathList
            self.selectedImagePath = ""
            self.imageNumber = -1
            self.weasel = pointerToWeasel
            #A list of the sorted image sliders, 
            #updated as they are added and removed 
            #from the subwindow
            self.listSortedImageSliders = [] 
            
            if singleImageSelected:
                self.isSeries = False
                self.isImage = True
                self.selectedImagePath = imagePathList
            else:
                self.isSeries = True
                self.isImage = False

            self.setWindowFlags(Qt.CustomizeWindowHint | 
                                          Qt.WindowCloseButtonHint | 
                                          Qt.WindowMinimizeButtonHint |
                                          Qt.WindowMaximizeButtonHint)
        
            height, width = self.weasel.getMDIAreaDimensions()
            self.subWindowWidth = width
            #Set dimensions of the subwindow to fit the MDI area
            self.setGeometry(0, 0, width, height)
            #Add subwindow to MDI
            self.weasel.mdiArea.addSubWindow(self)
                
            self.setUpMainLayout() 

            self.setUpTopRowLayout()

            self.setUpGraphicsViewLayout()
            
            self.setUpImageDataLayout()

            self.setUpLevelsSpinBoxes()


    def setUpMainLayout(self):
        try:
            self.mainVerticalLayout = QVBoxLayout()
            self.widget = QWidget()
            self.widget.setLayout(self.mainVerticalLayout)
            self.setWidget(self.widget)
        except Exception as e:
            print('Error in ImageViewer.setUpMainLayout: ' + str(e))
            logger.error('Error in ImageViewer.setUpMainLayout: ' + str(e))


    def setUpRoiToolsLayout(self):
        self.roiToolsLayout = QHBoxLayout()
        self.roiToolsLayout.setContentsMargins(0, 2, 0, 0)
        self.roiToolsLayout.setSpacing(0)
        self.roiToolsGroupBox = QGroupBox("ROIs")
        self.roiToolsGroupBox.setLayout(self.roiToolsLayout)


    def setUpImageLevelsLayout(self):
        self.imageLevelsLayout= QHBoxLayout()
        self.imageLevelsLayout.setContentsMargins(0, 2, 0, 0)
        self.imageLevelsLayout.setSpacing(0)
        self.imageLevelsGroupBox = QGroupBox()
        self.imageLevelsGroupBox.setLayout(imageLevelsLayout)


    def setUpTopRowLayout(self):
        try:
            self.topRowMainLayout = QHBoxLayout()
            
            self.setUpRoiToolsLayout()
            
            self.setUpImageLevelsLayout()
            
            self.topRowMainLayout.addWidget(self.roiToolsGroupBox)
            self.topRowMainLayout.addWidget(self.imageLevelsGroupBox)
        
            self.mainVerticalLayout.addLayout(self.topRowMainLayout)

            self.lblImageMissing = QLabel("<h4>Image Missing</h4>")
            self.lblImageMissing.hide()
            self.mainVerticalLayout.addWidget(self.lblImageMissing)
        except Exception as e:
            print('Error in ImageViewerROI.setUpTopRowLayout: ' + str(e))
            logger.error('Error in ImageViewerROI.setUpTopRowLayout: ' + str(e))


    def setUpGraphicsViewLayout(self):
        self.graphicsViewLayout = QHBoxLayout()
        self.graphicsViewLayout.setContentsMargins(0, 0, 0, 0)
        self.graphicsViewLayout.setSpacing(0)
        self.graphicsView = GraphicsView()
        self.graphicsViewLayout.addWidget(self.graphicsView)
        self.mainVerticalLayout.addLayout(self.graphicsViewLayout)


    def setUpImageDataLayout(self):
        self.imageDataLayout = QHBoxLayout()
        self.imageDataLayout.setContentsMargins(0, 0, 0, 0)
        self.imageDataLayout.setSpacing(0)
        self.imageDataGroupBox = QGroupBox()
        self.imageDataGroupBox.setLayout(self.imageDataLayout)
        self.mainVerticalLayout.addWidget(self.imageDataGroupBox)


    def setUpLevelsSpinBoxes(self):
        try:
            spinBoxObject = imageLevelsSpinBoxes()
            self.imageLevelsLayout.addLayout(spinBoxObject.getCompositeComponent())
            self.spinBoxIntensity, self.spinBoxContrast = spinBoxObject.getSpinBoxes() 
            self.spinBoxIntensity.valueChanged.connect(self.updateImageLevels)
            self.spinBoxContrast.valueChanged.connect(self.updateImageLevels)
        except Exception as e:
            print('Error in ImageViewerROI.setUpLevelsSpinBoxes: ' + str(e))
            logger.error('Error in ImageViewerROI.setUpLevelsSpinBoxes: ' + str(e))


    def updateImageLevels(self):
        logger.info("DisplayImageDrawROI.updateImageLevels called.")
        try:
            #if imageSlider:  To Do
            #    imageNumber = imageSlider.value()
            #else:
            #    imageNumber = 1
            intensity = self.spinBoxIntensity.value()
            contrast = self.spinBoxContrast.value()
            mask = self.graphicsView.dictROIs.getMask(self.cmbROIs.currentText(), imageNumber)
            graphicsView.graphicsItem.updateImageLevels(intensity, contrast, mask)
        except Exception as e:
            print('Error in DisplayImageDrawROI.updateImageLevels when imageNumber={}: '.format(imageNumber) + str(e))
            logger.error('Error in DisplayImageDrawROI.updateImageLevels: ' + str(e))