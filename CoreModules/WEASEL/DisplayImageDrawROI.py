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
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image
import CoreModules.WEASEL.saveDICOM_Image as saveDICOM_Image
import CoreModules.WEASEL.TreeView as treeView
import CoreModules.WEASEL.DisplayImageCommon as displayImageCommon
import CoreModules.WEASEL.MessageWindow as messageWindow
import CoreModules.WEASEL.InputDialog as inputDialog
import CoreModules.WEASEL.InterfaceDICOMXMLFile as interfaceDICOMXMLFile
from CoreModules.FreeHandROI.GraphicsView import GraphicsView
from CoreModules.FreeHandROI.ROI_Storage import ROIs 
import CoreModules.FreeHandROI.Resources as icons
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


def displayManySingleImageSubWindows(self):
    if len(self.checkedImageList)>0: 
        for image in self.checkedImageList:
            subjectID = image[0]
            studyName = image[1]
            seriesName = image[2]
            imagePath = image[3]
            displayImageROISubWindow(self, subjectID, studyName, seriesName, imagePath)


def displayManyMultiImageSubWindows(self):
    if len(self.checkedSeriesList)>0: 
        for series in self.checkedSeriesList:
            subjectName = series[0]
            studyName = series[1]
            seriesName = series[2]
            imageList = treeView.returnSeriesImageList(self, subjectName, studyName, seriesName)
            displayMultiImageROISubWindow(self, imageList, subjectName, studyName, 
                     seriesName, sliderPosition = -1)


def displayImageROISubWindow(self, subjectID, studyName, seriesName, imagePath):
    """
    Creates a subwindow that displays one DICOM image and allows an ROI 
    to be drawn on it 
    """
    try:
        logger.info("DisplayImageDrawROI displayImageROISubWindow called")
        
        (graphicsView, roiToolsLayout, imageLevelsLayout, 
        graphicsViewLayout, sliderLayout, 
        imageDataLayout, lblImageMissing, subWindow) = setUpSubWindow(self)
        imageName = os.path.basename(imagePath)
        windowTitle = subjectID + "-" + studyName + "-" + seriesName + "-" + imageName
        subWindow.setWindowTitle(windowTitle)
        #subWindow.setStyleSheet("background-color:#d9d9d9;")

        zoomSlider, zoomValueLabel = setUpZoomSlider(graphicsView)

        pixelValueTxt, roiMeanTxt, roiStdDevTxt = setUpImageDataWidgets(imageDataLayout, 
                                                        graphicsView, 
                                                        zoomValueLabel)
        
        cmbROIs, buttonList, btnDraw, btnErase = setUpROIButtons(self, 
                              roiToolsLayout, pixelValueTxt, roiMeanTxt, roiStdDevTxt, graphicsView, 
                             zoomSlider, zoomValueLabel, subjectID, studyName)
        
        spinBoxIntensity, spinBoxContrast = setUpLevelsSpinBoxes(imageLevelsLayout, 
                                                                 graphicsView, cmbROIs)
           
        pixelArray = readDICOM_Image.returnPixelArray(imagePath)
        if pixelArray is None:
            lblImageMissing.show()
            graphicsView.setImage(np.array([[0,0,0],[0,0,0]]))  
        else:
            graphicsView.setImage(pixelArray)

        setInitialImageLevelValues(graphicsView, spinBoxIntensity, spinBoxContrast)
            
        setUpImageEventHandlers(self, graphicsView, pixelValueTxt,         
                                    roiMeanTxt, roiStdDevTxt, 
                                        btnDraw, btnErase,
                                         cmbROIs, buttonList,
                                        zoomSlider, zoomValueLabel)
        
        
    except (IndexError, AttributeError):
            subWindow.close()
            msgBox = QMessageBox()
            msgBox.setWindowTitle("View a DICOM series or image with an ROI")
            msgBox.setText("Select either a series or an image")
            msgBox.exec()
    except Exception as e:
        print('Error in DisplayImageDrawROI.displayImageROISubWindow: ' + str(e))
        logger.error('Error in DisplayImageDrawROI.displayImageROISubWindow: ' + str(e))  


def displayManyMultiImageSubWindows(self):
    if len(self.checkedSeriesList)>0: 
        for series in self.checkedSeriesList:
            subjectName = series[0]
            studyName = series[1]
            seriesName = series[2]
            imageList = treeView.returnSeriesImageList(self, subjectName, studyName, seriesName)
            displayMultiImageROISubWindow(self, imageList, subjectName, studyName, 
                     seriesName, sliderPosition = -1)


