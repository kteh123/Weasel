"""This module contains functions for the display of a single DICOM image
or a series of DICOM images in an MDI subwindow that includes functionality
for the selecting and applying a colour table to the image/image series and
adjusting the contrast and intensity of the image/image series.  
It is possible to update the DICOM image/image series with the new 
colour table, contrast & intensity values."""

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
from CoreModules.WEASEL.UserImageColourSelection_Original import UserSelection
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

#Global variable for this module
#When several DICOM series of images are open at the the same time 
#in WEASEL, the user may wish to switch between the various subwindows
#updating the colour table, intensity and contrast levels of one or more
#images in each series. This dictionary supports this by linking series 
#name (key) to a list of sublists, userSelectionList (value), where each sublist 
#        represents an image thus:
#            [0] - Image name (used as key to search the list of sublists for a particular image)
#            [1] - colour table name
#            [2] - intensity level
#            [3] - contrast level
# userSelectionList is initialised with default values in the function displayMultiImageSubWindow
#The class UserSelection in UserImageColourSelection supplies the functionality
#to manipulate userSelectionList. 
userSelectionDict = {}

def displayManySingleImageSubWindows(self):
    try:
        logger.info("DisplayImageColour.displayManySingleImageSubWindows")
        if len(self.checkedImageList)>0: 
            for image in self.checkedImageList:
                studyName = image[0]
                seriesName = image[1]
                imagePath = image[2]
                subjectID = image[3]
                displayImageSubWindow(self, imagePath, subjectID, seriesName, studyName)
    except Exception as e:
        print('Error in DisplayImageColour.displayManySingleImageSubWindows: ' + str(e))
        logger.error('Error in DisplayImageColour.displayManySingleImageSubWindows: ' + str(e))


def displayManyMultiImageSubWindows(self):
    try:
        logger.info("DisplayImageColour.displayManyMultiImageSubWindows")
        if len(self.checkedSeriesList)>0: 
            for series in self.checkedSeriesList:
                subjectID = series[0]
                studyName = series[1]
                seriesName = series[2]
                imageList = treeView.returnSeriesImageList(self, subjectID, studyName, seriesName)
                displayMultiImageSubWindow(self, imageList, subjectID, studyName, 
                         seriesName, sliderPosition = -1)
    except Exception as e:
        print('Error in DisplayImageColour.displayManyMultiImageSubWindows: ' + str(e))
        logger.error('Error in DisplayImageColour.displayManyMultiImageSubWindows: ' + str(e))


def displayImageFromTreeView(self, item, col):
    #only display an image if the series or image name in column 1
    #(second column) of the tree view is double clicked.
    try:
        logger.info("DisplayImageColour.displayImageFromTreeView")
        if col == 1:
            #Has an image or a series been double-clicked?
            if treeView.isAnImageSelected(item):
                subjectID = item.parent().parent().parent().text(1).replace('Subject -', '').strip()
                studyName = item.parent().parent().text(1).replace('Study -', '').strip()
                seriesName = item.parent().text(1).replace('Series -', '').strip()
                imagePath = item.text(4)
                displayImageSubWindow(self, imagePath, subjectID, seriesName, studyName)
            elif treeView.isASeriesSelected(item):
                subjectID = item.parent().parent().text(1).replace('Subject -', '').strip()
                studyName = item.parent().text(1).replace('Study -', '').strip()
                seriesName = item.text(1).replace('Series -', '').strip()
                imageList = treeView.returnSeriesImageList(self, subjectID, studyName, seriesName)
                displayMultiImageSubWindow(self, imageList, subjectID, studyName, 
                         seriesName, sliderPosition = -1)
    except Exception as e:
            print('Error in DisplayImageColour.displayImageFromTreeView: ' + str(e))
            logger.error('Error in DisplayImageColour.displayImageFromTreeView: ' + str(e))


def setUpSubWindow(self, imageSeries = False):
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
        logger.info("DisplayImageColour.setUpSubWindow")
        subWindow = QMdiSubWindow(self)
        if imageSeries:
            subWindow.setObjectName = imageSeries
        else:
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
        colourTableLayout = QHBoxLayout()
        colourTableLayout.setContentsMargins(0, 2, 0, 0)
        colourTableLayout.setSpacing(5)
        colourTableGroupBox = QGroupBox("Colour Table")
        colourTableGroupBox.setLayout(colourTableLayout)

        imageLayout = QVBoxLayout()
        imageLayout.setContentsMargins(0, 2, 0, 0)
        imageLayout.setSpacing(0)
        imageGroupBox = QGroupBox("Image")
        #if not imageSeries:
        #    imageGroupBox.setVisible(False)
        imageGroupBox.setLayout(imageLayout)

        imageLevelsLayout= QHBoxLayout()
        imageLevelsLayout.setContentsMargins(0, 2, 0, 0)
        imageLevelsLayout.setSpacing(0)
        imageLevelsGroupBox = QGroupBox()
        imageLevelsGroupBox.setLayout(imageLevelsLayout)

        topRowMainLayout.addWidget(colourTableGroupBox)
        topRowMainLayout.addWidget(imageGroupBox)
        topRowMainLayout.addWidget(imageLevelsGroupBox)
        
        mainVerticalLayout.addLayout(topRowMainLayout)

        lblImageMissing = QLabel("<h4>Image Missing</h4>")
        lblImageMissing.hide()
        mainVerticalLayout.addWidget(lblImageMissing)

        graphicsViewLayout = pg.GraphicsLayoutWidget()
        plotItem = graphicsViewLayout.addPlot() 
        plotItem.getViewBox().setAspectLocked() 
        imgItem = pg.ImageItem(border='w')   
        graphicsView = pg.ImageView(view=plotItem, imageItem=imgItem)
        #mainVerticalLayout.addWidget(graphicsViewLayout)  does not work
        mainVerticalLayout.addWidget(graphicsView)

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
        return (imgItem, graphicsView, colourTableLayout, imageLayout, imageLevelsLayout, 
                imageDataLayout, graphicsViewLayout, sliderLayout, 
                lblImageMissing, subWindow)
    except Exception as e:
            print('Error in DisplayImageColour.setUpSubWindow: ' + str(e))
            logger.error('Error in DisplayImageColour.setUpSubWindow: ' + str(e))


def setUpPixelDataGroupBox(pixelDataLayout):
        lblPixel = QLabel("<h4>Pixel Value:</h4>")
        lblPixel.show()
        pixelDataLayout.addWidget(lblPixel)
        lblPixelValue = QLabel()
        lblPixelValue.show()
        lblPixelValue.setStyleSheet("color : red; padding-left:0; margin-left:0;")
        pixelDataLayout.addWidget(lblPixelValue)
        pixelDataLayout.addStretch(50)
        return  lblPixelValue


