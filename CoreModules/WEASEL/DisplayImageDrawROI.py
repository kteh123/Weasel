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
import CoreModules.WEASEL.styleSheet as styleSheet
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image
import CoreModules.WEASEL.saveDICOM_Image as saveDICOM_Image
import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.WEASEL.DisplayImageCommon as displayImageCommon
import CoreModules.WEASEL.MessageWindow as messageWindow
import CoreModules.WEASEL.InputDialog as inputDialog
import CoreModules.WEASEL.InterfaceDICOMXMLFile as interfaceDICOMXMLFile
from CoreModules.freeHandROI.GraphicsView import GraphicsView
from CoreModules.freeHandROI.ROI_Storage import ROIs 
import logging
logger = logging.getLogger(__name__)

MAGNIFYING_GLASS_CURSOR = 'CoreModules\\freeHandROI\\cursors\\Magnifying_Glass.png'
PEN_CURSOR = 'CoreModules\\freeHandROI\\cursors\\pencil.png'
ERASOR_CURSOR = 'CoreModules\\freeHandROI\\cursors\\erasor.png'
DELETE_ICON = 'CoreModules\\freeHandROI\\cursors\\delete_icon.png'
NEW_ICON = 'CoreModules\\freeHandROI\\cursors\\new_icon.png'
RESET_ICON = 'CoreModules\\freeHandROI\\cursors\\reset_icon.png'
SAVE_ICON = 'CoreModules\\freeHandROI\\cursors\\save_icon.png'
LOAD_ICON = 'CoreModules\\freeHandROI\\cursors\\load_icon.png'

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


def setUpGraphicsViewSubWindow(self):
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
        logger.info("DisplayImageDrawRIO.setUpGraphicsViewSubWindow called")
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
        hbox = QHBoxLayout()
        layout.addLayout(hbox)
        subWindow.show()
        return hbox, layout, lblImageMissing, subWindow
    except Exception as e:
            print('Error in DisplayImageDrawRIO.setUpGraphicsViewSubWindow: ' + str(e))
            logger.error('Error in DisplayImageDrawRIO.displayMultiImageSubWindow: ' + str(e))


def setUpLevelsSpinBoxes(layout, graphicsView, cmbROIs, imageSlider = None):
    logger.info("DisplayImageDrawROI.setUpLevelsSpinBoxes called.")
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

    groupBoxLevels = QGroupBox('Image Levels')
    gridLayoutLevels = QGridLayout()
    groupBoxLevels.setLayout(gridLayoutLevels)
    layout.addWidget(groupBoxLevels)
    
    gridLayoutLevels.addWidget(lblIntensity, 0,0)
    gridLayoutLevels.addWidget(spinBoxIntensity, 0, 1)
    gridLayoutLevels.addWidget(lblContrast, 0,2)
    gridLayoutLevels.addWidget(spinBoxContrast, 0,3)
    
    spinBoxIntensity.valueChanged.connect(lambda: updateImageLevels(graphicsView,
                spinBoxIntensity.value(), spinBoxContrast.value(),  cmbROIs, imageSlider))
    spinBoxContrast.valueChanged.connect(lambda: updateImageLevels(graphicsView,
                spinBoxIntensity.value(), spinBoxContrast.value(), cmbROIs, imageSlider))  
    layout.addLayout(gridLayoutLevels) 
    return spinBoxIntensity, spinBoxContrast
    

def updateImageLevels(graphicsView, intensity, contrast, cmbROIs, imageSlider = None):
    logger.info("DisplayImageDrawROI.updateImageLevels called.")
    try:
        if imageSlider:
            imageNumber = imageSlider.value()
        else:
            imageNumber = 1
        mask = graphicsView.dictROIs.getMask(cmbROIs.currentText(), imageNumber)
        graphicsView.graphicsItem.updateImageLevels(intensity, contrast, mask)
    except Exception as e:
            print('Error in DisplayImageDrawROI.updateImageLevels when imageNumber={}: '.format(imageNumber) + str(e))
            logger.error('Error in DisplayImageDrawROI.updateImageLevels: ' + str(e))