def displayMultiImageROISubWindow(self, imageList, subjectName, studyName, 
                     seriesName, sliderPosition = -1 ):
        """
        Creates a subwindow that displays all the DICOM images in a series. 
        A slider allows the user to navigate  through the images.  
        The user may create an ROI on the series of images.
        """
        try:
            logger.info("DisplayImageDrawROI.displayMultiImageROISubWindow called")
            (graphicsView, roiToolsLayout, imageLevelsLayout, 
            graphicsViewLayout, sliderLayout, 
            imageDataLayout, lblImageMissing, subWindow) = setUpSubWindow(self, imageSeries=True)
            #subWindow.setStyleSheet("background-color:#737373;")
            imageSlider, imageNumberLabel = setUpImageSlider(sliderLayout, sliderPosition, imageList, subWindow)
           
            zoomSlider, zoomValueLabel = setUpZoomSlider(graphicsView)

            pixelValueTxt, roiMeanTxt, roiStdDevTxt = setUpImageDataWidgets(imageDataLayout, 
                                                               graphicsView, 
                                                        zoomValueLabel)
        
            cmbROIs, buttonList, btnDraw, btnErase = setUpROIButtons(self, 
                              roiToolsLayout, pixelValueTxt, roiMeanTxt, roiStdDevTxt, 
                             graphicsView, zoomSlider, zoomValueLabel, subjectName, studyName)
        
            spinBoxIntensity, spinBoxContrast = setUpLevelsSpinBoxes(imageLevelsLayout, 
                                                                 graphicsView, cmbROIs)
           
            graphicsView.dictROIs = ROIs(NumImages=len(imageList))
            
            imageSlider.valueChanged.connect(
                  lambda: imageROISliderMoved(self, subjectName, studyName, seriesName, 
                                                   imageList, 
                                                   imageSlider,
                                                   lblImageMissing, pixelValueTxt, 
                                                   roiMeanTxt, roiStdDevTxt, cmbROIs,
                                                   btnDraw, btnErase,
                                                   spinBoxIntensity, 
                                                   spinBoxContrast,
                                                   graphicsView, subWindow, buttonList, zoomSlider,
                                                   zoomValueLabel, imageNumberLabel))
          
            imageROISliderMoved(self, subjectName, studyName, seriesName, 
                                    imageList, 
                                    imageSlider,
                                    lblImageMissing, 
                                    pixelValueTxt,  
                                    roiMeanTxt, roiStdDevTxt, cmbROIs,
                                    btnDraw, btnErase,
                                    spinBoxIntensity, 
                                    spinBoxContrast,
                                    graphicsView, subWindow, 
                                    buttonList, zoomSlider, 
                                    zoomValueLabel, imageNumberLabel)       
        except (IndexError, AttributeError):
                subWindow.close()
                msgBox = QMessageBox()
                msgBox.setWindowTitle("View a DICOM series or image with an ROI")
                msgBox.setText("Select either a series or an image")
                msgBox.exec()    
        except Exception as e:
            print('Error in displayMultiImageROISubWindow: ' + str(e))
            logger.error('Error in displayMultiImageROISubWindow: ' + str(e))


def setUpSubWindow(self, imageSeries=False):
    """
    This function creates a subwindow with a vertical mainVerticalLayout &
    a missing image label.

    Input Parameters
    ****************
    self - an object reference to the WEASEL interface.

    Output Parameters
    *****************
    mainVerticalLayout - PyQt5 QVBoxLayout vertical mainVerticalLayout box
    lblImageMissing - Label displaying the text 'Missing Image'. Hidden 
                        until WEASEL tries to display a missing image
    subWindow - An QMdiSubWindow subwindow
    """
    try:
        logger.info("DisplayImageDrawRIO.setUpSubWindow called")
        subWindow = QMdiSubWindow(self)
        subWindow.setObjectName = 'image_viewer'
        subWindow.setWindowFlags(Qt.CustomizeWindowHint | 
                                      Qt.WindowCloseButtonHint | 
                                      Qt.WindowMinimizeButtonHint |
                                      Qt.WindowMaximizeButtonHint)
        
        
        height, width = self.getMDIAreaDimensions()
        subWindow.setGeometry(0, 0, width, height)
        self.mdiArea.addSubWindow(subWindow)
        
        mainVerticalLayout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(mainVerticalLayout)
        subWindow.setWidget(widget)

        topRowMainLayout = QHBoxLayout()
        roiToolsLayout = QHBoxLayout()
        roiToolsLayout.setContentsMargins(0, 2, 0, 0)
        roiToolsLayout.setSpacing(0)
        roiToolsGroupBox = QGroupBox("ROIs")
        roiToolsGroupBox.setLayout(roiToolsLayout)
        imageLevelsLayout= QHBoxLayout()
        imageLevelsLayout.setContentsMargins(0, 2, 0, 0)
        imageLevelsLayout.setSpacing(0)
        imageLevelsGroupBox = QGroupBox()
        imageLevelsGroupBox.setLayout(imageLevelsLayout)
        topRowMainLayout.addWidget(roiToolsGroupBox)
        topRowMainLayout.addWidget(imageLevelsGroupBox)
        
        mainVerticalLayout.addLayout(topRowMainLayout)

        lblImageMissing = QLabel("<h4>Image Missing</h4>")
        lblImageMissing.hide()
        mainVerticalLayout.addWidget(lblImageMissing)
        graphicsViewLayout = QHBoxLayout()
        graphicsViewLayout.setContentsMargins(0, 0, 0, 0)
        graphicsViewLayout.setSpacing(0)
        graphicsView = GraphicsView()
        graphicsViewLayout.addWidget(graphicsView)
        mainVerticalLayout.addLayout(graphicsViewLayout)
        imageDataLayout = QHBoxLayout()
        imageDataLayout.setContentsMargins(0, 0, 0, 0)
        imageDataLayout.setSpacing(0)
        imageDataGroupBox = QGroupBox()
        imageDataGroupBox.setLayout(imageDataLayout)
        mainVerticalLayout.addWidget(imageDataGroupBox)

        sliderLayout = QHBoxLayout()
        if imageSeries:
            mainVerticalLayout.addLayout(sliderLayout)

        subWindow.show()
        return (graphicsView, roiToolsLayout, imageLevelsLayout, 
                graphicsViewLayout, sliderLayout, 
                imageDataLayout, lblImageMissing, subWindow)
    except Exception as e:
            print('Error in DisplayImageDrawRIO.setUpSubWindow: ' + str(e))
            logger.error('Error in DisplayImageDrawRIO.setUpSubWindow: ' + str(e))