def setUpImageGroupBox(imageLayout, imagePathForDisplay, studyName, 
                       seriesName, subjectID):
    try: 
        deleteButton = QPushButton()
        deleteButton.setToolTip(
            'Deletes the DICOM image being viewed')
        deleteButton.setIcon(QIcon(QPixmap(icons.DELETE_ICON)))
        lblHiddenImagePath = QLabel(imagePathForDisplay)
        lblHiddenStudyName = QLabel(studyName)
        lblHiddenSeriesName = QLabel(seriesName)
        lblHiddenSubjectID = QLabel(subjectID)
        
        #Maintain image data in hidden labels on the subwindow.
        #These values will used when updating an image with a
        #new colour table & intensity & contrast values. This
        #is done because several of these windows may be open
        #at once and the global self.selectedImagePath maybe
        #points to an image in a window other than the one
        #the user is working on
        imageLayout.addWidget(deleteButton)
        imageLayout.addWidget(lblHiddenSeriesName)
        imageLayout.addWidget(lblHiddenStudyName)
        imageLayout.addWidget(lblHiddenImagePath)
        imageLayout.addWidget(lblHiddenSubjectID)

        lblHiddenImagePath.hide()
        lblHiddenStudyName.hide()
        lblHiddenSeriesName.hide()
        lblHiddenSubjectID.hide()
        return deleteButton, lblHiddenImagePath, lblHiddenStudyName, lblHiddenSeriesName, lblHiddenSubjectID
    except Exception as e:
        print('Error in DisplayImageColour.setUpImageGroupBox: ' + str(e))
        logger.error('Error in DisplayImageColour.setUpImageGroupBox: ' + str(e))


def displayManySingleImageSubWindows(self):
    if len(self.checkedImageList)>0: 
        for image in self.checkedImageList:
            subjectID = image[0]
            studyName = image[1]
            seriesName = image[2]
            imagePath = image[3]
            displayImageSubWindow(self, imagePath, subjectID, seriesName, studyName)


def displayManyMultiImageSubWindows(self):
    if len(self.checkedSeriesList)>0: 
        for series in self.checkedSeriesList:
            subjectID = series[0]
            studyName = series[1]
            seriesName = series[2]
            imageList = treeView.returnSeriesImageList(self, subjectID, studyName, seriesName)
            displayMultiImageSubWindow(self, imageList, subjectID, studyName, 
                     seriesName, sliderPosition = -1)


def displayImageSubWindow(self, derivedImagePath=None, subjectID=None, seriesName=None, studyName=None):
        """
        Creates a subwindow that displays a single DICOM image. 

        Input Parmeters
        ***************
        self - an object reference to the WEASEL interface.
        studyName - string variable containing name of the DICOMstudy 
                containing the DICOM series of images to be displayed
        seriesName - string variable containing the name of DICOM series of images to be displayed
        derivedImagePath - optional parameter containing the path to a
            new image created by an operation on an existing image.
        """
        try:
            logger.info("DisplayImageColour.displayImageSubWindow called")
            #self.selectedImagePath is populated when the image in the
            #tree view is clicked & selected
            print("derivedImagePath={}".format(derivedImagePath))
            if derivedImagePath:
                self.selectedImagePath = derivedImagePath

            (imgItem, graphicsView, colourTableLayout, imageLayout, imageLevelsLayout, 
                pixelDataLayout, graphicsViewLayout, sliderLayout, 
                lblImageMissing, subWindow) = setUpSubWindow(self)
            imageName = os.path.basename(self.selectedImagePath)
            windowTitle = subjectID + " - " + studyName + " - " + seriesName + " - " + imageName
            subWindow.setWindowTitle(windowTitle)
            #subWindow.setStyleSheet("background-color:#ccccff;")
            (deleteButton, lblHiddenImagePath, 
             lblHiddenStudyName, 
             lblHiddenSeriesName, 
             lblHiddenSubjectID) = setUpImageGroupBox(imageLayout, self.selectedImagePath, studyName, seriesName, subjectID)
            btnApply = QPushButton() 
            cmbColours = QComboBox()
            spinBoxIntensity, spinBoxContrast = setUpLevelsSpinBoxes(self, btnApply, cmbColours, 
                                                                     lblHiddenSeriesName, lblHiddenImagePath,
                                                                     imageLevelsLayout, graphicsView, singleImageSelected=True)
            
            lblPixelValue = setUpPixelDataGroupBox(pixelDataLayout)

            cmbColours = setUpColourTools(self, colourTableLayout, graphicsView, True,  
                                                lblHiddenImagePath, lblHiddenSeriesName, 
                                                lblHiddenStudyName, lblHiddenSubjectID,
                                                spinBoxIntensity, spinBoxContrast, btnApply, 
                                                cmbColours, lblImageMissing, lblPixelValue)

            

            displayOneImage(self, lblImageMissing, lblPixelValue,
                            spinBoxIntensity, spinBoxContrast,
                            graphicsView, cmbColours, lblHiddenSeriesName.text(), lblHiddenImagePath.text())

            
            deleteButton.clicked.connect(lambda:
                                         deleteSingleImage(self, lblHiddenImagePath.text(), 
                                      subjectID, studyName, seriesName, subWindow))

        except (IndexError, AttributeError):
                subWindow.close()
                msgBox = QMessageBox()
                msgBox.setWindowTitle("View a DICOM image")
                msgBox.setText("Select an image to view")
                msgBox.exec()
        except Exception as e:
            print('Error in DisplayImageColour.displayImageSubWindow: ' + str(e))
            logger.error('Error in  DisplayImageColour.displayImageSubWindow: ' + str(e)) 


def displayOneImage(self, lblImageMissing, lblPixelValue,
                            spinBoxIntensity, spinBoxContrast,
                            graphicsView, cmbColours, SeriesName, imagePath):
    pixelArray = ReadDICOM_Image.returnPixelArray(imagePath)
    colourTable, lut = ReadDICOM_Image.getColourmap(imagePath)
    displayPixelArray(self, pixelArray, 0,lblImageMissing,
                            lblPixelValue,
                            spinBoxIntensity, spinBoxContrast,
                            graphicsView,
                             colourTable, cmbColours, SeriesName,
                            lut) 
    displayColourTableInComboBox(cmbColours, colourTable)