def setUpPixelDataWidgets(self, layout, graphicsView, imageSlider=None):
    try:
        logger.info("DisplayImageDrawROI.setUpPixelDataWidget called.")
        buttonList = []
        pixelDataLabel = QLabel("Pixel data")
        roiMeanLabel = QLabel("ROI Mean Value")
        lblCmbROIs =  QLabel("ROIs")
        cmbROIs = QComboBox()
        cmbROIs.setDuplicatesEnabled(False)
        cmbROIs.addItem("region1")
        cmbROIs.setCurrentIndex(0)
        graphicsView.roiCombo = cmbROIs

        btnDeleteROI = QPushButton() 
        btnDeleteROI.setToolTip('Delete the current ROI')
        btnDeleteROI.clicked.connect(graphicsView.deleteROI)
        btnDeleteROI.setIcon(QIcon(DELETE_ICON))
        
        btnNewROI = QPushButton() 
        btnNewROI.setToolTip('Add a new ROI')
        btnNewROI.clicked.connect(graphicsView.newROI)
        btnNewROI.setIcon(QIcon(NEW_ICON))

        btnResetROI = QPushButton()
        btnResetROI.setToolTip('Clears the ROI from the image')
        btnResetROI.clicked.connect(graphicsView.resetROI)
        btnResetROI.setIcon(QIcon(RESET_ICON))

        btnSaveROI = QPushButton()
        btnSaveROI.setToolTip('Saves the ROI in DICOM format')
        btnSaveROI.clicked.connect(lambda: saveROI(self, cmbROIs.currentText(), graphicsView))
        btnSaveROI.setIcon(QIcon(SAVE_ICON))

        btnLoad = QPushButton()
        btnLoad.setToolTip('Loads existing ROIs')
        btnLoad.clicked.connect(lambda: loadROI(self, cmbROIs, graphicsView))
        btnLoad.setIcon(QIcon(LOAD_ICON))

        btnErase = QPushButton()
        graphicsView.eraseButton = btnErase
        buttonList.append(btnErase)
        btnErase.setToolTip("Erase the ROI")
        btnErase.setCheckable(True)
        btnErase.setIcon(QIcon(ERASOR_CURSOR))

        btnDraw = QPushButton()
        graphicsView.drawButton = btnDraw
        buttonList.append(btnDraw)
        btnDraw.setToolTip("Draw an ROI")
        btnDraw.setCheckable(True)
        btnDraw.setIcon(QIcon(PEN_CURSOR))

        btnZoom = QPushButton()
        buttonList.append(btnZoom)
        btnZoom.setToolTip("Zoom in/Zoom out of the image")
        btnZoom.setCheckable(True)
        btnZoom.setIcon(QIcon(MAGNIFYING_GLASS_CURSOR))


        btnErase.clicked.connect(lambda checked: eraseROI(btnErase, 
                                                            checked, graphicsView, buttonList))
        btnDraw.clicked.connect(lambda checked: drawROI(btnDraw, 
                                                          checked, graphicsView, buttonList))
        btnZoom.clicked.connect(lambda checked: zoomImage(btnZoom, 
                                                          checked, graphicsView, buttonList))
    

        cmbROIs.setStyleSheet('QComboBox {font: 12pt Arial}')

        cmbROIs.currentIndexChanged.connect(
            lambda: reloadImageInNewImageItem(cmbROIs, graphicsView, pixelDataLabel, 
                                  roiMeanLabel, self, buttonList, imageSlider))

        cmbROIs.editTextChanged.connect( lambda text: roiNameChanged(cmbROIs, graphicsView, text))
        cmbROIs.setToolTip("Displays a list of ROIs created")
        cmbROIs.setEditable(True)
        cmbROIs.setInsertPolicy(QComboBox.InsertAtCurrent)
        spacerItem = QSpacerItem(20, 20, 
                                 QtWidgets.QSizePolicy.Minimum, 
                                 QtWidgets.QSizePolicy.Expanding)

        groupBoxImageData = QGroupBox('ROI')
        gridLayoutROI = QGridLayout()
        gridLayoutImageData =  QGridLayout()
        groupBoxImageData.setLayout(gridLayoutROI)
        layout.addWidget(groupBoxImageData)

        #First row
        gridLayoutROI.addWidget(lblCmbROIs, 0,0, alignment=Qt.AlignRight, )
        gridLayoutROI.addWidget(cmbROIs, 0,1, alignment=Qt.AlignLeft,)
        gridLayoutROI.addWidget(btnNewROI, 0,2, alignment=Qt.AlignLeft, )
        gridLayoutROI.addWidget(btnResetROI, 0,3, alignment=Qt.AlignLeft,)
        gridLayoutROI.addWidget(btnDeleteROI, 0,4, alignment=Qt.AlignLeft,)
        gridLayoutROI.addWidget(btnSaveROI, 0, 5, alignment=Qt.AlignLeft,)
        #Second row
        gridLayoutROI.addItem(spacerItem, 1, 0)
        gridLayoutROI.addItem(spacerItem, 1, 1)
        gridLayoutROI.addWidget(btnLoad, 1, 2, alignment=Qt.AlignLeft,)
        gridLayoutROI.addWidget(btnDraw, 1, 3, alignment=Qt.AlignLeft,)
        gridLayoutROI.addWidget(btnErase, 1,4, alignment=Qt.AlignLeft,)
        gridLayoutROI.addWidget(btnZoom, 1, 5, alignment=Qt.AlignLeft,)
        #Third row
        gridLayoutROI.addWidget(pixelDataLabel, 2, 0, 1, 3)
        gridLayoutROI.addWidget(roiMeanLabel, 2, 4, 1, 2)

        return pixelDataLabel, roiMeanLabel, cmbROIs, buttonList
    except Exception as e:
           print('Error in DisplayImageDrawROI.setUpPixelDataWidgets: ' + str(e))
           logger.error('Error in DisplayImageDrawROI.setUpPixelDataWidgets: ' + str(e))  