def setUpROIButtons(self, roiToolsLayout, pixelValueTxt,
         roiMeanTxt, roiStdDevTxt, graphicsView, 
         zoomSlider, zoomLabel, subjectID, studyID, imageSlider=None):
    try:
        logger.info("DisplayImageDrawROI.setUpPixelDataWidget called.")
        buttonList = []
        cmbROIs = QComboBox()
        lblCmbROIs =  QLabel("ROIs")
        cmbROIs.setDuplicatesEnabled(False)
        cmbROIs.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        cmbROIs.addItem("region1")
        cmbROIs.setCurrentIndex(0)

        btnDeleteROI = QPushButton() 
        btnDeleteROI.setToolTip('Delete the current ROI')
        btnDeleteROI.clicked.connect(graphicsView.deleteROI)
        btnDeleteROI.setIcon(QIcon(QPixmap(icons.DELETE_ICON)))
        
        btnNewROI = QPushButton() 
        btnNewROI.setToolTip('Add a new ROI')
        btnNewROI.clicked.connect(graphicsView.newROI)
        btnNewROI.setIcon(QIcon(QPixmap(icons.NEW_ICON)))

        btnResetROI = QPushButton()
        btnResetROI.setToolTip('Clears the ROI from the image')
        btnResetROI.clicked.connect(graphicsView.resetROI)
        btnResetROI.setIcon(QIcon(QPixmap(icons.RESET_ICON)))

        btnSaveROI = QPushButton()
        btnSaveROI.setToolTip('Saves the ROI in DICOM format')
        btnSaveROI.clicked.connect(lambda: saveROI(self, cmbROIs.currentText(), graphicsView))
        btnSaveROI.setIcon(QIcon(QPixmap(icons.SAVE_ICON)))

        btnLoad = QPushButton()
        btnLoad.setToolTip('Loads existing ROIs')
        btnLoad.clicked.connect(lambda: loadROI(self, cmbROIs, 
                                            graphicsView, subjectID, studyID))
        btnLoad.setIcon(QIcon(QPixmap(icons.LOAD_ICON)))

        btnErase = QPushButton()
        buttonList.append(btnErase)
        btnErase.setToolTip("Erase the ROI")
        btnErase.setCheckable(True)
        btnErase.setIcon(QIcon(QPixmap(icons.ERASOR_CURSOR)))

        btnDraw = QPushButton()
        buttonList.append(btnDraw)
        btnDraw.setToolTip("Draw an ROI")
        btnDraw.setCheckable(True)
        btnDraw.setIcon(QIcon(QPixmap(icons.PEN_CURSOR)))

        btnZoom = QPushButton()
        buttonList.append(btnZoom)
        btnZoom.setToolTip("Zoom In-Left Mouse Button/Zoom Out-Right Mouse Button")
        btnZoom.setCheckable(True)
        btnZoom.setIcon(QIcon(QPixmap(icons.MAGNIFYING_GLASS_CURSOR)))

        btnErase.clicked.connect(lambda checked: eraseROI(btnErase, 
                                                            checked, graphicsView, buttonList))
        btnDraw.clicked.connect(lambda checked: drawROI(btnDraw, 
                                                          checked, graphicsView, buttonList))
        btnZoom.clicked.connect(lambda checked: zoomImage(btnZoom, 
                                                          checked, graphicsView, buttonList))

        cmbROIs.setStyleSheet('QComboBox {font: 12pt Arial}')

        cmbROIs.currentIndexChanged.connect(
            lambda: reloadImageInNewImageItem(cmbROIs, graphicsView, pixelValueTxt,                          
                                   roiMeanTxt, roiStdDevTxt, self, buttonList, 
                                   btnDraw, btnErase, 
                                  zoomSlider, zoomLabel, imageSlider))

        cmbROIs.editTextChanged.connect( lambda text: roiNameChanged(cmbROIs, graphicsView, text))
        cmbROIs.setToolTip("Displays a list of ROIs created")
        cmbROIs.setEditable(True)
        cmbROIs.setInsertPolicy(QComboBox.InsertAtCurrent)
        
        roiToolsLayout.addWidget(cmbROIs,  alignment=Qt.AlignLeft)
        roiToolsLayout.addWidget(btnNewROI, alignment=Qt.AlignLeft)
        roiToolsLayout.addWidget(btnResetROI,  alignment=Qt.AlignLeft)
        roiToolsLayout.addWidget(btnDeleteROI,  alignment=Qt.AlignLeft)
        roiToolsLayout.addWidget(btnSaveROI,  alignment=Qt.AlignLeft)
        roiToolsLayout.addWidget(btnLoad,  alignment=Qt.AlignLeft)
        roiToolsLayout.addWidget(btnDraw,  alignment=Qt.AlignLeft)
        roiToolsLayout.addWidget(btnErase, alignment=Qt.AlignLeft)
        roiToolsLayout.addWidget(btnZoom,  alignment=Qt.AlignLeft)
        roiToolsLayout.addStretch(20)
        return  cmbROIs, buttonList, btnDraw, btnErase
    except Exception as e:
           print('Error in DisplayImageDrawROI.setUpROIButtons: ' + str(e))
           logger.error('Error in DisplayImageDrawROI.setUpROIButtons: ' + str(e))  