def displayMultiImageSubWindow(self, imageList, subjectID, studyName, 
                     seriesName, sliderPosition = -1):
        """
        Creates a subwindow that displays all the DICOM images in a series. 
        A slider allows the user to scroll through the images.  A delete
        button allows the user to delete the image they are viewing.

        The user can either update the whole series with a new colour table 
        and contrast & intensity values  or they can update individual
        images in the series with a new colour table 
        and contrast & intensity values.

        Input Parmeters
        ***************
        self - an object reference to the WEASEL interface.
        imageList - list of image file paths of the images in the series to be displayed
        studyName - string variable containing name of the DICOMstudy 
                containing the DICOM series of images to be displayed
        seriesName - string variable containing the name of DICOM series of images to be displayed
        sliderPosition - optional integer value denoting position of the slider widget that scrolls 
            through the images in imageList.
        """
        try:
            logger.info("DisplayImageColour.displayMultiImageSubWindow called")
            (imgItem, graphicsView, colourTableLayout, imageLayout, imageLevelsLayout, 
            pixelDataLayout, graphicsViewLayout, sliderLayout, 
            lblImageMissing, subWindow) = setUpSubWindow(self, imageSeries=True)
            #subWindow.setStyleSheet("background-color:#6666ff;")

            #set up list of lists to hold user selected colour table and level data
            userSelectionList = [[os.path.basename(imageName), 'default', -1, -1]
                                for imageName in imageList]
            #add user selection object to dictionary
            global userSelectionDict
            userSelectionDict[seriesName] = UserSelection(userSelectionList)
            
            
            #file path of the first image, 
            #Study ID & Series ID are stored locally on the
            #sub window as the text in label widgets
            #in case the user wishes to delete an
            #image in the series or update an image/image series
            #with new colour table, contrast & intensity values.
            #They may have several series open at once,
            #so the selected series on the treeview
            #may not the same as that from which the image is
            #being deleted.
            firstImagePath = imageList[0]
            (deleteButton, lblHiddenImagePath, 
             lblHiddenStudyName, 
             lblHiddenSeriesName, 
             lblHiddenSubjectID) = setUpImageGroupBox(imageLayout, firstImagePath, studyName, seriesName, subjectID)

            btnApply = QPushButton() 
            cmbColours = QComboBox()
            spinBoxIntensity, spinBoxContrast = setUpLevelsSpinBoxes(self, btnApply,
                                                                     cmbColours, lblHiddenSeriesName, 
                                                                     lblHiddenImagePath,
                                                                     imageLevelsLayout, 
                                                                     graphicsView, singleImageSelected=False)
           

            imageSlider = QSlider(Qt.Horizontal)
            imageSlider.setFocusPolicy(Qt.StrongFocus) # This makes the slider work with arrow keys on Mac OS
            imageSlider.setToolTip("Use this slider to navigate the series of DICOM images")
            lblPixelValue = setUpPixelDataGroupBox(pixelDataLayout)
            cmbColours = setUpColourTools(self, colourTableLayout, graphicsView, False,  
                                                lblHiddenImagePath, lblHiddenSeriesName, 
                                                lblHiddenStudyName, lblHiddenSubjectID,
                                                spinBoxIntensity, spinBoxContrast, btnApply, cmbColours, 
                                                lblImageMissing, lblPixelValue, imageSlider)

           
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
            imageNumberLabel = QLabel()
            if maxNumberImages > 1:
                sliderLayout.addWidget(imageSlider)
            sliderLayout.addWidget(imageNumberLabel)
            if len(imageList) < 11:
                sliderLayout.addStretch(1)
            
            imageSlider.valueChanged.connect(
                  lambda: imageSliderMoved(self, subjectID, studyName, seriesName, 
                                                imageList, 
                                                imageSlider.value(),
                                                lblImageMissing,
                                                lblPixelValue,
                                                deleteButton,
                                                 graphicsView, 
                                                spinBoxIntensity, spinBoxContrast,
                                                cmbColours, imageNumberLabel,
                                                subWindow))
           
            #Display the first image in the viewer
            imageSliderMoved(self, subjectID, studyName, seriesName, 
                                  imageList,
                                  imageSlider.value(),
                                  lblImageMissing,
                                  lblPixelValue,
                                  deleteButton,
                                   graphicsView, 
                                  spinBoxIntensity, spinBoxContrast,
                                  cmbColours, imageNumberLabel,
                                  subWindow)
            
            deleteButton.clicked.connect(lambda: deleteImageInMultiImageViewer(self,
                                      self.selectedImagePath, imageList, subjectID, 
                                      lblHiddenStudyName.text(), 
                                      lblHiddenSeriesName.text(),
                                      imageSlider.value(), subWindow))

        except (IndexError, AttributeError):
                subWindow.close()
                msgBox = QMessageBox() 
                msgBox.setWindowTitle("View a DICOM series")
                msgBox.setText("Select a series to view")
                msgBox.exec()  
        except Exception as e:
            print('Error in DisplayImageColour.displayMultiImageSubWindow: ' + str(e))
            logger.error('Error in DisplayImageColour.displayMultiImageSubWindow: ' + str(e))


def setUpLevelsSpinBoxes(self, applyButton, cmbColours, lblHiddenSeriesName, lblHiddenImagePath,
                         imageLevelsLayout, graphicsView, singleImageSelected=True): 
    try:
        logger.info("DisplayImageDrawROI.setUpLevelsSpinBoxes called.")
        spinBoxIntensity, spinBoxContrast = displayImageCommon.setUpLevelsSpinBoxes(imageLevelsLayout)

        spinBoxIntensity.valueChanged.connect(lambda: updateImageLevels(self,
                graphicsView,spinBoxIntensity, spinBoxContrast))
        spinBoxContrast.valueChanged.connect(lambda: updateImageLevels(self,
        graphicsView,spinBoxIntensity, spinBoxContrast))
            
        if not singleImageSelected: #series selected
            spinBoxIntensity.valueChanged.connect(lambda: updateImageUserSelection(
                                                    self,  applyButton, cmbColours,
                                                    spinBoxIntensity, spinBoxContrast,
                                                    lblHiddenSeriesName.text(),
                                                    lblHiddenImagePath.text()))
            spinBoxContrast.valueChanged.connect(lambda: updateImageUserSelection(
                                                    self,  applyButton, cmbColours,
                                                    spinBoxIntensity, spinBoxContrast,
                                                    lblHiddenSeriesName.text(),
                                                    lblHiddenImagePath.text()))
    
    
        histogramObject = graphicsView.getHistogramWidget().getHistogram()
        histogramObject.sigLevelsChanged.connect(lambda: getHistogramLevels(graphicsView, spinBoxIntensity, spinBoxContrast))
        graphicsView.ui.roiBtn.hide()
        graphicsView.ui.menuBtn.hide() 
  
        return spinBoxIntensity, spinBoxContrast
    except Exception as e:
            print('Error in DisplayImageColour.setUpLevelsSpinBoxes: ' + str(e))
            logger.error('Error in DisplayImageColour.setUpLevelsSpinBoxes: ' + str(e))


def getHistogramLevels( graphicsView, spinBoxIntensity, spinBoxContrast):
        """
        This function determines contrast and intensity from the image
        and set the contrast & intensity spinboxes to these values.

        Input Parameters
        *****************
         graphicsView - pyqtGraph imageView widget
        spinBoxIntensity - name of the spinbox widget that displays/sets image intensity.
        spinBoxContrast - name of the spinbox widget that displays/sets image contrast.
        """
        minLevel, maxLevel =  graphicsView.getLevels()
        width = maxLevel - minLevel
        centre = minLevel + (width/2)
        spinBoxIntensity.setValue(centre)
        spinBoxContrast.setValue(width)