def setButtonsToDefaultStyle(buttonList):
    try:
        logger.info("DisplayImageDrawROI.setButtonsToDefaultStyle called.")
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        if buttonList:
            for button in buttonList:
                button.setStyleSheet(
                 "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
                 )
    except Exception as e:
            print('Error in DisplayImageDrawROI.setButtonsToDefaultStyle: ' + str(e))
            logger.error('Error in DisplayImageDrawROI.setButtonsToDefaultStyle: ' + str(e))  


def zoomImage(btn, checked, graphicsView, buttonList):
    logger.info("DisplayImageDrawROI.zoomImage called.")
    if checked:
        setButtonsToDefaultStyle(buttonList)
        graphicsView.setZoomEnabled(True)
        graphicsView.graphicsItem.drawEnabled = False
        graphicsView.graphicsItem.eraseEnabled = False
        btn.setStyleSheet("background-color: red")
    else:
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        graphicsView.setZoomEnabled(False)
        btn.setStyleSheet(
         "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
         )
def drawROI(btn, checked, graphicsView, buttonList):
    logger.info("DisplayImageDrawROI.drawROI called.")
    if checked:
        setButtonsToDefaultStyle(buttonList)
        graphicsView.drawROI()
        btn.setStyleSheet("background-color: red")
    else:
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        graphicsView.graphicsItem.drawEnabled = False
        btn.setStyleSheet(
         "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
         )


def eraseROI(btn, checked, graphicsView, buttonList):
    logger.info("DisplayImageDrawROI.eraseROI called.")
    if checked:
        setButtonsToDefaultStyle(buttonList)
        graphicsView.eraseROI()
        btn.setStyleSheet("background-color: red")
    else:
        QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        graphicsView.graphicsItem.eraseEnabled = False
        btn.setStyleSheet(
         "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
         )


