from PyQt5 import QtCore 
from PyQt5.QtCore import  Qt
from PyQt5.QtGui import QPixmap, QIcon,  QCursor
from PyQt5.QtWidgets import (QFileDialog, QApplication,                           
                            QMessageBox, 
                            QWidget, 
                            QGridLayout, 
                            QHBoxLayout,
                            QVBoxLayout, 
                            QMdiSubWindow, 
                            QGroupBox, 
                            QDoubleSpinBox,
                            QPushButton,  
                            QLabel, 
                            QComboBox,
                            QSizePolicy,
                            QSlider, 
                            QComboBox)

import os
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import math
from scipy.stats import iqr
import External.pyqtgraph as pg 
import CoreModules.WEASEL.ReadDICOM_Image as ReadDICOM_Image
import CoreModules.WEASEL.SaveDICOM_Image as SaveDICOM_Image
import CoreModules.WEASEL.TreeView  as treeView 
import CoreModules.WEASEL.DisplayImageCommon as displayImageCommon
import CoreModules.WEASEL.MessageWindow  as messageWindow
from CoreModules.WEASEL.UserImageColourSelection import UserSelection
import CoreModules.FreeHandROI.Resources as icons

import logging
logger = logging.getLogger(__name__)

#List of colour tables supported by matplotlib
listColours = ['gray', 'cividis',  'magma', 'plasma', 'viridis', 
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
            'binary', 'gist_yarg', 'gist_gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper',
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',
            'twilight', 'twilight_shifted', 'hsv',
            'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
            'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'turbo',
            'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar', 'custom']