def setUpColourTools(self, layout,  graphicsView,
            singleImageSelected,
            lblHiddenImagePath,
            lblHiddenSeriesName,
            lblHiddenStudyName, lblHiddenSubjectID, spinBoxIntensity, spinBoxContrast,             
            btnApply, cmbColours, lblImageMissing, lblPixelValue, imageSlider = None):
        """
            Generates widgets for the display of a 
            dropdown list containing colour tables
            and spin boxes for setting image contrast and intensity.

            Input Parmeters
            ***************
            self - an object reference to the WEASEL interface.
            layout - a QVBoxLayout widget that lines up widgets vertically.
                    The parent layout on the subwindow.
             graphicsView - pyqtGraph imageView widget
            singleImageSelected - boolean variable, set to True if a 
                    single image is being viewed. Otherwise set to False
            lblHiddenImagePath - name of the hidden label widget whose text
                    contains the path to an image file.applyColourTableToSeries
            lblHiddenSeriesName - name of the hidden label widget whose text
                    contains the name of the DICOM series whose images are 
                    being viewed.
            lblHiddenStudyName - name of the hidden label widget whose text
                    contains the name of the DICOM study containing the series
                    whose images are  being viewed.
            spinBoxIntensity - name of the spinbox widget that displays/sets image intensity.
            spinBoxContrast - name of the spinbox widget that displays/sets image contrast.
            imageSlider - name of the slider widget used to scroll through the images.

        Output Parameters
        *****************
            cmbColours - A dropdown list of colour table names based on the QComboBox class
        """
        try:
            logger.info("displayImageColour.setUpColourTools called")

            #When this checkbox is checked, the selected colour table, 
            #contrast and intensity levels are added to the whole series
            btnApply.setCheckable(True)
            btnApply.setIcon(QIcon(QPixmap(icons.APPLY_SERIES_ICON)))
            btnApply.setToolTip(
                    "Click to apply colour table and levels selected by the user to the whole series")
            
            btnApply.clicked.connect(lambda:applyColourTableToSeries(self, btnApply, graphicsView, 
                                                                         cmbColours, 
                                                                        lblHiddenSeriesName.text()
                                                                        ))
            cmbColours.blockSignals(True)
            cmbColours.addItems(listColours)
            cmbColours.setCurrentIndex(0)
            cmbColours.blockSignals(False)
            cmbColours.setToolTip('Select a colour table to apply to the image')
           
            layout.addWidget(cmbColours)

            btnUpdate = QPushButton() 
            btnUpdate.setIcon(QIcon(QPixmap(icons.SAVE_ICON)))
            btnUpdate.setToolTip('Update DICOM with the new colour table, contrast & intensity levels')
            #For the update button, connect signal to slot
            if singleImageSelected:
                cmbColours.currentIndexChanged.connect(lambda:
                         applyColourTableToAnImage(cmbColours, graphicsView))
                #Viewing and potentially updating a single DICOM images
                btnUpdate.clicked.connect(lambda:updateDICOM(self, 
                                                lblHiddenImagePath,
                                                lblHiddenSeriesName,
                                                lblHiddenStudyName, lblHiddenSubjectID,
                                                cmbColours,
                                                    spinBoxIntensity, 
                                                    spinBoxContrast, singleImage=True))
            else:
                #Viewing and potentially updating a series of DICOM images
                cmbColours.currentIndexChanged.connect(lambda:
                        applyColourTableToSeries(self, btnApply,  graphicsView, cmbColours, lblHiddenSeriesName.text()))
                btnUpdate.clicked.connect(lambda:updateDICOM(self, 
                                                                lblHiddenImagePath,
                                                                lblHiddenSeriesName,
                                                                lblHiddenStudyName, lblHiddenSubjectID,
                                                                cmbColours,
                                                                    spinBoxIntensity, 
                                                                    spinBoxContrast))
            
  
            btnExport = QPushButton() 
            btnExport.setIcon(QIcon(QPixmap(icons.EXPORT_ICON)))
            btnExport.setToolTip('Exports the image to an external graphic file.')
            btnExport.clicked.connect(lambda:exportImage(self,  graphicsView, cmbColours))
            btnReset = QPushButton() 
            btnReset.setIcon(QIcon(QPixmap(icons.RESET_ICON)))
            btnReset.setToolTip('Return to colour tables and levels in the DICOM file')
            
            if singleImageSelected: #series selected
                layout.addWidget(btnReset)
                layout.addWidget(btnUpdate)
                layout.addWidget(btnExport)
                btnReset.clicked.connect(lambda: displayOneImage(self, lblImageMissing, lblPixelValue,
                            spinBoxIntensity, spinBoxContrast,
                            graphicsView, cmbColours, lblHiddenSeriesName.text(), lblHiddenImagePath.text()))                                                     
            else:
                #Viewing a DICOM series, so show the Reset button
                #and Apply to Series checkbox
                layout.addWidget(btnApply)
                
                #Clicking Reset button deletes user selected colour table and contrast 
                #and intensity levelts and returns images to values in the original DICOM file.
                btnReset.clicked.connect(lambda: clearUserSelection(self, imageSlider,
                                                                   lblHiddenSeriesName.text()))
                layout.addWidget(btnReset)
                layout.addWidget(btnUpdate)
                layout.addWidget(btnExport)
                cmbColours.activated.connect(lambda:
                        updateImageUserSelection(self,  btnApply, cmbColours,
                                                      spinBoxIntensity, spinBoxContrast,
                                                      lblHiddenSeriesName.text(),
                                                      lblHiddenImagePath.text()))
                

            return cmbColours
        except Exception as e:
            print('Error in displayImageColour.setUpColourTools: ' + str(e))
            logger.error('Error in displayImageColour.setUpColourTools: ' + str(e))