def setUpImageEventHandlers(self, graphicsView, pixelDataLabel, 
                            roiMeanLabel, cmbROIs, buttonList, imageSlider=None):
    logger.info("DisplayImageDrawROI.setUpImageEventHandlers called.")
    graphicsView.graphicsItem.sigMouseHovered.connect(
    lambda: displayImageDataUnderMouse(graphicsView, pixelDataLabel))

    graphicsView.graphicsItem.sigMaskCreated.connect(
        lambda:storeMaskData(graphicsView, cmbROIs.currentText(), imageSlider))

    graphicsView.graphicsItem.sigMaskCreated.connect(
        lambda: displayROIMeanAndStd(self, roiMeanLabel, graphicsView, cmbROIs, imageSlider))

    graphicsView.graphicsItem.sigMaskEdited.connect(
        lambda:replaceMask(graphicsView, cmbROIs.currentText(), imageSlider))

    graphicsView.graphicsItem.sigMaskEdited.connect(
        lambda:storeMaskData(graphicsView, cmbROIs.currentText(), imageSlider))

    graphicsView.sigContextMenuDisplayed.connect(lambda:setButtonsToDefaultStyle(buttonList))

    graphicsView.sigReloadImage.connect(lambda:reloadImageInNewImageItem(cmbROIs, graphicsView, pixelDataLabel, 
                              roiMeanLabel, self, buttonList, imageSlider ))

    graphicsView.sigROIDeleted.connect(lambda:deleteROITidyUp(self, cmbROIs, graphicsView, 
              pixelDataLabel, roiMeanLabel, buttonList, imageSlider))


def setUpGraphicsView(hbox):
    try:
        logger.info("DisplayImageDrawROI.setUpGraphicsView called.")
        zoomSlider = Slider(Qt.Vertical)
        zoomLabel = QLabel("<H4>100%</H4>")
        graphicsView = GraphicsView(zoomSlider, zoomLabel)
        hbox.addWidget(graphicsView)

        zoomSlider.setMinimum(0)
        zoomSlider.setMaximum(20)
        zoomSlider.setSingleStep(1)
        zoomSlider.setTickPosition(QSlider.TicksBothSides)
        zoomSlider.setTickInterval(1)
        zoomSlider.valueChanged.connect(lambda: graphicsView.zoomImage(zoomSlider.direction()))

        groupBoxZoom = QGroupBox('Zoom')
        layoutZoom = QVBoxLayout()
        groupBoxZoom.setLayout(layoutZoom)
        layoutZoom.addWidget(zoomSlider)
        layoutZoom.addWidget(zoomLabel)
        hbox.addWidget(groupBoxZoom)
        return graphicsView
    except Exception as e:
            print('Error in DisplayImageDrawROI.setUpGraphicsView: ' + str(e))
            logger.error('Error in DisplayImageDrawROI.setUpGraphicsViewe: ' + str(e))  


def displayImageROISubWindow(self, derivedImagePath=None):
        """
        Creates a subwindow that displays one DICOM image and allows the creation of an ROI on it 
        """
        try:
            logger.info("DisplayImageDrawROI displayImageROISubWindow called")
            pixelArray = readDICOM_Image.returnPixelArray(self.selectedImagePath)
        
            hbox, layout, lblImageMissing, subWindow = setUpGraphicsViewSubWindow(self)
            windowTitle = displayImageCommon.getDICOMFileData(self)
            subWindow.setWindowTitle(windowTitle)

            graphicsView = setUpGraphicsView(hbox)

            if pixelArray is None:
                lblImageMissing.show()
                graphicsView.setImage(np.array([[0,0,0],[0,0,0]]))  
            else:
                graphicsView.setImage(pixelArray)

            pixelDataLabel, roiMeanLabel, cmbROIs, buttonList = setUpPixelDataWidgets(self, layout, 
                                                                          graphicsView)

            setUpImageEventHandlers(self, graphicsView, pixelDataLabel, roiMeanLabel,
                                    cmbROIs, buttonList)

            spinBoxIntensity, spinBoxContrast = setUpLevelsSpinBoxes(layout, graphicsView, cmbROIs)
            spinBoxIntensity.setValue(graphicsView.graphicsItem.intensity)
            spinBoxContrast.setValue(graphicsView.graphicsItem.contrast)

        except (IndexError, AttributeError):
                subWindow.close()
                msgBox = QMessageBox()
                msgBox.setWindowTitle("View a DICOM series or image with an ROI")
                msgBox.setText("Select either a series or an image")
                msgBox.exec()
        except Exception as e:
            print('Error in DisplayImageDrawROI.displayImageROISubWindow: ' + str(e))
            logger.error('Error in DisplayImageDrawROI.displayImageROISubWindow: ' + str(e)) 