def setUpLevelsSpinBoxes(imageLevelsLayout, graphicsView, cmbROIs, imageSlider = None): 
    logger.info("DisplayImageDrawROI.setUpLevelsSpinBoxes called.")
    spinBoxIntensity, spinBoxContrast = displayImageCommon. setUpLevelsSpinBoxes(imageLevelsLayout)
    spinBoxIntensity.valueChanged.connect(lambda: updateImageLevels(graphicsView,
                spinBoxIntensity.value(), spinBoxContrast.value(),  cmbROIs, imageSlider))
    spinBoxContrast.valueChanged.connect(lambda: updateImageLevels(graphicsView,
                spinBoxIntensity.value(), spinBoxContrast.value(), cmbROIs, imageSlider))  
  
    return spinBoxIntensity, spinBoxContrast


def setUpImageDataWidgets(imageDataLayout, graphicsView, zoomValueLabel, imageSlider = None):
    try:
        logger.info("DisplayImageDrawROI.setUpImageDataWidgets called.")
        
        pixelValueLabel = QLabel("Pixel Value")
        pixelValueLabel.setAlignment(Qt.AlignRight)
        pixelValueLabel.setStyleSheet("padding-right:1; margin-right:1;")
        pixelValueTxt = QLabel()
        pixelValueTxt.setIndent(0)
        pixelValueTxt.setAlignment(Qt.AlignLeft)
        pixelValueTxt.setStyleSheet("color : red; padding-left:1; margin-left:1;")

        roiMeanLabel = QLabel("ROI Mean")
        roiMeanLabel.setStyleSheet("padding-right:1; margin-right:1;")
        roiMeanTxt = QLabel()
        roiMeanTxt.setStyleSheet("color : red; padding-left:1; margin-left:1;")
        roiStdDevLabel = QLabel("ROI Sdev.")
        roiStdDevLabel.setStyleSheet("padding-right:1; margin-right:1;")
        roiStdDevTxt = QLabel()
        roiStdDevTxt.setStyleSheet("color : red; padding-left:1; margin-left:1;")
        zoomLabel = QLabel("Zoom:")
        zoomLabel.setStyleSheet("padding-right:1; margin-right:1;")
        zoomValueLabel.setStyleSheet("color : red; padding-left:1; margin-left:1;")
        
        imageDataLayout.addWidget(pixelValueLabel, Qt.AlignRight)
        imageDataLayout.addWidget(pixelValueTxt, Qt.AlignLeft)
        imageDataLayout.addWidget(roiMeanLabel, Qt.AlignLeft) 
        imageDataLayout.addWidget(roiMeanTxt, Qt.AlignLeft) 
        imageDataLayout.addWidget(roiStdDevLabel, Qt.AlignLeft)
        imageDataLayout.addWidget(roiStdDevTxt, Qt.AlignLeft)
        imageDataLayout.addWidget(zoomLabel, Qt.AlignLeft)
        imageDataLayout.addWidget(zoomValueLabel, Qt.AlignLeft)
        imageDataLayout.addStretch(10)
    
        return (pixelValueTxt,  
                roiMeanTxt, roiStdDevTxt)
    except Exception as e:
            print('Error in DisplayImageDrawROI.setUpImageDataWidgets: ' + str(e))
            logger.error('Error in DisplayImageDrawROI.setUpImageDataWidgets: ' + str(e))


def setUpImageSlider(sliderLayout, sliderPosition, imageList, subWindow):
    try:
        imageSlider = QSlider(Qt.Horizontal)
        imageSlider.setFocusPolicy(Qt.StrongFocus) # This makes the slider work with arrow keys on Mac OS
        imageSlider.setToolTip("Use this slider to navigate the series of DICOM images")
        maxNumberImages = len(imageList)
        imageSlider.setMinimum(1)
        imageSlider.setMaximum(maxNumberImages)
        if maxNumberImages < 4:
            imageSlider.setFixedWidth(subWindow.width()*.2)
        elif maxNumberImages > 3 and maxNumberImages < 11:
            imageSlider.setFixedWidth(subWindow.width()*.5)
        else:
            imageSlider.setFixedWidth(subWindow.width()*.85)
        if sliderPosition == -1:
            imageSlider.setValue(1)
        else:
            imageSlider.setValue(sliderPosition)
        imageSlider.setSingleStep(1)
        imageSlider.setTickPosition(QSlider.TicksBothSides)
        imageSlider.setTickInterval(1)

        sliderLayout.addWidget(imageSlider)
        imageNumberLabel = QLabel()
        sliderLayout.addWidget(imageNumberLabel)
        return imageSlider, imageNumberLabel
    except Exception as e:
        print('Error in DisplayImageDrawROI.setUpImageSlider: ' + str(e))
        logger.error('Error in DisplayImageDrawROI.setUpImageSlider: ' + str(e))