def displayPixelArray(self, pixelArray, currentImageNumber,
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
            if pixelArray is None:
                #the image is missing, so show a black screen
                lblImageMissing.show()
                deleteButton.hide()
                graphicsView.setImage(np.array([[0,0,0],[0,0,0]]))  
            else:
                if multiImage: #series
                    centre = spinBoxIntensity.value()
                    width = spinBoxContrast.value()
                    success, minimumValue, maximumValue = returnUserSelectedLevels(seriesName, 
                                                                               centre, 
                                                                               width, 
                                                                               currentImageNumber)
                    if not success:
                        centre, width, maximumValue, minimumValue = readLevelsFromDICOMImage(self, pixelArray)

                else:  #single image 
                    centre, width, maximumValue, minimumValue = readLevelsFromDICOMImage(self, pixelArray)

                blockLevelsSpinBoxSignals(spinBoxIntensity, spinBoxContrast, True)
                spinBoxIntensity.setValue(centre)
                spinBoxContrast.setValue(width)
                blockLevelsSpinBoxSignals(spinBoxIntensity, spinBoxContrast, False)
                blockHistogramSignals( graphicsView, True)
                if len(np.shape(pixelArray)) < 3:
                     graphicsView.setImage(pixelArray, autoHistogramRange=True, levels=(minimumValue, maximumValue))
                else:
                     graphicsView.setImage(pixelArray, autoHistogramRange=True, xvals=np.arange(np.shape(pixelArray)[0] + 1), levels=(minimumValue, maximumValue))
                
                #spinBoxStep = int(0.01 * iqr(pixelArray, rng=(25, 75)))
                if (minimumValue < 1 and minimumValue > -1) and (maximumValue < 1 and maximumValue > -1):
                    spinBoxStep = float((maximumValue - minimumValue) / 200) # It takes 100 clicks to walk through the middle 50% of the signal range
                else:
                    spinBoxStep = int((maximumValue - minimumValue) / 200) # It takes 100 clicks to walk through the middle 50% of the signal range
                #print(spinBoxStep)
                spinBoxIntensity.setSingleStep(spinBoxStep)
                spinBoxContrast.setSingleStep(spinBoxStep)

                blockHistogramSignals( graphicsView, False)
        
                #Add Colour Table or look up table To Image
                setPgColourMap(colourTable,  graphicsView, cmbColours, lut)

                lblImageMissing.hide()   
  
                graphicsView.getView().scene().sigMouseMoved.connect(
                   lambda pos: getPixelValue(pos,  graphicsView, pixelArray, lblPixelValue, currentImageNumber+1))

        except Exception as e:
            print('Error in DisplayImageColour.displayPixelArray: ' + str(e))
            logger.error('Error in DisplayImageColour.displayPixelArray: ' + str(e))


def returnUserSelectedLevels(seriesName, centre, width, currentImageNumber):
    """
    When the user has selected new image levels that must override the 
    levels saved in the DICOM series/image, this function returns those selected levels

    Input parameters
    ****************
    seriesName - string variable containing the name of DICOM series of images to be displayed
    centre - Image intensity
    width - Image contrast
    currentImageNumber - The ordinal number of the image being viewed in the image list

    Output parameters
    *****************
    success - boolean, set to true if level values are successfully retrieved
    maximumValue - Maximum pixel value in the image
    minimumValue - Minimum pixel value in the image
    """
    try:
        logger.info("DisplayImageColour.returnUserSelectedLevels called")
        minimumValue = -1
        maximumValue = -1
        success = False
        global userSelectionDict
        obj = userSelectionDict[seriesName]
        if obj.getSeriesUpdateStatus():
            #apply contrast and intensity values
            #selected in the GUI spinboxes
            #for the whole series to this image
            minimumValue = centre - (width/2)
            maximumValue = centre + (width/2)
            success = True
        elif obj.getImageUpdateStatus():
            #the user has opted to change the levels of individual images
            #in a series.
            #if user selected levels exist for this image, retrieve them
            _, centre, width = obj.returnUserSelection(currentImageNumber) 
            if centre != -1:
                #saved values exist, so use them
                minimumValue = centre - (width/2)
                maximumValue = centre + (width/2)
                success = True

        return success, minimumValue, maximumValue
    except Exception as e:
        print('Error in DisplayImageColour.returnUserSelectedLevels: ' + str(e))
        logger.error('Error in DisplayImageColour.returnUserSelectedLevels: ' + str(e))


def blockLevelsSpinBoxSignals(spinBoxIntensity, spinBoxContrast, block):
    """ 
    Toggles (off/on) blocking the signals from the spinboxes associated 
    with input of intensity and contrast values. 
    Input Parmeters
    ***************
        spinBoxIntensity - name of the spinbox widget that displays/sets image intensity.
        spinBoxContrast - name of the spinbox widget that displays/sets image contrast.
        block - boolean taking values True/False
    """
    spinBoxIntensity.blockSignals(block)
    spinBoxContrast.blockSignals(block)


def blockHistogramSignals(imgView, block):
        """ 
        Toggles (off/on) blocking the signals from the histogram associated 
        with image view imgView. 
        Input Parmeters
        ***************
            imgView - name of the imageView widget associated with the histogram
            block - boolean taking values True/False
        """
        histogramObject = imgView.getHistogramWidget().getHistogram()
        histogramObject.blockSignals(block)


def imageSliderMoved(self, subjectID, studyName, seriesName, 
                        imageList, imageNumber,
                        lblImageMissing, lblPixelValue, 
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
            logger.info("DisplayImageColour.imageSliderMoved called")
            currentImageNumber = imageNumber - 1
            if currentImageNumber >= 0:
                maxNumberImages = str(len(imageList))
                imageNumberString = "image {} of {}".format(imageNumber, maxNumberImages)
                imageNumberLabel.setText(imageNumberString)
                self.selectedImagePath = imageList[currentImageNumber]
                #print("imageSliderMoved before={}".format(self.selectedImagePath))
                pixelArray = ReadDICOM_Image.returnPixelArray(self.selectedImagePath)
                lut = None
                #Get colour table of the image to be displayed
                if obj.getSeriesUpdateStatus():
                    colourTable = cmbColours.currentText()
                elif obj.getImageUpdateStatus():
                    colourTable, _, _ = obj.returnUserSelection(currentImageNumber)  
                    if colourTable == 'default':
                        colourTable, lut = ReadDICOM_Image.getColourmap(self.selectedImagePath)
                    #print('apply User Selection, colour table {}, image number {}'.format(colourTable,currentImageNumber ))
                else:
                    colourTable, lut = ReadDICOM_Image.getColourmap(self.selectedImagePath)

                #display above colour table in colour table dropdown list
                displayColourTableInComboBox(cmbColours, colourTable)

                displayPixelArray(self, pixelArray, currentImageNumber, 
                                       lblImageMissing,
                                       lblPixelValue,
                                       spinBoxIntensity, spinBoxContrast,
                                        graphicsView, colourTable,
                                       cmbColours, seriesName,
                                       lut,
                                       multiImage=True,  
                                       deleteButton=deleteButton) 

                subWindow.setWindowTitle(subjectID + ' - ' + studyName + ' - '+ seriesName + ' - ' 
                         + os.path.basename(self.selectedImagePath))
        except TypeError as e: 
            print('Type Error in DisplayImageColour.imageSliderMoved: ' + str(e))
            logger.error('Type Error in DisplayImageColour.imageSliderMoved: ' + str(e))
        except Exception as e:
            print('Error in DisplayImageColour.imageSliderMoved: ' + str(e))
            logger.error('Error in DisplayImageColour.imageSliderMoved: ' + str(e))


def deleteSingleImage(self, currentImagePath, subjectID, 
                                      studyName, seriesName, subWindow):
    """When the Delete button is clicked on the single image viewer,
    this function deletes the physical image, removes the 
    reference to it in the XML file and removes it from the image viewer.
    
    Input Parmeters
    ***************
        self - an object reference to the WEASEL interface.
        currentImagePath - file path to the image being viewed.
        studyName - string variable containing name of the DICOMstudy 
                containing the DICOM series of images to be displayed
        seriesName - string variable containing the name of DICOM series
                of images to be displayed
        lastSliderPosition - integer variable holding the value of the 
                    slider when the delete button is clicked; i.e., the
                    number of the image being deleted.
    """
    try:
        logger.info("DisplayImageColour.deleteSingleImage called")
        imageName = os.path.basename(currentImagePath)
        #print ('study id {} series id {}'.format(studyName, seriesName))
        buttonReply = QMessageBox.question(self, 
            'Delete DICOM image', "You are about to delete image {}".format(imageName), 
            QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)

        if buttonReply == QMessageBox.Ok:
            #Delete physical file
            QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
            subWindow.close()
            QApplication.processEvents()
            os.remove(currentImagePath)
            #Remove deleted image from the list
            self.objXMLReader.removeOneImageFromSeries(subjectID,
                    studyName, seriesName, currentImagePath)
            QApplication.processEvents()
            #Update tree view with xml file modified above
            treeView.refreshDICOMStudiesTreeView(self)
            QApplication.restoreOverrideCursor()
    except Exception as e:
        print('Error in DisplayImageColour.deleteSingleImage: ' + str(e))
        logger.error('Error in DisplayImageColour.deleteSingleImage: ' + str(e))


def deleteImageInMultiImageViewer(self, currentImagePath, imageList, 
                                   subjectID, studyName, seriesName,
                                      lastSliderPosition, subWindow):
    """When the Delete button is clicked on the multi image viewer,
    this function deletes the physical image, removes the 
    reference to it in the XML file and removes it from the image viewer.
    
    Input Parmeters
    ***************
        self - an object reference to the WEASEL interface.
        currentImagePath - file path to the image being viewed.
        studyName - string variable containing name of the DICOMstudy 
                containing the DICOM series of images to be displayed
        seriesName - string variable containing the name of DICOM series
                of images to be displayed
        lastSliderPosition - integer variable holding the value of the 
                    slider when the delete button is clicked; i.e., the
                    number of the image being deleted.
    """
    try:
        logger.info("DisplayImageColour.deleteImageInMultiImageViewer called")
        imageName = os.path.basename(currentImagePath)
        #print ('study id {} series id {}'.format(studyName, seriesName))
        buttonReply = QMessageBox.question(self, 
            'Delete DICOM image', "You are about to delete image {}".format(imageName), 
            QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)

        if buttonReply == QMessageBox.Ok:
            #Delete physical file
            if os.path.exists(currentImagePath):
                os.remove(currentImagePath)
            #Remove deleted image from the list
            imageList.remove(currentImagePath)

            #Refresh the multi-image viewer to remove deleted image
            #First close it
            subWindow.close()
            QApplication.processEvents()
                
            if len(imageList) == 0:
                #Only redisplay the multi-image viewer if there
                #are still images in the series to display
                #The image list is empty, so do not redisplay
                #multi image viewer 
                pass   
            elif len(imageList) == 1:
                #There is only one image left in the display
                displayMultiImageSubWindow(self, imageList, subjectID, studyName, seriesName)
            elif len(imageList) + 1 == lastSliderPosition:    
                    #we are deleting the last image in the series of images
                    #so move the slider back to the penultimate image in list 
                displayMultiImageSubWindow(self, imageList, subjectID,
                                    studyName, seriesName, len(imageList))
            else:
                #We are deleting an image at the start of the list
                #or in the body of the list. Move slider forwards to 
                #the next image in the list.
                displayMultiImageSubWindow(self, imageList, subjectID,
                                    studyName, seriesName, lastSliderPosition)
     
            #Now update XML file
            #Get the series containing this image and count the images it contains
            #If it is the last image in a series then remove the
            #whole series from XML file
            #If it is not the last image in a series
            #just remove the image from the XML file 
            if len(imageList) == 0:
                #no images left in the series, so remove it from the xml file
                self.objXMLReader.removeOneSeriesFromStudy(subjectID, studyName, seriesName)
            elif len(imageList) > 0:
                #1 or more images in the series, 
                #so just remove the image from its series in the xml file
                self.objXMLReader.removeOneImageFromSeries(subjectID, 
                    studyName, seriesName, currentImagePath)
            #Update tree view with xml file modified above
            treeView.refreshDICOMStudiesTreeView(self)
    except Exception as e:
        print('Error in DisplayImageColour.deleteImageInMultiImageViewer: ' + str(e))
        logger.error('Error in DisplayImageColour.deleteImageInMultiImageViewer: ' + str(e))


def exportImage(self,  graphicsView, cmbColours):
    """Function executed when the Export button is clicked.  
    It exports the DICOM image and its colour table to a png graphics file.
    It launches a file dialog, so that the user can select the file path to 
    the png file in which the exported file will be stored. It also collects 
    the name of the image colour table and the image levels.
    
    Input Parmeters
    ***************
        self - an object reference to the WEASEL interface.
         graphicsView - pyqtGraph imageView widget
        cmbColours - A dropdown list of colour table names based on the QComboBox class
    """
    try:
        colourTable = cmbColours.currentText()
        #Default file name is derived from the DICOM image name
        defaultImageName = os.path.basename(self.selectedImagePath) 
        #remove .dcm extension
        defaultImageName = os.path.splitext(defaultImageName)[0] + '.png'
        #Display a save file dialog to get the full file path and name of
        #where to export the DICOM image & its colour table to a png file
        fileName, _ = QFileDialog.getSaveFileName(caption="Enter a file name", 
                                                    directory=defaultImageName, 
                                                    filter="*.png")
        minimumValue, maximumValue =  graphicsView.getLevels()

        #Test if the user has selected a file name
        if fileName:
            exportImageViaMatplotlib(self,  graphicsView.getImageItem().image,
                                            fileName, 
                                            colourTable,
                                             minimumValue,
                                            maximumValue)
    except Exception as e:
        print('Error in DisplayImageColour.exportImage: ' + str(e))
        logger.error('Error in DisplayImageColour.exportImage: ' + str(e))


def exportImageViaMatplotlib(self, pixelArray, fileName, colourTable,  minimumValue, maximumValue):
    """This function uses matplotlib.pyplot to save the DICOM image being viewed 
    and its colour table in a png file with the path+filename in fileName. 
    
    Input Parmeters
    ***************
        self - an object reference to the WEASEL interface.
        pixelArray - pixel array to be exported as a png file
        fileName - file path to the png file in which the exported file will be stored.
        colourTable - String variable containing the name of a colour table
        maximumValue - Maximum pixel value in the image
        minimumValue - Minimum pixel value in the image
    """ 
    try:
        #axisOrder = pg.getConfigOption('imageAxisOrder') 
        #if axisOrder =='row-major':
        #Transpose the array so as to match the screen image 
        # (a transpose is already applied when reading DICOM image)
        pixelArray = np.transpose(pixelArray)
        cmap = plt.get_cmap(colourTable)
        pos = plt.imshow(pixelArray, cmap=cmap)
        plt.clim(int(minimumValue), int(maximumValue))
        cBar = plt.colorbar()
        cBar.minorticks_on()
        plt.savefig(fname=fileName)
        plt.close()
        QMessageBox.information(self, "Export Image", "Image Saved")
    except Exception as e:
        print('Error in DisplayImageColour.exportImageViaMatplotlib: ' + str(e))
        logger.error('Error in DisplayImageColour.exportImageViaMatplotlib: ' + str(e))


def applyColourTableToAnImage(cmbColours, graphicsView):
    colourTable = cmbColours.currentText()
    if colourTable.lower() == 'custom':
        colourTable = 'gray'                
        displayColourTableInComboBox(cmbColours, 'gray')   
    setPgColourMap(colourTable,  graphicsView)


def applyColourTableToSeries(self, button, graphicsView, cmbColours, seriesName): 
    """This function applies a user selected colour map to the current image.
    If the Apply checkbox is checked then the new colour map is also applied to 
    the whole series of DICOM images by setting a boolean flag to True.

    Input Parmeters
    ***************
        self - an object reference to the WEASEL interface.
         graphicsView - pyqtGraph imageView widget
        cmbColours - A dropdown list of colour table names based on the QComboBox class
        seriesName - string variable containing the name of 
            DICOM series of images to be displayed
        applySeriesCheckBox - Name of the apply user selection to the whole series checkbox widget
    """
    try:
        applyColourTableToAnImage(cmbColours, graphicsView)

        global userSelectionDict
        obj = userSelectionDict[seriesName]
        
        if button.isChecked():
            button.setStyleSheet("background-color: red")
            obj.setSeriesUpdateStatus(True)
            obj.setImageUpdateStatus(False)
        else:
            obj.setSeriesUpdateStatus(False)
            button.setStyleSheet(
            "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
            )
               
    except Exception as e:
        print('Error in DisplayImageColour.applyColourTableToSeries: ' + str(e))
        logger.error('Error in DisplayImageColour.applyColourTableToSeries: ' + str(e))              
        

def clearUserSelection(self, imageSlider, seriesName):
    """This function removes the user selected colour tables, contrast & intensity values from
    the list of image lists that hold these values.  They are reset to the default values of
    'default' for the colour table and -1 for the contrast & intensity values
    
    Input Parmeters
    ***************
        self - an object reference to the WEASEL interface.
        imageSlider - name of the slider widget used to scroll through the images.
        seriesName - string variable containing the name of DICOM series of images to be displayed
    """
    global userSelectionDict
    obj = userSelectionDict[seriesName]
    obj.clearUserSelection()

    #reload current image to display it without user selected 
    #colour table and levels.
    #This is done by advancing the slider and then moving it  
    #back to the original image
    if imageSlider:
        imageNumber = imageSlider.value()
        if imageNumber == 1:
            tempNumber = imageNumber + 1
        else:
            tempNumber = imageNumber - 1

        imageSlider.setValue(tempNumber)
        imageSlider.setValue(imageNumber)
                    

def updateImageUserSelection(self, applyButton, 
                             cmbColours,
                             spinBoxIntensity, spinBoxContrast,
                             seriesName, 
                             firstImagePath):
    """When the colour table & levels associated with an image are changed, their values
        are associated with that image in the list of lists userSelectionList, where each sublist 
        represents an image thus:
            [0] - Image name (used as key to search the list of lists)
            [1] - colour table name
            [2] - intensity level
            [3] - contrast level
        userSelectionList is initialised with default values in the function displayMultiImageSubWindow
        
        Input Parmeters
        ***************
        self - an object reference to the WEASEL interface.
        applySeriesCheckBox - Name of the apply user selection to the whole series checkbox widget
        cmbColours - A dropdown list of colour table names based on the QComboBox class 
        spinBoxIntensity - name of the spinbox widget that displays/sets image intensity.
        spinBoxContrast - name of the spinbox widget that displays/sets image contrast.
        seriesName - string variable containing the name of DICOM series of images to be displayed
        firstImagePath - string variable containing the file path to the first image in the DICOM series
        """
    try:
        logger.info('updateImageUserSelection called')
        if not applyButton.isChecked():
            #The apply user selection to whole series checkbox 
            #is not checked

            colourTable = cmbColours.currentText()
            intensity = spinBoxIntensity.value()
            contrast = spinBoxContrast.value()

            if self.selectedImagePath:
                self.selectedImageName = os.path.basename(self.selectedImagePath)
            else:
                #Workaround for the fact that when the first image is displayed,
                #somehow self.selectedImageName looses its value.
                self.selectedImageName = os.path.basename(firstImagePath)
            
            #print("self.selectedImageName ={}".format(self.selectedImageName))
            #print("colourTable = {}".format(colourTable))
            global userSelectionDict
            obj = userSelectionDict[seriesName]
            obj.updateUserSelection(self.selectedImageName, colourTable, intensity, contrast)
            
    except Exception as e:
        print('Error in DisplayImageColour.updateImageUserSelection: ' + str(e))
        logger.error('Error in DisplayImageColour.updateImageUserSelection: ' + str(e))


def updateImageLevels(self,  graphicsView, spinBoxIntensity, spinBoxContrast):
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
        centre = spinBoxIntensity.value()
        width = spinBoxContrast.value()
        halfWidth = width/2

        minimumValue = centre - halfWidth
        maximumValue = centre + halfWidth
        #print("centre{}, width{},  minimumValue{}, maximumValue{}".format(centre, width,  minimumValue, maximumValue))
        graphicsView.setLevels( minimumValue, maximumValue)
        graphicsView.show()
    except Exception as e:
        print('Error in DisplayImageColour.updateImageLevels: ' + str(e))
        logger.error('Error in DisplayImageColour.updateImageLevels: ' + str(e))
        

def updateDICOM(self, lblHiddenImagePath, lblHiddenSeriesName, lblHiddenStudyName, lblHiddenSubjectID,
                cmbColours, spinBoxIntensity, spinBoxContrast, singleImage=False):
        """
        This function is executed when the Update button 
        is clicked and it coordinates the calling of the functions, 
        updateWholeDicomSeries & updateDicomSeriesImageByImage.
        
        Input Parmeters
        ***************
        self - an object reference to the WEASEL interface.
        lblHiddenSeriesName - name of the hidden label widget whose text
                    contains the name of the DICOM series whose images are 
                    being viewed.
        lblHiddenStudyName - name of the hidden label widget whose text
                contains the name of the DICOM study containing the series
                whose images are  being viewed.
        cmbColours - A dropdown list of colour table names based on the QComboBox class
        spinBoxIntensity - name of the spinbox widget that displays/sets image intensity.
        spinBoxContrast - name of the spinbox widget that displays/sets image contrast.
        """
        try:
            logger.info("DisplayImageColour.updateDICOM called")
            if singleImage:
                buttonReply = QMessageBox.question(self, 
                          'Update DICOM', "You are about to overwrite this DICOM File. Please click OK to proceed.", 
                          QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
            else:
                buttonReply = QMessageBox.question(self, 
                          'Update DICOM', "You are about to overwrite this series of DICOM Files. Please click OK to proceed.", 
                          QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
            if buttonReply == QMessageBox.Ok:
                imageName = lblHiddenImagePath.text()
                seriesName = lblHiddenSeriesName.text()
                studyName = lblHiddenStudyName.text()
                subjectID = lblHiddenSubjectID.text()
                colourTable = cmbColours.currentText()
                if singleImage == False:
                    global userSelectionDict
                    obj = userSelectionDict[seriesName]
                    #print("DisplayImageColour.updateDICOM called")
                    #print("obj.getSeriesUpdateStatus() = {}".format(obj.getSeriesUpdateStatus()))
                    #print("obj.getImageUpdateStatus() = {}".format(obj.getImageUpdateStatus()))
                    if obj.getSeriesUpdateStatus():
                        levels = [spinBoxIntensity.value(), spinBoxContrast.value()]
                        updateWholeDicomSeries(self, subjectID, seriesName, studyName, colourTable, levels)
                    if obj.getImageUpdateStatus():
                        updateDicomSeriesImageByImage(self, subjectID, seriesName, studyName)
                else:
                    SaveDICOM_Image.updateSingleDicomImage(self, 
                                                           spinBoxIntensity,
                                                           spinBoxContrast,
                                                           imageName,
                                                           seriesName,
                                                           studyName,
                                                           colourTable,
                                                           lut=None)
        except Exception as e:
            print('Error in DisplayImageColour.updateDICOM: ' + str(e))
            logger.error('Error in DisplayImageColour.updateDICOM: ' + str(e))


def updateWholeDicomSeries(self, subjectID, seriesID, studyID, colourTable, levels, lut=None):
    """
    Updates every image in a DICOM series with one colour table and
            one set of levels
            
      Input Parmeters
      ***************
        self - an object reference to the WEASEL interface.
        seriesName - string variable containing the name of DICOM series of images to be updated
        studyName - string variable containing name of the DICOMstudy 
                containing the DICOM series of images to be updated
        colourTable - String variable containing the name of a colour table
        levels  - 2 item list containing the image contrast and intensity values as integers, 
                    [contrast, intensity]
        lut - array holding a lookup table of colours. A custom colour map
        """
    try:
        logger.info("In DisplayImageColour.updateWholeDicomSeries")
        imagePathList = self.objXMLReader.getImagePathList(subjectID, studyID, seriesID)

        #Iterate through list of images and update each image
        numImages = len(imagePathList)
        messageWindow.displayMessageSubWindow(self,
            "<H4>Updating {} DICOM files</H4>".format(numImages),
            "Updating DICOM images")
        messageWindow.setMsgWindowProgBarMaxValue(self, numImages)
        imageCounter = 0
        for imagePath in imagePathList:
            dataset = ReadDICOM_Image.getDicomDataset(imagePath) 
            # Update every DICOM file in the series                                     
            updatedDataset = SaveDICOM_Image.updateSingleDicom(dataset, colourmap=colourTable, levels=levels, lut=lut)
            SaveDICOM_Image.saveDicomToFile(updatedDataset, output_path=imagePath)
            imageCounter += 1
            messageWindow.setMsgWindowProgBarValue(self, imageCounter)
        messageWindow.closeMessageSubWindow(self)
    except Exception as e:
        print('Error in DisplayImageColour.updateWholeDicomSeries: ' + str(e))


def updateDicomSeriesImageByImage(self, subjectID, seriesName, studyName):
    """Updates one or more images in a DICOM series each with potentially
    a different table and set of levels
    
    Input Parmeters
    ***************
        self - an object reference to the WEASEL interface.
        seriesName - string variable containing the name of DICOM series 
        of images to be updated
        studyName - string variable containing name of the DICOMstudy 
                containing the DICOM series of images to updated
        colourTable - String variable containing the name of a colour table
        lut - array holding a lookup table of colours. A custom colour map
    
    """
    try:
        logger.info("In DisplayImageColour.updateDicomSeriesImageByImage")
       
        imagePathList = self.objXMLReader.getImagePathList(subjectID, studyName, seriesName)

        #Iterate through list of images and update each image
        numImages = len(imagePathList)
        messageWindow.displayMessageSubWindow(self,
            "<H4>Updating {} DICOM files</H4>".format(numImages),
            "Updating DICOM images")
        messageWindow.setMsgWindowProgBarMaxValue(self, numImages)
        imageCounter = 0
        global userSelectionDict
        obj = userSelectionDict[seriesName]
        for imageCounter, imagePath in enumerate(imagePathList, 0):
            #print('In updateDicomSeriesImageByImage, series name={}'.format(seriesName))
            # Apply user selected colour table & levels to individual images in the series
            selectedColourMap, center, width = obj.returnUserSelection(imageCounter)
            #print('selectedColourMap, center, width = {}, {}, {}'.format(selectedColourMap, center, width))
            if selectedColourMap != 'default' and center != -1 and width != -1:
                # Update an individual DICOM file in the series
                #print('In If, imageCounter = {}, imagePath={}'.format(imageCounter, imagePath))
                levels = [center, width]  
                dataset = ReadDICOM_Image.getDicomDataset(imagePath)
                updatedDataset = SaveDICOM_Image.updateSingleDicom(dataset, colourmap=selectedColourMap, 
                                                    levels=levels, lut=None)
                SaveDICOM_Image.saveDicomToFile(updatedDataset, output_path=imagePath)
            messageWindow.setMsgWindowProgBarValue(self, imageCounter)
        messageWindow.closeMessageSubWindow(self)
    except Exception as e:
        print('Error in DisplayImageColour.updateDicomSeriesImageByImage: ' + str(e))


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
            print('Error in DisplayImageColour.displayColourTableInComboBox: ' + str(e))
            logger.error('Error in DisplayImageColour.displayColourTableInComboBox: ' + str(e))



def setPgColourMap(colourTable,  graphicsView, cmbColours=None, lut=None):
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
        graphicsView.setColorMap(pgMap)        
    except Exception as e:
        print('Error in DisplayImageColour.setPgColourMap: ' + str(e))
        logger.error('Error in DisplayImageColour.setPgColourMap: ' + str(e))


def getPixelValue(pos,  graphicsView, pixelArray, lblPixelValue, imageNumber=1):
    """
    This function checks that the mouse pointer is over the
    image and when it is, it determines the value of the pixel
    under the mouse pointer and displays this in the label
    lblPixelValue.

    Input parameters
    ****************
    pos - X,Y coordinates of the mouse pointer
     graphicsView - pyqtGraph imageView widget
    pixelArray - pixel array to be displayed in  graphicsView
    lblPixelValue - Label widget that displays the value of the pixel under the mouse pointer
                and the X,Y coordinates of the mouse pointer.
    """
    try:
        #print ("Image position: {}".format(pos))
        container =  graphicsView.getView()
        if container.sceneBoundingRect().contains(pos): 
            mousePoint = container.getViewBox().mapSceneToView(pos) 
            x_i = math.floor(mousePoint.x())
            y_i = math.floor(mousePoint.y()) 
            z_i =  imageNumber
            if (len(np.shape(pixelArray)) == 2) and y_i >= 0 and y_i < pixelArray.shape [ 1 ] \
                and x_i >= 0 and x_i < pixelArray.shape [ 0 ]: 
                lblPixelValue.setText(
                    "<h4> = {} @ X: {}, Y: {}, Z: {}</h4>"
                .format (round(pixelArray[ x_i, y_i ], 6), x_i, y_i, z_i))
            elif (len(np.shape(pixelArray)) == 3) \
                and x_i >= 0 and x_i < pixelArray.shape [ 1 ] \
                and y_i >= 0 and y_i < pixelArray.shape [ 2 ]:
                z_i = math.floor(graphicsView.timeIndex(graphicsView.timeLine)[1])
                lblPixelValue.setText(
                    "<h4> = {} @ X: {}, Y: {}, Z: {}</h4>"
                .format (round(pixelArray[ z_i, x_i, y_i ], 6), x_i, y_i, z_i + 1))
            else:
                lblPixelValue.setText("")
        else:
            lblPixelValue.setText("")
                   
    except Exception as e:
        print('Error in DisplayImageColour.getPixelValue: ' + str(e))
        logger.error('Error in DisplayImageColour.getPixelValue: ' + str(e))


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
            logger.info("DisplayImageColour.readLevelsFromDICOMImage called")
            #set default values
            centre = -1 
            width = -1 
            maximumValue = -1  
            minimumValue = -1 
            dataset = ReadDICOM_Image.getDicomDataset(self.selectedImagePath)
            if dataset and hasattr(dataset, 'WindowCenter') and hasattr(dataset, 'WindowWidth'):
                slope = float(getattr(dataset, 'RescaleSlope', 1))
                intercept = float(getattr(dataset, 'RescaleIntercept', 0))
                centre = dataset.WindowCenter # * slope + intercept
                width = dataset.WindowWidth # * slope
                maximumValue = centre + width/2
                minimumValue = centre - width/2
            elif dataset and hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
                # In Enhanced MRIs, this display will retrieve the centre and width values of the first slice
                slope = dataset.PerFrameFunctionalGroupsSequence[0].PixelValueTransformationSequence[0].RescaleSlope
                intercept = dataset.PerFrameFunctionalGroupsSequence[0].PixelValueTransformationSequence[0].RescaleIntercept
                centre = dataset.PerFrameFunctionalGroupsSequence[0].FrameVOILUTSequence[0].WindowCenter # * slope + intercept
                width = dataset.PerFrameFunctionalGroupsSequence[0].FrameVOILUTSequence[0].WindowWidth # * slope
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
            print('Error in DisplayImageColour.readLevelsFromDICOMImage: ' + str(e))
            logger.error('Error in DisplayImageColour.readLevelsFromDICOMImage: ' + str(e))