def displayMultiImageROISubWindow(self, imageList, studyName, 
                     seriesName, sliderPosition = -1):
        """
        Creates a subwindow that displays all the DICOM images in a series. 
        A slider allows the user to navigate  through the images.  
        The user may create an ROI on the series of images.
        """
        try:
            logger.info("DisplayImageDrawROI.displayMultiImageROISubWindow called")
            hbox, layout, lblImageMissing, subWindow = setUpGraphicsViewSubWindow(self)
            
            imageSlider = QSlider(Qt.Horizontal)
            imageSlider.setMinimum(1)
            imageSlider.setMaximum(len(imageList))
            if sliderPosition == -1:
                imageSlider.setValue(1)
            else:
                imageSlider.setValue(sliderPosition)
            imageSlider.setSingleStep(1)
            imageSlider.setTickPosition(QSlider.TicksBothSides)
            imageSlider.setTickInterval(1)

            graphicsView = setUpGraphicsView(hbox)
            graphicsView.dictROIs = ROIs(NumImages=len(imageList))
            
            pixelDataLabel, roiMeanLabel, cmbROIs, buttonList = setUpPixelDataWidgets(self, layout, 
                                                                          graphicsView,
                                                                           imageSlider)
            spinBoxIntensity, spinBoxContrast = setUpLevelsSpinBoxes(layout, 
                                                                     graphicsView, 
                                                                     cmbROIs, 
                                                                     imageSlider)

            layout.addWidget(imageSlider)

            imageSlider.valueChanged.connect(
                  lambda: imageROISliderMoved(self, seriesName, 
                                                   imageList, 
                                                   imageSlider,
                                                   lblImageMissing, pixelDataLabel,
                                                   roiMeanLabel, cmbROIs, 
                                                   spinBoxIntensity, 
                                                   spinBoxContrast,
                                                   graphicsView, subWindow,
                                                   buttonList))
           
            imageROISliderMoved(self, seriesName, 
                                    imageList, 
                                    imageSlider,
                                    lblImageMissing, 
                                    pixelDataLabel, 
                                    roiMeanLabel, cmbROIs,
                                    spinBoxIntensity, 
                                    spinBoxContrast,
                                    graphicsView, subWindow, buttonList)
            
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
        logger.info("DisplayImageDrawROI.displayImageDataUnderMouse called")
        xCoord = graphicsView.graphicsItem.xMouseCoord
        yCoord = graphicsView.graphicsItem.yMouseCoord
        pixelColour = graphicsView.graphicsItem.pixelColour
        pixelValue = graphicsView.graphicsItem.pixelValue
        str ="Pixel value {}, Pixel colour {} @ X = {}, Y = {}".format(pixelValue, pixelColour,
                                                                      xCoord, yCoord)
        pixelDataLabel.setText(str)


def getRoiMeanAndStd(mask, pixelArray):
    logger.info("DisplayImageDrawROI.getRoiMeanAndStd called")
    mean = round(np.mean(np.extract(mask, pixelArray)), 3)
    std = round(np.std(np.extract(mask, pixelArray)), 3)
    return mean, std