def setUpZoomSlider(graphicsView):
    try:
        zoomSlider = Slider(Qt.Vertical)
        zoomLabel = QLabel("<H4>100%</H4>")
        zoomSlider.setMinimum(0)
        zoomSlider.setMaximum(20)
        zoomSlider.setSingleStep(1)
        zoomSlider.setTickPosition(QSlider.TicksBothSides)
        zoomSlider.setTickInterval(1)
        zoomSlider.valueChanged.connect(lambda: graphicsView.zoomImage(zoomSlider.direction()))

        return zoomSlider, zoomLabel
    except Exception as e:
            print('Error in DisplayImageDrawROI.setUpZoomSlider: ' + str(e))
            logger.error('Error in DisplayImageDrawROI.setUpZoomSlider: ' + str(e))  


def addNewROItoDropDownList(newRegion, roiCombo):
    logger.info("DisplayImageDrawROI.addNewROItoDropDownList called.")
    noDuplicate = True
    for count in range(roiCombo.count()):
         if roiCombo.itemText(count) == newRegion:
             noDuplicate = False
             break
    if noDuplicate:
        roiCombo.blockSignals(True)
        roiCombo.addItem(newRegion)
        roiCombo.setCurrentIndex(roiCombo.count() - 1)
        roiCombo.blockSignals(False)
    

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


def setEraseButtonColour(setRed, btnDraw, btnErase):
    logger.info("DisplayImageDrawRIO.setEraseButtonColour called")
    if setRed:
           btnErase.setStyleSheet("background-color: red")
           btnDraw.setStyleSheet(
            "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
             )
    else:
           btnErase.setStyleSheet(
             "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
             )


def setDrawButtonColour(setRed, btnDraw, btnErase):
    logger.info("DisplayImageDrawRIO.setDrawButtonColour called")
    if setRed:
           btnDraw.setStyleSheet("background-color: red")
           btnErase.setStyleSheet(
            "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
             )
    else:
           btnDraw.setStyleSheet(
             "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
             )


def setButtonsToDefaultStyle(buttonList):
    logger.info("DisplayImageDrawRIO.setButtonsToDefaultStyle called")
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


def setUpImageEventHandlers(self, graphicsView, pixelValueTxt,  
                            roiMeanTxt, roiStdDevTxt, btnDraw, btnErase,
                            cmbROIs, buttonList, zoomSlider, zoomLabel, imageSlider=None):
    logger.info("DisplayImageDrawROI.setUpImageEventHandlers called.")
    try:
        graphicsView.graphicsItem.sigMouseHovered.connect(
        lambda mouseOverImage:displayImageDataUnderMouse(mouseOverImage, graphicsView, 
                                                         pixelValueTxt, imageSlider))

        graphicsView.graphicsItem.sigMaskCreated.connect(
            lambda:storeMaskData(graphicsView, cmbROIs.currentText(), imageSlider))

        graphicsView.graphicsItem.sigMaskCreated.connect(
            lambda: displayROIMeanAndStd(self, roiMeanTxt, roiStdDevTxt, graphicsView, cmbROIs, imageSlider))

        graphicsView.graphicsItem.sigMaskEdited.connect(
            lambda:replaceMask(graphicsView, cmbROIs.currentText(), imageSlider))

        graphicsView.graphicsItem.sigMaskEdited.connect(
            lambda:storeMaskData(graphicsView, cmbROIs.currentText(), imageSlider))

        graphicsView.sigContextMenuDisplayed.connect(lambda:setButtonsToDefaultStyle(buttonList))

        graphicsView.sigReloadImage.connect(lambda:reloadImageInNewImageItem(cmbROIs, graphicsView, 
                                            pixelValueTxt,  
                                            roiMeanTxt, roiStdDevTxt, self, buttonList, 
                                            btnDraw, btnErase, zoomSlider, 
                                    zoomLabel, imageSlider ))

        graphicsView.sigROIDeleted.connect(lambda:deleteROITidyUp(self, cmbROIs, graphicsView, 
                    pixelValueTxt,  
                roiMeanTxt, roiStdDevTxt, buttonList, btnDraw, btnErase,  
                    zoomSlider, zoomLabel, imageSlider))

        graphicsView.sigSetDrawButtonRed.connect(lambda setRed:setDrawButtonColour(setRed, btnDraw, btnErase))

        graphicsView.sigSetEraseButtonRed.connect(lambda setRed:setEraseButtonColour(setRed, btnDraw, btnErase))

        graphicsView.sigROIChanged.connect(lambda:setButtonsToDefaultStyle(buttonList))
        graphicsView.sigROIChanged.connect(lambda:updateROIName(graphicsView, cmbROIs))
        graphicsView.sigNewROI.connect(lambda newROIName:addNewROItoDropDownList(newROIName, cmbROIs))
        graphicsView.sigUpdateZoom.connect(lambda increment:updateZoomSlider(zoomSlider, zoomLabel, increment))
    except Exception as e:
            print('Error in DisplayImageDrawROI.setUpImageEventHandlers: ' + str(e))
            logger.error('Error in DisplayImageDrawROI.setUpImageEventHandlers: ' + str(e))  


def updateROIName(graphicsView, cmbROIs):
    logger.info("DisplayImageDrawROI.updateROIName called.")
    graphicsView.currentROIName = cmbROIs.currentText()