class ImageViewer(QMdiSubWindow):
    """description of class"""
    def __init__(self,  pointerWeasel, subjectID="subjectID", 
                 studyID="studyID", seriesID="seriesID", imageList=[1,2,3,4]): 
        super().__init__()

        self.subjectID = subjectID
        self.studyID = studyID
        self.seriesID = seriesID
        self.imageList = imageList
        self.selectedImagePath = ""
        self.imageNumber = -1
        self.colourTable = ""

        self.setWindowFlags(Qt.CustomizeWindowHint | 
                                      Qt.WindowCloseButtonHint | 
                                      Qt.WindowMinimizeButtonHint |
                                      Qt.WindowMaximizeButtonHint)
        #self.selectedImagePath = imageList[currentImageNumber]
        #        subWindow.setWindowTitle(subjectID + ' - ' + studyName + ' - '+ seriesName + ' - ' 
        #                 + os.path.basename(self.selectedImagePath))
        #self.windowTitle = subjectID + " - " + studyName + " - " + seriesName + " - " + imageName
        #self.setWindowTitle(self.windowTitle)
        height, width = pointerWeasel.getMDIAreaDimensions()
        self.setGeometry(0, 0, width, height)
        pointerWeasel.mdiArea.addSubWindow(self)
        
        self.mainVerticalLayout = QVBoxLayout()
        self.widget = QWidget()
        self.widget.setLayout(self.mainVerticalLayout)
        self.setWidget(self.widget)

        self.topRowMainLayout = QHBoxLayout()
        self.colourTableLayout = QHBoxLayout()
        self.colourTableLayout.setContentsMargins(0, 2, 0, 0)
        self.colourTableLayout.setSpacing(5)
        self.colourTableGroupBox = QGroupBox("Colour Table")
        self.colourTableGroupBox.setLayout(self.colourTableLayout)

        self.imageLayout = QVBoxLayout()
        self.imageLayout.setContentsMargins(0, 2, 0, 0)
        self.imageLayout.setSpacing(0)
        self.imageGroupBox = QGroupBox("Image")
        self.imageGroupBox.setLayout(self.imageLayout)

        self.imageLevelsLayout= QHBoxLayout()
        self.imageLevelsLayout.setContentsMargins(0, 2, 0, 0)
        self.imageLevelsLayout.setSpacing(0)
        self.imageLevelsGroupBox = QGroupBox()
        self.imageLevelsGroupBox.setLayout(self.imageLevelsLayout)

        self.topRowMainLayout.addWidget(self.colourTableGroupBox)
        self.topRowMainLayout.addWidget(self.imageGroupBox)
        self.topRowMainLayout.addWidget(self.imageLevelsGroupBox)
        
        self.mainVerticalLayout.addLayout(self.topRowMainLayout)

        self.lblImageMissing = QLabel("<h4>Image Missing</h4>")
        self.lblImageMissing.hide()
        self.mainVerticalLayout.addWidget(self.lblImageMissing)

        self.graphicsViewLayout = pg.GraphicsLayoutWidget()
        self.plotItem = self.graphicsViewLayout.addPlot() 
        self.plotItem.getViewBox().setAspectLocked() 
        self.imgItem = pg.ImageItem(border='w')   
        self.graphicsView = pg.ImageView(view=self.plotItem, imageItem=self.imgItem)
        self.mainVerticalLayout.addWidget(self.graphicsView)

        self.imageDataLayout = QHBoxLayout()
        self.imageDataLayout.setContentsMargins(0, 0, 0, 0)
        self.imageDataLayout.setSpacing(0)
        self.imageDataGroupBox = QGroupBox()
        self.imageDataGroupBox.setLayout(self.imageDataLayout)
        self.mainVerticalLayout.addWidget(self.imageDataGroupBox)
        
        self.sliderLayout = QGridLayout()
        self.addSliderButtonLayout = QHBoxLayout()
        self.mainVerticalLayout.addLayout(self.sliderLayout)
        self.addSliderButton = QPushButton("Add Slider")
        self.addSliderButton.clicked.connect(self.addSlider)
        self.addSliderButtonLayout.addWidget(self.addSliderButton)
        self.addSliderButtonLayout.addStretch(1)
        self.mainVerticalLayout.addLayout(self.addSliderButtonLayout)

        self.deleteButton = QPushButton()
        self.deleteButton.setToolTip(
            'Deletes the DICOM image being viewed')
        self.deleteButton.setIcon(QIcon(QPixmap(icons.DELETE_ICON)))
        self.imageLayout.addWidget(self.deleteButton)

        
        self.spinBoxIntensity, self.spinBoxContrast = displayImageCommon.setUpLevelsSpinBoxes(self.imageLevelsLayout)

        self.spinBoxIntensity.valueChanged.connect(self.updateImageLevels)
        self.spinBoxContrast.valueChanged.connect(self.updateImageLevels)
            
        #if not singleImageSelected: #series selected
        #self.spinBoxIntensity.valueChanged.connect(lambda: updateImageUserSelection(
        #                                        self,  applyButton, cmbColours,
        #                                        self.spinBoxIntensity, self.spinBoxContrast,
        #                                        lblHiddenSeriesName.text(),
        #                                        lblHiddenImagePath.text()))
        #self.spinBoxContrast.valueChanged.connect(lambda: updateImageUserSelection(
        #                                        self,  applyButton, cmbColours,
        #                                        self.spinBoxIntensity, self.spinBoxContrast,
        #                                        lblHiddenSeriesName.text(),
        #                                        lblHiddenImagePath.text()))
    
    
        self.histogramObject = self.graphicsView.getHistogramWidget().getHistogram()
        self.histogramObject.sigLevelsChanged.connect(self.getHistogramLevels)
        self.graphicsView.ui.roiBtn.hide()
        self.graphicsView.ui.menuBtn.hide()

        self.mainImageSlider = self.createImageSlider()

        self.lblPixel = QLabel("<h4>Pixel Value:</h4>")
        self.imageDataLayout.addWidget(self.lblPixel)
        self.lblPixelValue = QLabel()
        self.lblPixelValue.setStyleSheet("color : red; padding-left:0; margin-left:0;")
        self.imageDataLayout.addWidget(self.lblPixelValue)
        self.imageDataLayout.addStretch(50)
        
        self.btnApply = QPushButton() 
        self.btnApply.setCheckable(True)
        self.btnApply.setIcon(QIcon(QPixmap(icons.APPLY_SERIES_ICON)))
        self.btnApply.setToolTip(
                    "Click to apply colour table and levels selected by the user to the whole series")
            
        #self.btnApply.clicked.connect(lambda:applyColourTableToSeries(self, btnApply, graphicsView, 
                    #                                                     cmbColours, 
                   #                                                     lblHiddenSeriesName.text()
                  #  #))
        self.cmbColours = QComboBox()                                                    
        self.cmbColours.blockSignals(True)
        self.cmbColours.addItems(listColours)
        self.cmbColours.setCurrentIndex(0)
        self.cmbColours.blockSignals(False)
        self.cmbColours.setToolTip('Select a colour table to apply to the image')
        self.colourTableLayout.addWidget(self.cmbColours)

        self.btnUpdate = QPushButton() 
        self.btnUpdate.setIcon(QIcon(QPixmap(icons.SAVE_ICON)))
        self.btnUpdate.setToolTip('Update DICOM with the new colour table, contrast & intensity levels')
        ##For the update button, connect signal to slot
        #if singleImageSelected:
        #    cmbColours.currentIndexChanged.connect(lambda:
        #                applyColourTableToAnImage(cmbColours, graphicsView))
        #    #Viewing and potentially updating a single DICOM images
        #    btnUpdate.clicked.connect(lambda:updateDICOM(self, 
        #                                    lblHiddenImagePath,
        #                                    lblHiddenSeriesName,
        #                                    lblHiddenStudyName, lblHiddenSubjectID,
        #                                    cmbColours,
        #                                        spinBoxIntensity, 
        #                                        spinBoxContrast, singleImage=True))
        #else:
        #    #Viewing and potentially updating a series of DICOM images
        #    cmbColours.currentIndexChanged.connect(lambda:
        #            applyColourTableToSeries(self, btnApply,  graphicsView, cmbColours, lblHiddenSeriesName.text()))
        #    btnUpdate.clicked.connect(lambda:updateDICOM(self, 
        #                                                    lblHiddenImagePath,
        #                                                    lblHiddenSeriesName,
        #                                                    lblHiddenStudyName, lblHiddenSubjectID,
        #                                                    cmbColours,
        #                                                        spinBoxIntensity, 
        #                                                        spinBoxContrast))
            
  
        self.btnExport = QPushButton() 
        self.btnExport.setIcon(QIcon(QPixmap(icons.EXPORT_ICON)))
        self.btnExport.setToolTip('Exports the image to an external graphic file.')
        #self.btnExport.clicked.connect(lambda:exportImage(self,  graphicsView, cmbColours))
        self.btnReset = QPushButton() 
        self.btnReset.setIcon(QIcon(QPixmap(icons.RESET_ICON)))
        self.btnReset.setToolTip('Return to colour tables and levels in the DICOM file')
            
        #if singleImageSelected: #series selected
        #    self.colourTableLayout.addWidget(btnReset)
        #    self.colourTableLayout.addWidget(btnUpdate)
        #    self.colourTableLayout.addWidget(btnExport)
        #    #self.colourTableLayoutbtnReset.clicked.connect(lambda: displayOneImage(self, lblImageMissing, lblPixelValue,
        #      #          spinBoxIntensity, spinBoxContrast,
        #       #         graphicsView, cmbColours, lblHiddenSeriesName.text(), lblHiddenImagePath.text()))                                                     
        #else:
        #Viewing a DICOM series, so show the Reset button
        #and Apply to Series checkbox
        self.colourTableLayout.addWidget(self.btnApply)
                
        #Clicking Reset button deletes user selected colour table and contrast 
        #and intensity levelts and returns images to values in the original DICOM file.
        #self.colourTableLayout.clicked.connect(lambda: clearUserSelection(self, imageSlider,
         #                                                   lblHiddenSeriesName.text()))
        self.colourTableLayout.addWidget(self.btnReset)
        self.colourTableLayout.addWidget(self.btnUpdate)
        self.colourTableLayout.addWidget(self.btnExport)
            #    cmbColours.activated.connect(lambda:
            #            updateImageUserSelection(self,  btnApply, cmbColours,
            #                                          spinBoxIntensity, spinBoxContrast,
            #                                          lblHiddenSeriesName.text(),
            #                                          lblHiddenImagePath.text()))
                

            #cmbColours = setUpColourTools(self, colourTableLayout, graphicsView, False,  
            #                                    lblHiddenImagePath, lblHiddenSeriesName, 
            #                                    lblHiddenStudyName, lblHiddenSubjectID,
            #                                    spinBoxIntensity, spinBoxContrast, btnApply, cmbColours, 
            #                                    lblImageMissing, lblPixelValue, mainImageSlider)

        sliderPosition=1   ####delete later
        maxNumberImages = len(self.imageList)
        self.mainImageSlider.setMaximum(maxNumberImages)
        if maxNumberImages < 4:
            self.mainImageSlider.setFixedWidth(self.width()*.2)
        elif maxNumberImages > 3 and maxNumberImages < 11:
            self.mainImageSlider.setFixedWidth(self.width()*.5)
        else:
            self.mainImageSlider.setFixedWidth(self.width()*.85)
        if sliderPosition == -1:
            self.mainImageSlider.setValue(1)
        else:
            self.mainImageSlider.setValue(sliderPosition)
        self.imageNumberLabel = QLabel()

        self.mainImageSlider.valueChanged.connect(
                  lambda: imageSliderMoved(self, subjectID, studyName, seriesName, 
                                                imageList, 
                                                mainImageSlider.value(),
                                                
                                               
                                                deleteButton,
                                                 graphicsView, 
                                                spinBoxIntensity, spinBoxContrast,
                                                cmbColours, imageNumberLabel,
                                                subWindow))
           
            #Display the first image in the viewer
        self.imageSliderMoved(self, subjectID, studyName, seriesName, 
                                  imageList,
                                  mainImageSlider.value(),
                                  
                                  deleteButton,
                                   graphicsView, 
                                  spinBoxIntensity, spinBoxContrast,
                                  cmbColours, imageNumberLabel,
                                  subWindow)
        
        self.show()


    def addSlider(self):
        rowNumber = self.sliderLayout.rowCount()
        imageTypeList = self.createImageTypeList()
        imageSlider = self.createImageSlider()
        deleteSliderButton = QPushButton("Delete")
        deleteSliderButton.clicked.connect(lambda: 
             self.deleteSlider(rowNumber, self.sliderLayout))
        self.sliderLayout.addWidget(imageTypeList, rowNumber, 0)
        self.sliderLayout.addWidget(imageSlider, rowNumber, 1)
        self.sliderLayout.addWidget(deleteSliderButton, rowNumber, 2)


    def deleteSlider(self, rowNumber):
        for colNumber in range(0, self.sliderLayout.columnCount()):
            widgetItem = self.sliderLayout.itemAtPosition(rowNumber, colNumber)
            self.sliderLayout.removeItem(widgetItem)
            widgetItem.widget().deleteLater()


    def createImageSlider(self):
        imageSlider = QSlider(Qt.Horizontal)
        imageSlider.setFocusPolicy(Qt.StrongFocus) # This makes the slider work with arrow keys on Mac OS
        imageSlider.setToolTip("Use this slider to navigate the series of DICOM images")
        imageSlider.setSingleStep(1)
        imageSlider.setTickPosition(QSlider.TicksBothSides)
        imageSlider.setTickInterval(1)
        imageSlider.setMinimum(1)
        return imageSlider


    def createImageTypeList(self):
        imageTypeList = QComboBox()
        #imageTypeList.setStyleSheet (
         #   "QComboBox::down-arrow {border-width: 0px;}")
        #imageTypeList.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        imageTypeList.setFixedWidth(900)
        imageTypeList.addItems(displayImageCommon.listImageTypes)
        imageTypeList.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        imageTypeList.currentIndexChanged.connect(lambda listIndex: getSubsetImages(listIndex))
        return imageTypeList

    
    def updateImageLevels(self):
        """When the contrast and intensity values are adjusted using the spinboxes, 
        this function sets the corresponding values in the image being viewed. 
    
        Input Parmeters
        ***************
            self - an object reference to the WEASEL interface.
             graphicsView - pyqtGraph imageView widget
            spinBoxIntensity - name of the spinbox widget that displays/sets image intensity.
            spinBoxContrast - name of the spinbox widget that displays/sets image contrast.
        """
        try:
            centre = self.spinBoxIntensity.value()
            width = self.spinBoxContrast.value()
            halfWidth = width/2

            minimumValue = centre - halfWidth
            maximumValue = centre + halfWidth
            #print("centre{}, width{},  minimumValue{}, maximumValue{}".format(centre, width,  minimumValue, maximumValue))
            self.graphicsView.setLevels( minimumValue, maximumValue)
            self.graphicsView.show()
        except Exception as e:
            print('Error in DisplayImageColour.updateImageLevels: ' + str(e))
            logger.error('Error in DisplayImageColour.updateImageLevels: ' + str(e))


    def getHistogramLevels(self):
        """
        This function determines contrast and intensity from the image
        and set the contrast & intensity spinboxes to these values.

        Input Parameters
        *****************
            graphicsView - pyqtGraph imageView widget
        spinBoxIntensity - name of the spinbox widget that displays/sets image intensity.
        spinBoxContrast - name of the spinbox widget that displays/sets image contrast.
        """
        minLevel, maxLevel =  self.graphicsView.getLevels()
        width = maxLevel - minLevel
        centre = minLevel + (width/2)
        self.spinBoxIntensity.setValue(centre)
        self.spinBoxContrast.setValue(width)


    def imageSliderMoved(self, 
                        
                        deleteButton,  graphicsView, 
                        spinBoxIntensity, spinBoxContrast,
                        cmbColours, imageNumberLabel,
                        subWindow):

        """On the Multiple Image Display sub window, this
        function is called when the image slider is moved. 
        It causes the next image in imageList to be displayed
        
        self - object reference to the WEASEL GUI
        seriesName - string variable containing the name of DICOM series of images to be displayed
        lblImageMissing - Label widget that displays the text 'Missing Image'
        lblPixelValue - Label widget that displays the value of the pixel under the mouse pointer
                and the X,Y coordinates of the mouse pointer.
        graphicsView - pyqtGraph imageView widget
        imageList - list of image file paths of the images in the series to be displayed
        spinBoxIntensity - name of the spinbox widget that displays/sets image intensity.
        spinBoxContrast - name of the spinbox widget that displays/sets image contrast.
        cmbColours - A dropdown list of colour table names based on the QComboBox class
        subWindow - object reference to the subwindow hosting the slider control
        """

        try:
            global userSelectionDict
            obj = userSelectionDict[seriesName]
            logger.info("ImageViewer.imageSliderMoved called")
            self.imageNumber = self.mainImageSlider.value()
            currentImageNumber = self.imageNumber - 1
            if currentImageNumber >= 0:
                maxNumberImages = str(len(self.imageList))
                imageNumberString = "image {} of {}".format(self.imageNumber, maxNumberImages)
                self.imageNumberLabel.setText(imageNumberString)
                self.selectedImagePath = self.imageList[currentImageNumber]
                #print("imageSliderMoved before={}".format(self.selectedImagePath))
                self.pixelArray = ReadDICOM_Image.returnPixelArray(self.selectedImagePath)
                lut = None
                #Get colour table of the image to be displayed
                if obj.getSeriesUpdateStatus():
                    self.colourTable = self.cmbColours.currentText()
                elif obj.getImageUpdateStatus():
                    self.colourTable, _, _ = obj.returnUserSelection(currentImageNumber)  
                    if self.colourTable == 'default':
                        self.colourTable, lut = ReadDICOM_Image.getColourmap(self.selectedImagePath)
                    #print('apply User Selection, colour table {}, image number {}'.format(colourTable,currentImageNumber ))
                else:
                    self.colourTable, lut = ReadDICOM_Image.getColourmap(self.selectedImagePath)

                #display above colour table in colour table dropdown list
                self.displayColourTableInComboBox()

                self.displayPixelArray(self, pixelArray, currentImageNumber, 
                                       
                                       
                                       spinBoxIntensity, spinBoxContrast,
                                        graphicsView, colourTable,
                                       cmbColours, seriesName,
                                       lut,
                                       multiImage=True,  
                                       deleteButton=deleteButton) 
                self.selectedImagePath = imageList[currentImageNumber]
                subWindow.setWindowTitle(self.subjectID + ' - ' + self.studyName + ' - '+ self.seriesName + ' - ' 
                         + os.path.basename(self.selectedImagePath))
        except TypeError as e: 
            print('Type Error in DisplayImageColour.imageSliderMoved: ' + str(e))
            logger.error('Type Error in DisplayImageColour.imageSliderMoved: ' + str(e))
        except Exception as e:
            print('Error in DisplayImageColour.imageSliderMoved: ' + str(e))
            logger.error('Error in DisplayImageColour.imageSliderMoved: ' + str(e))


    def displayColourTableInComboBox(self):
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
            self.cmbColours.blockSignals(True)
            index = self.cmbColours.findText(self.colourTable)
            if index >= 0:
                self.cmbColours.setCurrentIndex(index)
            self.cmbColours.blockSignals(False)
        except Exception as e:
                print('Error in DisplayImageColour.displayColourTableInComboBox: ' + str(e))
                logger.error('Error in DisplayImageColour.displayColourTableInComboBox: ' + str(e))


    def displayPixelArray(self, currentImageNumber,
                              lblImageMissing, lblPixelValue,
                              spinBoxIntensity, spinBoxContrast,
                               graphicsView, colourTable, cmbColours, 
                              seriesName,
                              lut=None,
                              multiImage=False, deleteButton=None):
            """Displays the an image's pixel array in a pyqtGraph imageView widget 
            & sets its colour table, contrast and intensity levels. 
            Also, sets the contrast and intensity in the associated histogram.
        
            Input Parmeters
            ***************
            self - an object reference to the WEASEL interface.
            pixelArray - pixel array to be displayed in  graphicsView
            currentImageNumber - ordinal number of the image to be displayed
                    in the list of images forming the series.
            lblImageMissing - Label widget that displays the text 'Missing Image'
            lblPixelValue - Label widget that displays the value of the pixel under the mouse pointer
                    and the X,Y coordinates of the mouse pointer.
            spinBoxIntensity - name of the spinbox widget that displays/sets image intensity.
            spinBoxContrast - name of the spinbox widget that displays/sets image contrast.
             graphicsView - pyqtGraph imageView widget
            colourTable - String variable containing the name of a colour table
            cmbColours - Name of the dropdown list of colour table names
            seriesName - string variable containing the name of DICOM series 
                of images to be displayed
            lut - array holding a lookup table of colours. A custom colour map
            multiImage - optional boolean variable, default False,
                        set to True if a series of DICOM images is being viewed.
            deleteButton - name of the button widget, which when 
                    clicked causes an image to be deleted
            """

            try:
                logger.info("DisplayImageColour.displayPixelArray called")

                #Check that pixel array holds an image & display it
                if self.pixelArray is None:
                    #the image is missing, so show a black screen
                    self.lblImageMissing.show()
                    self.deleteButton.hide()
                    self.graphicsView.setImage(np.array([[0,0,0],[0,0,0]]))  
                else:
                    if multiImage: #series
                        centre = self.spinBoxIntensity.value()
                        width = self.spinBoxContrast.value()
                        success, minimumValue, maximumValue = returnUserSelectedLevels(seriesName, 
                                                                                   centre, 
                                                                                   width, 
                                                                                   currentImageNumber)
                        if not success:
                            centre, width, maximumValue, minimumValue = readLevelsFromDICOMImage(self, self.pixelArray)

                    else:  #single image 
                        centre, width, maximumValue, minimumValue = readLevelsFromDICOMImage(self, self.pixelArray)

                    self.blockLevelsSpinBoxSignals(True)
                    self.spinBoxIntensity.setValue(centre)
                    self.spinBoxContrast.setValue(width)
                    self.blockLevelsSpinBoxSignals(False)
                    self.histogramObject.blockSignal(True)
                    if len(np.shape(self.pixelArray)) < 3:
                         self.graphicsView.setImage(self.pixelArray, 
                                                    autoHistogramRange=True, 
                                                    levels=(minimumValue, maximumValue))
                    else:
                         self.graphicsView.setImage(self.pixelArray, 
                                                    autoHistogramRange=True, 
                                                    xvals=np.arange(np.shape(pixelArray)[0] + 1), 
                                                    levels=(minimumValue, maximumValue))
                
                    #spinBoxStep = int(0.01 * iqr(pixelArray, rng=(25, 75)))
                    if (minimumValue < 1 and minimumValue > -1) and (maximumValue < 1 and maximumValue > -1):
                        spinBoxStep = float((maximumValue - minimumValue) / 200) # It takes 100 clicks to walk through the middle 50% of the signal range
                    else:
                        spinBoxStep = int((maximumValue - minimumValue) / 200) # It takes 100 clicks to walk through the middle 50% of the signal range
                    #print(spinBoxStep)
                    self.spinBoxIntensity.setSingleStep(spinBoxStep)
                    self.spinBoxContrast.setSingleStep(spinBoxStep)

                    self.histogramObject.blockSignal(False)
        
                    #Add Colour Table or look up table To Image
                    self.setPgColourMap()

                    self.lblImageMissing.hide()   
  
                    self.graphicsView.getView().scene().sigMouseMoved.connect(
                       lambda pos: getPixelValue(pos,  graphicsView, pixelArray, lblPixelValue, currentImageNumber+1))

            except Exception as e:
                print('Error in DisplayImageColour.displayPixelArray: ' + str(e))
                logger.error('Error in DisplayImageColour.displayPixelArray: ' + str(e))


    def blockLevelsSpinBoxSignals(self, block):
        """ 
        Toggles (off/on) blocking the signals from the spinboxes associated 
        with input of intensity and contrast values. 
        Input Parmeters
        ***************
            spinBoxIntensity - name of the spinbox widget that displays/sets image intensity.
            spinBoxContrast - name of the spinbox widget that displays/sets image contrast.
            block - boolean taking values True/False
        """
        self.spinBoxIntensity.blockSignals(block)
        self.spinBoxContrast.blockSignals(block)


    def setPgColourMap(self):
        """This function converts a matplotlib colour map into
        a colour map that can be used by the pyqtGraph imageView widget.
    
        Input Parmeters
        ***************
            colourTable - name of the colour map
             graphicsView - name of the imageView widget
            cmbColours - name of the dropdown lists of colour map names
            lut - name of the look up table containing raw colour data
        """

        try:
            if self.colourTable == None:
                self.colourTable = 'gray'

            if self.cmbColours:
                self.displayColourTableInComboBox()   
        
            if self.colourTable == 'custom':
                colors = lut
            elif self.colourTable == 'gray':
                colors = [[0.0, 0.0, 0.0, 1.0], [1.0, 1.0, 1.0, 1.0]]
            else:
                cmMap = cm.get_cmap(self.colourTable)
                colourClassName = cmMap.__class__.__name__
                if colourClassName == 'ListedColormap':
                    colors = cmMap.colors
                elif colourClassName == 'LinearSegmentedColormap':
                    colors = cmMap(np.linspace(0, 1))
          
            positions = np.linspace(0, 1, len(colors))
            pgMap = pg.ColorMap(positions, colors)
            self.graphicsView.setColorMap(pgMap)        
        except Exception as e:
            print('Error in DisplayImageColour.setPgColourMap: ' + str(e))
            logger.error('Error in DisplayImageColour.setPgColourMap: ' + str(e))