def displayROIMeanAndStd(self, roiMeanLabel, graphicsView, cmbROIs, imageSlider=None):
        logger.info("DisplayImageDrawROI.displayROIMeanAndStd called")
        if imageSlider:
            imageNumber = imageSlider.value()
        else:
            imageNumber = 1
        pixelArray = readDICOM_Image.returnPixelArray(self.selectedImagePath)
        regionName = cmbROIs.currentText()
        mask = graphicsView.dictROIs.getMask(regionName, imageNumber)
        if mask is not None:
            mean, std = getRoiMeanAndStd(mask, pixelArray)
            str ="ROI mean = {}, standard deviation = {}".format(mean, std)
        else:
            str = ""
        roiMeanLabel.setText(str)
        

def storeMaskData(graphicsView, regionName, imageSlider=None):
        logger.info("DisplayImageDrawROI.storeMaskData called")
        if imageSlider:
            imageNumber = imageSlider.value()
        else:
            imageNumber = 1
        mask = graphicsView.graphicsItem.getMaskData()
        graphicsView.dictROIs.addRegion(regionName, mask, imageNumber)


def replaceMask(graphicsView, regionName, imageSlider=None):
        logger.info("DisplayImageDrawROI.replaceMask called")
        if imageSlider:
            imageNumber = imageSlider.value()
        else:
            imageNumber = 1
        mask = graphicsView.graphicsItem.getMaskData()
        graphicsView.dictROIs.replaceMask(regionName, mask, imageNumber)
        

def imageROISliderMoved(self, seriesName, imageList, imageSlider,
                        lblImageMissing, pixelDataLabel, roiMeanLabel,
                        cmbROIs,
                        spinBoxIntensity, spinBoxContrast,  
                        graphicsView, subWindow, buttonList):
        """On the Multiple Image with ROI Display sub window, this
        function is called when the image slider is moved. 
        It causes the next image in imageList to be displayed"""
        try:
            logger.info("DisplayImageDrawROI.imageROISliderMoved called")
            imageNumber = imageSlider.value()

            currentImageNumber = imageNumber - 1
            if currentImageNumber >= 0:
                self.selectedImagePath = imageList[currentImageNumber]
                #print("imageSliderMoved before={}".format(self.selectedImagePath))
                pixelArray = readDICOM_Image.returnPixelArray(self.selectedImagePath)
                setButtonsToDefaultStyle(buttonList)
                if pixelArray is None:
                    lblImageMissing.show()
                    graphicsView.setImage(np.array([[0,0,0],[0,0,0]]))
                else:
                    reloadImageInNewImageItem(cmbROIs, graphicsView, pixelDataLabel, 
                              roiMeanLabel, self, buttonList, imageSlider) 
 
                    spinBoxIntensity.blockSignals(True)
                    spinBoxIntensity.setValue(graphicsView.graphicsItem.intensity)
                    spinBoxIntensity.blockSignals(False)
                    spinBoxContrast.blockSignals(True)
                    spinBoxContrast.setValue(graphicsView.graphicsItem.contrast)
                    spinBoxContrast.blockSignals(False)
                    setUpImageEventHandlers(self, graphicsView, pixelDataLabel, 
                                            roiMeanLabel, cmbROIs, buttonList,
                                         imageSlider)

                subWindow.setWindowTitle(seriesName + ' - ' 
                         + os.path.basename(self.selectedImagePath))
               # print("imageSliderMoved after={}".format(self.selectedImagePath))
        except Exception as e:
            print('Error in DisplayImageDrawROI.imageROISliderMoved: ' + str(e))
            logger.error('Error in DisplayImageDrawROI.imageROISliderMoved: ' + str(e))


def reloadImageInNewImageItem(cmbROIs, graphicsView, pixelDataLabel, 
                              roiMeanLabel, self, buttonList, imageSlider=None ):
    try:
        logger.info("DisplayImageDrawROI.reloadImageInNewImageItem called")
        graphicsView.dictROIs.setPreviousRegionName(cmbROIs.currentText())

        if imageSlider:
            imageNumber = imageSlider.value()
        else:
            imageNumber = 1

        pixelArray = readDICOM_Image.returnPixelArray(self.selectedImagePath)
        mask = graphicsView.dictROIs.getMask(cmbROIs.currentText(), imageNumber)
        graphicsView.setImage(pixelArray, mask)
        pixelDataLabel.clear() 
        roiMeanLabel.clear()
        setUpImageEventHandlers(self, graphicsView, pixelDataLabel, roiMeanLabel,
                                     cmbROIs, buttonList, imageSlider)
    except Exception as e:
           print('Error in DisplayImageDrawROI.reloadImageInNewImageItem: ' + str(e))
           logger.error('Error in DisplayImageDrawROI.reloadImageInNewImageItem: ' + str(e))
    