def displayImageDataUnderMouse(mouseOverImage, graphicsView, pixelValueTxt, imageSlider=None):
        logger.info("DisplayImageDrawROI.displayImageDataUnderMouse called")
        #print("mousePointerOverImage={}".format(mousePointerOverImage))
        if mouseOverImage:
            xCoord = graphicsView.graphicsItem.xMouseCoord
            yCoord = graphicsView.graphicsItem.yMouseCoord
            pixelValue = graphicsView.graphicsItem.pixelValue
            strValue = str(pixelValue)
            if imageSlider:
                imageNumber = imageSlider.value()
            else:
                imageNumber = 1
            strPosition = ' @ X:' + str(xCoord) + ', Y:' + str(yCoord) + ', Z:' + str(imageNumber)
            pixelValueTxt.setText('= ' + strValue + strPosition)
        else:
             pixelValueTxt.setText('')
       
        

def getRoiMeanAndStd(mask, pixelArray):
    logger.info("DisplayImageDrawROI.getRoiMeanAndStd called")
    mean = round(np.mean(np.extract(np.transpose(mask), pixelArray)), 3)
    std = round(np.std(np.extract(np.transpose(mask), pixelArray)), 3)
    return mean, std


def displayROIMeanAndStd(self, roiMeanTxt, roiStdDevTxt, graphicsView, cmbROIs, imageSlider=None):
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
            roiMeanTxt.setText(str(mean))
            roiStdDevTxt.setText(str(std))
        else:
            roiMeanTxt.clear()
            roiStdDevTxt.clear()
        

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
        

def imageROISliderMoved(self, subjectName, studyName, seriesName, 
                        imageList, imageSlider,
                        lblImageMissing, pixelValueTxt,  
                        roiMeanTxt, roiStdDevTxt,
                        cmbROIs,  btnDraw, btnErase,
                        spinBoxIntensity, spinBoxContrast,  
                        graphicsView, subWindow, 
                        buttonList, zoomSlider, 
                        zoomLabel, imageNumberLabel):
        """On the Multiple Image with ROI Display sub window, this
        function is called when the image slider is moved. 
        It causes the next image in imageList to be displayed"""
        try:
            logger.info("DisplayImageDrawROI.imageROISliderMoved called")
            imageNumber = imageSlider.value()
            currentImageNumber = imageNumber - 1
            if currentImageNumber >= 0:
                maxNumberImages = str(len(imageList))
                imageNumberString = "image {} of {}".format(imageNumber, maxNumberImages)
                imageNumberLabel.setText(imageNumberString)
                self.selectedImagePath = imageList[currentImageNumber]
                #print("imageSliderMoved before={}".format(self.selectedImagePath))
                pixelArray = readDICOM_Image.returnPixelArray(self.selectedImagePath)
                setButtonsToDefaultStyle(buttonList)
                if pixelArray is None:
                    lblImageMissing.show()
                    graphicsView.setImage(np.array([[0,0,0],[0,0,0]]))
                else:
                    reloadImageInNewImageItem(cmbROIs, graphicsView, pixelValueTxt, 
                            roiMeanTxt, roiStdDevTxt, self, buttonList, 
                            btnDraw, btnErase, zoomSlider, 
                              zoomLabel, imageSlider) 

                    setInitialImageLevelValues(graphicsView, spinBoxIntensity, spinBoxContrast)

                    setUpImageEventHandlers(self, graphicsView, pixelValueTxt, 
                                roiMeanTxt, roiStdDevTxt,
                                btnDraw, btnErase,
                                cmbROIs, buttonList,
                                zoomSlider, zoomLabel,
                                imageSlider)

                subWindow.setWindowTitle(subjectName + '-' + studyName + '-' + seriesName + '-' 
                         + os.path.basename(self.selectedImagePath))
               # print("imageSliderMoved after={}".format(self.selectedImagePath))
        except Exception as e:
            print('Error in DisplayImageDrawROI.imageROISliderMoved: ' + str(e))
            logger.error('Error in DisplayImageDrawROI.imageROISliderMoved: ' + str(e))


def reloadImageInNewImageItem(cmbROIs, graphicsView, pixelValueTxt,  
                                roiMeanTxt, roiStdDevTxt, self, buttonList, 
                              btnDraw, btnErase, zoomSlider, zoomLabel,
                              imageSlider=None ):
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
        displayROIMeanAndStd(self, roiMeanTxt, roiStdDevTxt, graphicsView, cmbROIs, imageSlider)  
        setUpImageEventHandlers(self, graphicsView, pixelValueTxt, 
                                roiMeanTxt, roiStdDevTxt, 
                                btnDraw, btnErase, 
                                cmbROIs, buttonList, zoomSlider, zoomLabel, imageSlider)
    except Exception as e:
           print('Error in DisplayImageDrawROI.reloadImageInNewImageItem: ' + str(e))
           logger.error('Error in DisplayImageDrawROI.reloadImageInNewImageItem: ' + str(e))
    