def deleteROITidyUp(self, cmbROIs, graphicsView, 
              pixelDataLabel, roiMeanLabel, buttonList, imageSlider=None):
    logger.info("DisplayImageDrawROI.deleteROITidyUp called")
    
    reloadImageInNewImageItem(cmbROIs, graphicsView, pixelDataLabel, 
                              roiMeanLabel, self, buttonList, imageSlider) 
    displayROIMeanAndStd(self, roiMeanLabel, graphicsView, cmbROIs, imageSlider)
    if cmbROIs.currentIndex() == 0 and cmbROIs.count() == 1: 
        cmbROIs.clear()
        cmbROIs.addItem("region1")
        cmbROIs.setCurrentIndex(0) 
        pixelDataLabel.clear()
        roiMeanLabel.clear()
    else:
        if imageSlider:
            imageNumber = imageSlider.value()
        else:
            imageNumber = 1
        cmbROIs.blockSignals(True)
        cmbROIs.removeItem(cmbROIs.currentIndex())
        cmbROIs.blockSignals(False)
        mask = graphicsView.dictROIs.getMask(cmbROIs.currentText(), imageNumber)
        graphicsView.graphicsItem.reloadMask(mask)
 
        
def loadROI(self, cmbROIs, graphicsView):
    try:
        logger.info("DisplayImageDrawROI.loadROI called")
        # Some guidance notes. But bear in mind that these ideas may not survive
        # Their first meeting with reality!
        # I am assuming the workflow is as follows
        #   1. The user first loads a series of DICOM images
        #   2. Then the user loads the series of ROIs that are superimposed upon the images

        # Prompt Windows to select Series
        # paramDict = {"Series":"listview"}
        # listview window doesn't adjust automatically
        paramDict = {"Series":"dropdownlist"}
        helpMsg = "Select a Series with ROI"
        studyID = self.selectedStudy
        study = self.objXMLReader.getStudy(studyID)
        #Build a list of saved ROI series
        listSeries = [series.attrib['id']  for series in study if 'ROI' in series.attrib['id']]
        inputDlg = inputDialog.ParameterInputDialog(paramDict, title= "Load ROI", helpText=helpMsg, lists=[listSeries])
        listParams = inputDlg.returnListParameterValues()
        if inputDlg.closeInputDialog() == False: 
            # Assuming an ROI series is selected
            seriesID = listParams[0]
            imagePathList = self.objXMLReader.getImagePathList(studyID, seriesID)
            maskList = readDICOM_Image.returnSeriesPixelArray(imagePathList)
            regionList = readDICOM_Image.getSeriesTagValues(imagePathList, "ContentDescription")[0]
            # Consider DICOM Tag SegmentSequence[:].SegmentLabel as some 3rd software do

            # First populate the ROI_Storage data structure in a loop
            for imageNumber in range(len(regionList)):
                graphicsView.dictROIs.addRegion(regionList[imageNumber], np.array(maskList[imageNumber], dtype=bool), imageNumber + 1)

            # Second populate the dropdown list of region names
            cmbROIs.blockSignals(True)
            #remove previous contents of ROI dropdown list
            cmbROIs.clear()  
            cmbROIs.addItems(graphicsView.dictROIs.getListOfRegions())
            cmbROIs.blockSignals(False)

            # Redisplay the current image to show the mask
            mask = graphicsView.dictROIs.getMask(regionList[imageNumber], 1)
            graphicsView.graphicsItem.reloadMask(mask)
        
    except Exception as e:
            print('Error in DisplayImageDrawROI.loadROI: ' + str(e))
            logger.error('Error in DisplayImageDrawROI.loadROI: ' + str(e)) 