def deleteROITidyUp(self, cmbROIs, graphicsView, 
              pixelValueTxt,  
              roiMeanTxt, roiStdDevTxt, buttonList, btnDraw, btnErase, zoomSlider,
              zoomLabel, imageSlider=None):
    logger.info("DisplayImageDrawROI.deleteROITidyUp called")
    
    reloadImageInNewImageItem(cmbROIs, graphicsView, 
                              pixelValueTxt, 
                               
                              roiMeanTxt, roiStdDevTxt, 
                              self, buttonList, btnDraw, btnErase, zoomSlider,
                             zoomLabel, imageSlider) 
    displayROIMeanAndStd(self, roiMeanTxt, roiStdDevTxt, graphicsView, cmbROIs, imageSlider)
    if cmbROIs.currentIndex() == 0 and cmbROIs.count() == 1: 
        cmbROIs.clear()
        cmbROIs.addItem("region1")
        cmbROIs.setCurrentIndex(0) 
        roiMeanTxt.clear()
        roiStdDevTxt.clear()
        pixelValueTxt.clear()
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
 
        
def loadROI(self, cmbROIs, graphicsView, subjectID, studyID):
    try:
        logger.info("DisplayImageDrawROI.loadROI called")
        # The following workflow is assumed:
        #   1. The user first loads a series of DICOM images
        #   2. Then the user loads the series of ROIs that are superimposed upon the images

        # Prompt Windows to select Series
        paramDict = {"Series":"listview"}
        helpMsg = "Select a Series with ROI"
        #studyID = self.selectedStudy
        study = self.objXMLReader.getStudy(subjectID, studyID)
        listSeries = [series.attrib['id'] for series in study] # if 'ROI' in series.attrib['id']]
        inputDlg = inputDialog.ParameterInputDialog(paramDict, title= "Load ROI", helpText=helpMsg, lists=[listSeries])
        listParams = inputDlg.returnListParameterValues()
        if inputDlg.closeInputDialog() == False:
            # for series ID in listParams[0]: # more than 1 ROI may be selected
            seriesID = listParams[0][0] # Temporary, only the first ROI
            imagePathList = self.objXMLReader.getImagePathList(subjectID, studyID, seriesID)
            if self.isASeriesChecked:
                targetPath = [i[3] for i in self.checkedImageList]
                #targetPath = self.imageList
            else:
                targetPath = [self.selectedImagePath]
            maskInput = readDICOM_Image.returnSeriesPixelArray(imagePathList)
            maskInput[maskInput != 0] = 1
            maskList = [] # Output Mask
            # Consider DICOM Tag SegmentSequence[:].SegmentLabel as some 3rd software do
            if hasattr(readDICOM_Image.getDicomDataset(imagePathList[0]), "ContentDescription"):
                region = readDICOM_Image.getSeriesTagValues(imagePathList, "ContentDescription")[0][0]
            else:
                region = "new_region_label"
            # Affine re-adjustment
            for index, dicomFile in enumerate(targetPath):
                messageWindow.displayMessageSubWindow(self,
                "<H4>Loading selected ROI into target image {}</H4>".format(index + 1),
                "Load ROIs")
                messageWindow.setMsgWindowProgBarMaxValue(self, len(targetPath))
                messageWindow.setMsgWindowProgBarValue(self, index + 1)
                dataset_original = readDICOM_Image.getDicomDataset(dicomFile)
                tempArray = np.zeros(np.shape(readDICOM_Image.getPixelArray(dataset_original)))
                horizontalFlag = None
                verticalFlag = None
                for maskFile in imagePathList:
                    dataset = readDICOM_Image.getDicomDataset(maskFile)
                    maskArray = readDICOM_Image.getPixelArray(dataset)
                    maskArray[maskArray != 0] = 1
                    affineResults = readDICOM_Image.mapMaskToImage(maskArray, dataset, dataset_original)
                    if affineResults:
                        try:
                            coords = zip(*affineResults)
                            tempArray[tuple(coords)] = list(np.ones(len(affineResults)).flatten())
                            #if len(np.unique([idx[0] for idx in affineResults])) == 1 and len(np.unique([idx[1] for idx in affineResults])) != 1: horizontalFlag = True
                            #if len(np.unique([idx[1] for idx in affineResults])) == 1 and len(np.unique([idx[0] for idx in affineResults])) != 1: verticalFlag = True
                        except:
                            pass
                # Will need an Enhanced MRI as example  
                #if ~hasattr(dataset_original, 'PerFrameFunctionalGroupsSequence'):
                    #if horizontalFlag == True:
                        #struct_elm = np.ones((int(dataset_original.SliceThickness / dataset.PixelSpacing[0]), 1)) # Change /2 value here
                        #tempArray = binary_dilation(tempArray, structure=struct_elm).astype(int)
                        #tempArray = binary_closing(tempArray, structure=struct_elm).astype(int)
                    #elif verticalFlag == True:
                        #struct_elm = np.ones((1, int(dataset_original.SliceThickness / dataset.PixelSpacing[1]))) # Change /2 value here
                        #tempArray = binary_dilation(tempArray, structure=struct_elm).astype(int)
                        #tempArray = binary_closing(tempArray, structure=struct_elm).astype(int)
                maskList.append(tempArray)
            messageWindow.setMsgWindowProgBarValue(self, index + 2)
            messageWindow.closeMessageSubWindow(self)

            # Faster approach - 3D and no dilation
            #maskList = np.zeros(np.shape(readDICOM_Image.returnSeriesPixelArray(targetPath)))
            #dataset_original = readDICOM_Image.getDicomDataset(targetPath)
            #dataset = readDICOM_Image.getDicomDataset(imagePathList[0])
            #affineResults = readDICOM_Image.mapMaskToImage(maskInput, dataset, dataset_original)
            #if affineResults:
                #try:
                    #coords = zip(*affineResults)
                    #maskList[tuple(coords)] = list(np.ones(len(affineResults)).flatten())
                #except:
                    #pass
            
            # First populate the ROI_Storage data structure in a loop
            for imageNumber in range(len(maskList)):
                graphicsView.dictROIs.addRegion(region, np.array(maskList[imageNumber]).astype(bool), imageNumber + 1)

            # Second populate the dropdown list of region names
            cmbROIs.blockSignals(True)
            #remove previous contents of ROI dropdown list
            cmbROIs.clear()  
            cmbROIs.addItems(graphicsView.dictROIs.getListOfRegions())
            cmbROIs.blockSignals(False)

            # Redisplay the current image to show the mask
            #mask = graphicsView.dictROIs.getMask(region, 1)
            #graphicsView.graphicsItem.reloadMask(mask)
            cmbROIs.setCurrentIndex(cmbROIs.count() - 1)
        
    except Exception as e:
            print('Error in DisplayImageDrawROI.loadROI: ' + str(e))
            logger.error('Error in DisplayImageDrawROI.loadROI: ' + str(e)) 