def saveROI(self, regionName, graphicsView):
    try:
        # Save Current ROI
        logger.info("DisplayImageDrawROI.saveROI called")
        maskList = graphicsView.dictROIs.dictMasks[regionName] # Will return a list of boolean masks
        maskList = [np.array(mask, dtype=np.int) for mask in maskList] # Convert each 2D boolean to 0s and 1s
        suffix = str("_ROI_"+ regionName)
        if len(maskList) > 1:
            inputPath = self.imageList
        else:
            inputPath = [self.selectedImagePath]
        # Saving Progress message
        messageWindow.displayMessageSubWindow(self,
            "<H4>Saving ROIs into a new DICOM Series ({} files)</H4>".format(len(inputPath)),
            "Processing DICOM images")
        outputPath = []
        for image in inputPath:
            outputPath.append(saveDICOM_Image.returnFilePath(image, suffix))
        saveDICOM_Image.saveDicomNewSeries(outputPath, inputPath, maskList, suffix, parametric_map="SEG") # Consider Enhanced DICOM for parametric_map
        seriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self, inputPath, outputPath, suffix)
        treeView.refreshDICOMStudiesTreeView(self, newSeriesName=seriesID)
        messageWindow.closeMessageSubWindow(self)
        QMessageBox.information(self, "Export ROIs", "Image Saved")
    except Exception as e:
            print('Error in DisplayImageDrawROI.saveROI: ' + str(e))
            logger.error('Error in DisplayImageDrawROI.saveROI: ' + str(e)) 

    # Save all ROIs
    #for label, mask in dictROIs.dictMasks.items():

    # Test Affine
    #inputPath1 = ['C:\\Users\\md1jgra\\Desktop\\Joao-3-scanners-2019\\test-affine\\1.2.840.113619.6.408.218238138221875479893414809240658168986-15-1-test.dcm']
    #outputPath = ['C:\\Users\\md1jgra\\Desktop\\Joao-3-scanners-2019\\test-affine\\1.2.840.113619.6.408.218238138221875479893414809240658168986-15-1-test-mask.dcm']
    #newMask = []
    #for index, file in enumerate(inputPath1):
    #    dataset = readDICOM_Image.getDicomDataset(file)
    #    dataset_original = readDICOM_Image.getDicomDataset(inputPath[index])
    #    newMask.append(readDICOM_Image.mapMaskToImage(maskList[index], dataset, dataset_original))
    #saveDICOM_Image.saveDicomNewSeries(outputPath, inputPath1, newMask, suffix, parametric_map="SEG")
    #seriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self, inputPath1, outputPath, suffix)
    #treeView.refreshDICOMStudiesTreeView(self, newSeriesName=seriesID)


def roiNameChanged(cmbROIs, graphicsView, newText):
    try:
        logger.info("DisplayImageDrawROI.roiNameChanged called")
        currentIndex = cmbROIs.currentIndex()
        #Prevent spaces in new ROI name
        if ' ' in newText:
            newText = newText.replace(" ", "")
            print("newText={}".format(newText))
            cmbROIs.setItemText(currentIndex, newText)
            cmbROIs.setCurrentText(newText)
        index = cmbROIs.findText(newText);
        if index == -1:
            cmbROIs.setItemText(currentIndex, newText);
            nameChangedOK = graphicsView.dictROIs.renameDictionaryKey(newText)
            #dictROIs.printContentsDictMasks()
            if nameChangedOK == False:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("ROI Name Change")
                msgBox.setText("This name is already in use")
                msgBox.exec()
                cmbROIs.setCurrentText(graphicsView.dictROIs.prevRegionName)
    except Exception as e:
            print('Error in DisplayImageDrawROI.roiNameChanged: ' + str(e))
            logger.error('Error in DisplayImageDrawROI.roiNameChanged: ' + str(e)) 