def saveROI(self, regionName, graphicsView):
    try:
        # Save Current ROI
        logger.info("DisplayImageDrawROI.saveROI called")
        maskList = graphicsView.dictROIs.dictMasks[regionName] # Will return a list of boolean masks
        maskList = [np.transpose(np.array(mask, dtype=np.int)) for mask in maskList] # Convert each 2D boolean to 0s and 1s
        suffix = str("_ROI_"+ regionName)
        if len(maskList) > 1:
            inputPath = [i[3] for i in self.checkedImageList]
            #inputPath = self.imageList
        else:
            inputPath = [self.selectedImagePath]
        # Saving Progress message
        messageWindow.displayMessageSubWindow(self,
            "<H4>Saving ROIs into a new DICOM Series ({} files)</H4>".format(len(inputPath)),
            "Export ROIs")
        messageWindow.setMsgWindowProgBarMaxValue(self, len(inputPath))
        (subjectID, studyID, seriesID) = self.objXMLReader.getImageParentIDs(inputPath[0])
        seriesID = str(int(self.objXMLReader.getStudy(subjectID, studyID)[-1].attrib['id'].split('_')[0]) + 1)
        seriesUID = saveDICOM_Image.generateUIDs(readDICOM_Image.getDicomDataset(inputPath[0]), seriesID)
        #outputPath = []
        #for image in inputPath:
        for index, path in enumerate(inputPath):
            #outputPath.append(saveDICOM_Image.returnFilePath(image, suffix))
            messageWindow.setMsgWindowProgBarValue(self, index)
            outputPath = saveDICOM_Image.returnFilePath(path, suffix)
            saveDICOM_Image.saveNewSingleDicomImage(outputPath, path, maskList[index], suffix, series_id=seriesID, series_uid=seriesUID, parametric_map="SEG")
            treeSeriesID = interfaceDICOMXMLFile.insertNewImageInXMLFile(self, path, outputPath, suffix)
        #saveDICOM_Image.saveDicomNewSeries(outputPath, inputPath, maskList, suffix, parametric_map="SEG") # Consider Enhanced DICOM for parametric_map
        #seriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self, inputPath, outputPath, suffix)
        messageWindow.setMsgWindowProgBarValue(self, len(inputPath))
        messageWindow.closeMessageSubWindow(self)
        treeView.refreshDICOMStudiesTreeView(self, newSeriesName=treeSeriesID)
        QMessageBox.information(self, "Export ROIs", "Image Saved")
    except Exception as e:
            print('Error in DisplayImageDrawROI.saveROI: ' + str(e))
            logger.error('Error in DisplayImageDrawROI.saveROI: ' + str(e)) 


def roiNameChanged(cmbROIs, graphicsView, newText):
    try:
        logger.info("DisplayImageDrawROI.roiNameChanged called")
        currentIndex = cmbROIs.currentIndex()
        #Prevent spaces in new ROI name
        if ' ' in newText:
            newText = newText.replace(" ", "")
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


def updateZoomSlider(zoomSlider, zoomLabel, increment):
    """This function updates the position of the slider on the image
    zoom slider and calculates the % zoom for display in the label zoomLabel.
    Although, the zoom slider widget is not displayed on the screen,
    this function is a convenient way to keep track of the current image
    zoom value"""
    try:
        logger.info("DisplayImageDrawRIO.updateZoomSlider called")
        zoomSlider.blockSignals(True)
        if increment == 0:
            zoomSlider.setValue(0)
            zoomLabel.setText("<H4>100%</H4>")
        else:
            newValue = zoomSlider.value() + increment
            newZoomValue = 100 + (newValue * 25)
            zoomLabel.setText("<H4>" + str(newZoomValue) + "%</H4>")
            if zoomSlider.value() < zoomSlider.maximum() and increment > 0:
                zoomSlider.setValue(newValue)
            elif zoomSlider.value() > zoomSlider.minimum() and increment < 0:
                zoomSlider.setValue(newValue)
        zoomSlider.blockSignals(False)
    except Exception as e:
            print('Error in DisplayImageDrawROI.updateZoomSlider: ' + str(e))
            logger.error('Error in DisplayImageDrawROI.updateZoomSlider: ' + str(e))


def setInitialImageLevelValues(graphicsView, spinBoxIntensity, spinBoxContrast):
    spinBoxIntensity.blockSignals(True)
    spinBoxIntensity.setValue(graphicsView.graphicsItem.intensity)
    spinBoxIntensity.blockSignals(False)
    spinBoxContrast.blockSignals(True)
    spinBoxContrast.setValue(graphicsView.graphicsItem.contrast)
    spinBoxContrast.blockSignals(False)


