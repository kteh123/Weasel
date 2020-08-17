"""This module contains functions for the display of a single DICOM image
or a series of DICOM images in an MDI subwindow that includes functionality
for the selecting and applying a colour table to the image/image series and
adjusting the contrast and intensity of the image/image series.  
It is possible to update the DICOM image/image series with the new 
colour table, contrast & intensity values."""

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
import CoreModules.WEASEL.MessageWindow  as messageWindow
from CoreModules.WEASEL.UserImageColourSelection import UserSelection

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
            'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
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
#The class UserSelection in CoreModules.WEASEL.UserImageColourSelection supplies the functionality
#to manipulate userSelectionList. 
userSelectionDict = {}

def displayImageSubWindow(self, derivedImagePath=None):
        """
        Creates a subwindow that displays a single DICOM image. 
        """
        try:
            logger.info("DisplayImageColour.displayImageSubWindow called")
            #self.selectedImagePath is populated when the image in the
            #tree view is clicked & selected
            
            imageViewer, layout, lblImageMissing, subWindow = \
                displayImageCommon.setUpImageViewerSubWindow(self)
            windowTitle = displayImageCommon.getDICOMFileData(self)
            subWindow.setWindowTitle(windowTitle)

            if derivedImagePath:
                imagePathForDisplay = derivedImagePath
            else:
                imagePathForDisplay = self.selectedImagePath
            
            lblHiddenImagePath = QLabel(imagePathForDisplay)
            pixelArray = readDICOM_Image.returnPixelArray(imagePathForDisplay)
            colourTable, lut = readDICOM_Image.getColourmap(imagePathForDisplay)

            lblHiddenImagePath.hide()
            lblHiddenStudyID = QLabel()
            lblHiddenStudyID.hide()
            lblHiddenSeriesID = QLabel()
            lblHiddenSeriesID.hide()
            
            #Maintain image data in hidden labels on the subwindow.
            #These values will used when updating an image with a
            #new colour table & intensity & contrast values. This
            #is done because several of these windows may be open
            #at once and the global self.selectedImagePath maybe
            #points to an image in a window other than the one
            #the user is working on
            layout.addWidget(lblHiddenSeriesID)
            layout.addWidget(lblHiddenStudyID)
            layout.addWidget(lblHiddenImagePath)

            spinBoxIntensity = QDoubleSpinBox()
            spinBoxContrast = QDoubleSpinBox()
            img, imv, viewBox = displayImageCommon.setUpViewBoxForImage( 
                                                     imageViewer, 
                                                     layout, 
                                                     spinBoxIntensity, 
                                                     spinBoxContrast)

            lblPixelValue = QLabel("<h4>Pixel Value:</h4>")
            lblPixelValue.show()
            layout.addWidget(lblPixelValue)
            
            cmbColours = setUpColourTools(self, layout, imv, True,  
                                                lblHiddenImagePath, lblHiddenSeriesID, lblHiddenStudyID, 
                                                spinBoxIntensity, spinBoxContrast)
            
            displayImageCommon.displayColourTableInComboBox(cmbColours, colourTable)
            displayPixelArray(self, pixelArray, 0,
                                    lblImageMissing,
                                    lblPixelValue,
                                    spinBoxIntensity, spinBoxContrast,
                                    imv, colourTable, lblHiddenSeriesID.text(),
                                    cmbColours, lut)  
        except Exception as e:
            print('Error in DisplayImageColour.displayImageSubWindow: ' + str(e))
            logger.error('Error in  DisplayImageColour.displayImageSubWindow: ' + str(e)) 


def displayMultiImageSubWindow(self, imageList, studyName, 
                     seriesName, sliderPosition = -1):
        """
        Creates a subwindow that displays all the DICOM images in a series. 
        A slider allows the user to navigate  through the images.  A delete
        button allows the user to delete the image they are viewing.

        The user can either update the whole series with a new colour table 
        and contrast & intensity values  or they can update individual
        images in the series with a new colour table 
        and contrast & intensity values.
        """
        try:
            logger.info("DisplayImageColour.displayMultiImageSubWindow called")
            imageViewer, layout, lblImageMissing, subWindow = \
                displayImageCommon.setUpImageViewerSubWindow(self)

            #set up list of lists to hold user selected colour table and level data
            userSelectionList = [[os.path.basename(imageName), 'default', -1, -1]
                                for imageName in imageList]
            #add user selection object to dictionary
            global userSelectionDict
            userSelectionDict[seriesName] = UserSelection(userSelectionList)
            
            #Study ID & Series ID are stored locally on the
            #sub window in case the user wishes to delete an
            #image in the series or update an image/image series
            #with new colour table, contrast & intensity values.
            #They may have several series open at once,
            #so the selected series on the treeview
            #may not the same as that from which the image is
            #being deleted.
            firstImagePath = imageList[0]
            lblHiddenImagePath = QLabel(firstImagePath)
            #lblHiddenImagePath.hide()
            lblHiddenStudyID = QLabel(studyName)
            lblHiddenStudyID.hide()
            lblHiddenSeriesID = QLabel(seriesName)
            lblHiddenSeriesID.hide()
            btnDeleteDICOMFile = QPushButton('Delete DICOM Image')
            btnDeleteDICOMFile.setToolTip(
            'Deletes the DICOM image being viewed')
            btnDeleteDICOMFile.hide()
         
            layout.addWidget(lblHiddenImagePath)
            layout.addWidget(lblHiddenSeriesID)
            layout.addWidget(lblHiddenStudyID)
            layout.addWidget(btnDeleteDICOMFile)

            spinBoxIntensity = QDoubleSpinBox()
            spinBoxContrast = QDoubleSpinBox()
            imageSlider = QSlider(Qt.Horizontal)

            img, imv, viewBox = displayImageCommon.setUpViewBoxForImage(imageViewer, 
                                                     layout, spinBoxIntensity, spinBoxContrast) 
            lblPixelValue = QLabel("<h4>Pixel Value:</h4>")
            lblPixelValue.show()
            layout.addWidget(lblPixelValue)
            cmbColours = setUpColourTools(self, layout, imv, False,  
                                               lblHiddenImagePath, lblHiddenSeriesID, lblHiddenStudyID, 
                                               spinBoxIntensity, spinBoxContrast,
                                               imageSlider, showResetButton=True)

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
                  lambda: imageSliderMoved(self, seriesName, 
                                                imageList, 
                                                imageSlider.value(),
                                                lblImageMissing,
                                                lblPixelValue,
                                                btnDeleteDICOMFile,
                                                imv, 
                                                spinBoxIntensity, spinBoxContrast,
                                                cmbColours,
                                                subWindow))
           
            #Display the first image in the viewer
            imageSliderMoved(self, seriesName, 
                                  imageList,
                                  imageSlider.value(),
                                  lblImageMissing,
                                  lblPixelValue,
                                  btnDeleteDICOMFile,
                                  imv, 
                                  spinBoxIntensity, spinBoxContrast,
                                  cmbColours,
                                  subWindow)
            
            btnDeleteDICOMFile.clicked.connect(lambda:
                                               deleteImageInMultiImageViewer(self,
                                      self.selectedImagePath, 
                                      lblHiddenStudyID.text(), 
                                      lblHiddenSeriesID.text(),
                                      imageSlider.value()))
           
        except Exception as e:
            print('Error in DisplayImageColour.displayMultiImageSubWindow: ' + str(e))
            logger.error('Error in DisplayImageColour.displayMultiImageSubWindow: ' + str(e))


def setUpColourTools(self, layout, imv,
            singleImageSelected,
            lblHiddenImagePath,
            lblHiddenSeriesID,
            lblHiddenStudyID, spinBoxIntensity, spinBoxContrast,             
            imageSlider = None, showResetButton = False):
        """
            Generates widgets for the display of a 
            dropdown list containing colour tables
            and spin boxes for setting image contrast and intensity.
        """
        try:
            logger.info("displayImageColour.setUpColourTools called")
            groupBoxColour = QGroupBox('Colour Table')
            groupBoxLevels = QGroupBox('Levels')
            #gridLayoutColour will later be added to groupBoxLevels
            gridLayoutColour = QGridLayout()
            gridLayoutLevels = QGridLayout()
            #add grid layouts to the group boxes
            groupBoxColour.setLayout(gridLayoutColour)
            groupBoxLevels.setLayout(gridLayoutLevels)
            layout.addWidget(groupBoxColour)

            #When this checkbox is checked, the selected colour table, 
            #contrast and intensity levels are added to the whole series
            chkApply = QCheckBox("Apply Selection to whole series")
            chkApply.stateChanged.connect(lambda:applyColourTableToSeries(self, imv, 
                                                                         cmbColours, 
                                                                         lblHiddenSeriesID.text(),
                                                                         chkApply))
            chkApply.setToolTip(
                    "Tick to apply colour table and levels selected by the user to the whole series")
       
            cmbColours = QComboBox()
            cmbColours.setToolTip('Select a colour table to apply to the image')
            cmbColours.blockSignals(True)
            cmbColours.addItems(listColours)
            cmbColours.setCurrentIndex(0)
            cmbColours.blockSignals(False)
            cmbColours.currentIndexChanged.connect(lambda:
                        applyColourTableToSeries(self, imv, cmbColours, lblHiddenSeriesID.text(), chkApply))

            btnUpdate = QPushButton('Update') 
            btnUpdate.setToolTip('Update DICOM with the new colour table, contrast & intensity levels')
            #For the update button, connect signal to slot
            if singleImageSelected:
                #Viewing and potentially updating a single DICOM images
                    btnUpdate.clicked.connect(lambda:saveDICOM_Image.updateSingleDicomImage
                                            (self, 
                                            spinBoxIntensity, spinBoxContrast,
                                            lblHiddenImagePath.text(),
                                                    lblHiddenSeriesID.text(),
                                                    lblHiddenStudyID.text(),
                                                    cmbColours.currentText(),
                                                    lut=None))
            else:
                #Viewing and potentially updating a series of DICOM images
                btnUpdate.clicked.connect(lambda:updateDICOM(self, 
                                                                lblHiddenSeriesID,
                                                                lblHiddenStudyID,
                                                                cmbColours,
                                                                    spinBoxIntensity, 
                                                                    spinBoxContrast))
            
  
            btnExport = QPushButton('Export') 
            btnExport.setToolTip('Exports the image to an external graphic file.')
            btnExport.clicked.connect(lambda:exportImage(self, imv, cmbColours))

            #Levels 
            lblIntensity = QLabel("Centre (Intensity)")
            lblContrast = QLabel("Width (Contrast)")
            lblIntensity.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            lblContrast.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            
            spinBoxIntensity.setMinimum(-100000.00)
            spinBoxContrast.setMinimum(-100000.00)
            spinBoxIntensity.setMaximum(1000000000.00)
            spinBoxContrast.setMaximum(1000000000.00)
            spinBoxIntensity.setWrapping(True)
            spinBoxContrast.setWrapping(True)
            spinBoxIntensity.valueChanged.connect(lambda: updateImageLevels(self,
            imv,spinBoxIntensity, spinBoxContrast))
            spinBoxContrast.valueChanged.connect(lambda: updateImageLevels(self,
            imv,spinBoxIntensity, spinBoxContrast))
            
            if not singleImageSelected: #series selected
                spinBoxIntensity.valueChanged.connect(lambda: updateUserSelectedLevels(self,
                chkApply,spinBoxIntensity.value(), spinBoxContrast.value(), lblHiddenSeriesID.text()))
                spinBoxContrast.valueChanged.connect(lambda: updateUserSelectedLevels(self,
                chkApply,spinBoxIntensity.value(), spinBoxContrast.value(), lblHiddenSeriesID.text()))

            gridLayoutLevels.addWidget(lblIntensity, 0,0)
            gridLayoutLevels.addWidget(spinBoxIntensity, 0, 1)
            gridLayoutLevels.addWidget(lblContrast, 0,2)
            gridLayoutLevels.addWidget(spinBoxContrast, 0,3)
            gridLayoutColour.addWidget(cmbColours,0,0)

            if showResetButton:
                #Viewing a DICOM series, so show the Reset button
                #and Apply to Series checkbox
                gridLayoutColour.addWidget(chkApply,0,1)
                btnReset = QPushButton('Reset') 
                btnReset.setToolTip('Return to colour tables and levels in the DICOM file')
                #Clicking Reset button deletes user selected colour table and contrast 
                #and intensity levelts and returns images to values in the original DICOM file.
                btnReset.clicked.connect(lambda: clearUserSelection(self, imageSlider,
                                                                   lblHiddenSeriesID.text()))
                gridLayoutColour.addWidget(btnReset,0,2)
                gridLayoutColour.addWidget(btnUpdate,1,1)
                gridLayoutColour.addWidget(btnExport,1,2)
                gridLayoutColour.addWidget(groupBoxLevels, 2, 0, 1, 3)
                cmbColours.activated.connect(lambda:
                        updateUserSelectedColourTable(self, cmbColours, chkApply, 
                                                      lblHiddenSeriesID.text(),
                                                      lblHiddenImagePath.text()))
            else:
                gridLayoutColour.addWidget(btnUpdate,0,1)
                gridLayoutColour.addWidget(btnExport,0,2)
                gridLayoutColour.addWidget(groupBoxLevels, 1, 0, 1, 3)

            return cmbColours
        except Exception as e:
            print('Error in displayImageColour.setUpColourTools: ' + str(e))
            logger.error('Error in displayImageColour.setUpColourTools: ' + str(e))


def displayPixelArray(self, pixelArray, currentImageNumber,
                          lblImageMissing, lblPixelValue,
                          spinBoxIntensity, spinBoxContrast,
                          imv, colourTable, cmbColours, 
                          seriesID,
                          lut=None,
                          multiImage=False, deleteButton=None):
        """Displays the an image's pixel array in a pyqtGraph imageView widget 
        & sets its colour table, contrast and intensity levels. 
        Also, sets the contrast and intensity in the associated histogram."""
        try:
            logger.info("DisplayImageColour.displayPixelArray called")
            global userSelectionDict
            obj = userSelectionDict[seriesID]
            if multiImage:
                #only show delete button when viewing a series
                deleteButton.show()
            else:
                #Create dummy button to prevent runtime error
                #This is the case when viewing a single image
                deleteButton = QPushButton()
                deleteButton.hide()

            #Check that pixel array holds an image & display it
            if pixelArray is None:
                #the image is missing, so show a black screen
                lblImageMissing.show()
                deleteButton.hide()
                imv.setImage(np.array([[0,0,0],[0,0,0]]))  
            else:
                if obj.getSeriesUpdateStatus():
                    #apply selected contrast and intensity values
                    #for the whole series to this image
                    centre = spinBoxIntensity.value()
                    width = spinBoxContrast.value()
                    minimumValue = centre - (width/2)
                    maximumValue = centre + (width/2)
                elif obj.getImageUpdateStatus():
                    #try to retrieve saved user selected levels for this image
                    _, centre, width = obj.returnUserSelection(currentImageNumber) 
                    if centre != -1:
                        #saved values exist, so use them
                        minimumValue = centre - (width/2)
                        maximumValue = centre + (width/2)
                    else:  
                        # No user selected values exist for this image, 
                        # so retrieve them from the DICOM image
                        #Get minimum value
                        try:
                            dataset = readDICOM_Image.getDicomDataset(self.selectedImagePath)
                            slope = float(getattr(dataset, 'RescaleSlope', 1))
                            intercept = float(getattr(dataset, 'RescaleIntercept', 0))
                            centre = dataset.WindowCenter * slope + intercept
                            width = dataset.WindowWidth * slope
                            minimumValue = centre - width/2
                        except:
                            minimumValue = np.amin(pixelArray) if (np.median(pixelArray) - iqr(pixelArray, rng=(
                            1, 99))/2) < np.amin(pixelArray) else np.median(pixelArray) - iqr(pixelArray, rng=(1, 99))/2
                            centre = spinBoxIntensity.value()
                            width = spinBoxContrast.value()
                        #Get Maximum value
                        try:
                            dataset = readDICOM_Image.getDicomDataset(self.selectedImagePath)
                            slope = float(getattr(dataset, 'RescaleSlope', 1))
                            intercept = float(getattr(dataset, 'RescaleIntercept', 0))
                            centre = dataset.WindowCenter * slope + intercept
                            width = dataset.WindowWidth * slope
                            maximumValue = centre + width/2
                        except:
                            maximumValue = np.amax(pixelArray) if (np.median(pixelArray) + iqr(pixelArray, rng=(
                            1, 99))/2) > np.amax(pixelArray) else np.median(pixelArray) + iqr(pixelArray, rng=(1, 99))/2
                            centre = spinBoxIntensity.value()
                            width = spinBoxContrast.value()
                else: #Read levels directly from the DICOM image
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
                        centre = minimumValue + (abs(maximumValue) - abs(minimumValue))/2
                        width = maximumValue - abs(minimumValue)

                spinBoxIntensity.setValue(centre)
                spinBoxContrast.setValue(width)
                blockHistogramSignals(imv, True)
                imv.setImage(pixelArray, autoHistogramRange=True, levels=(minimumValue, maximumValue))
                blockHistogramSignals(imv, False)
        
                #Add Colour Table or look up table To Image
                displayImageCommon.setPgColourMap(colourTable, imv, cmbColours, lut)

                lblImageMissing.hide()   
  
                imv.getView().scene().sigMouseMoved.connect(
                   lambda pos: displayImageCommon.getPixelValue(pos, imv, pixelArray, lblPixelValue))

        except Exception as e:
            print('Error in DisplayImageColour.displayPixelArray: ' + str(e))
            logger.error('Error in DisplayImageColour.displayPixelArray: ' + str(e))


def blockHistogramSignals(imgView, block):
        """ Toggles (off/on) blocking the signals from the histogram associated with image view imgView. 
        block - boolean taking values True/False
        """
        histogramObject = imgView.getHistogramWidget().getHistogram()
        histogramObject.blockSignals(block)


def imageSliderMoved(self, seriesName, imageList, imageNumber,
                        lblImageMissing, lblPixelValue, 
                        btnDeleteDICOMFile, imv, 
                        spinBoxIntensity, spinBoxContrast,
                        cmbColours,
                        subWindow):
        """On the Multiple Image Display sub window, this
        function is called when the image slider is moved. 
        It causes the next image in imageList to be displayed"""
        try:
            global userSelectionDict
            obj = userSelectionDict[seriesName]

            logger.info("DisplayImageColour.imageSliderMoved called")
            currentImageNumber = imageNumber - 1
            if currentImageNumber >= 0:
                self.selectedImagePath = imageList[currentImageNumber]
                #print("imageSliderMoved before={}".format(self.selectedImagePath))
                pixelArray = readDICOM_Image.returnPixelArray(self.selectedImagePath)
                lut = None
                #Get colour table of the image to be displayed
                if obj.getSeriesUpdateStatus():
                    colourTable = cmbColours.currentText()
                elif obj.getImageUpdateStatus():
                    colourTable, _, _ = obj.returnUserSelection(currentImageNumber)  
                    if colourTable == 'default':
                        colourTable, lut = readDICOM_Image.getColourmap(self.selectedImagePath)
                    #print('apply User Selection, colour table {}, image number {}'.format(colourTable,currentImageNumber ))
                else:
                    colourTable, lut = readDICOM_Image.getColourmap(self.selectedImagePath)

                #display above colour table in colour table dropdown list
                displayImageCommon.displayColourTableInComboBox(cmbColours, colourTable)

                displayPixelArray(self, pixelArray, currentImageNumber, 
                                       lblImageMissing,
                                       lblPixelValue,
                                       spinBoxIntensity, spinBoxContrast,
                                       imv, colourTable,
                                       cmbColours, seriesName,
                                       lut,
                                       multiImage=True,  
                                       deleteButton=btnDeleteDICOMFile) 

                subWindow.setWindowTitle(seriesName + ' - ' 
                         + os.path.basename(self.selectedImagePath))
              
        except Exception as e:
            print('Error in DisplayImageColour.imageSliderMoved: ' + str(e))
            logger.error('Error in DisplayImageColour.imageSliderMoved: ' + str(e))


def deleteImageInMultiImageViewer(self, currentImagePath, 
                                      studyID, seriesID,
                                      lastSliderPosition):
    """When the Delete button is clicked on the multi image viewer,
    this function deletes the physical image, removes the 
    reference to it in the XML file and removes it from the image viewer."""
    try:
        logger.info("DisplayImageColour.deleteImageInMultiImageViewer called")
        imageName = os.path.basename(currentImagePath)
        #print ('study id {} series id {}'.format(studyID, seriesID))
        buttonReply = QMessageBox.question(self, 
            'Delete DICOM image', "You are about to delete image {}".format(imageName), 
            QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)

        if buttonReply == QMessageBox.Ok:
            #Delete physical file
            os.remove(currentImagePath)
            #Remove deleted image from the list
            self.imageList.remove(currentImagePath)

            #Refresh the multi-image viewer to remove deleted image
            #First close it
            self.closeSubWindow(seriesID)
                
            if len(self.imageList) == 0:
                #Only redisplay the multi-image viewer if there
                #are still images in the series to display
                #The image list is empty, so do not redisplay
                #multi image viewer 
                pass   
            elif len(self.imageList) == 1:
                #There is only one image left in the display
                displayMultiImageSubWindow(self, self.imageList, studyID, seriesID)
            elif len(self.imageList) + 1 == lastSliderPosition:    
                    #we are deleting the nth image in a series of n images
                    #so move the slider back to penultimate image in list 
                displayMultiImageSubWindow(self, self.imageList, 
                                    studyID, seriesID, len(self.imageList))
            else:
                #We are deleting an image at the start of the list
                #or in the body of the list. Move slider forwards to 
                #the next image in the list.
                displayMultiImageSubWindow(self, self.imageList, 
                                    studyID, seriesID, lastSliderPosition)
     
            #Now update XML file
            #Get the series containing this image and count the images it contains
            #If it is the last image in a series then remove the
            #whole series from XML file
            #If it is not the last image in a series
            #just remove the image from the XML file 
            images = self.objXMLReader.getImageList(studyID, seriesID)
            if len(images) == 1:
                #only one image, so remove the series from the xml file
                #need to get study (parent) containing this series (child)
                #then remove child from parent
                self.objXMLReader.removeSeriesFromXMLFile(studyID, seriesID)
            elif len(images) > 1:
                #more than 1 image in the series, 
                #so just remove the image from the xml file
                ##need to get the series (parent) containing this image (child)
                ##then remove child from parent
                self.objXMLReader.removeOneImageFromSeries(
                    studyID, seriesID, currentImagePath)
            #Update tree view with xml file modified above
            treeView.refreshDICOMStudiesTreeView(self)
    except Exception as e:
        print('Error in DisplayImageColour.deleteImageInMultiImageViewer: ' + str(e))
        logger.error('Error in DisplayImageColour.deleteImageInMultiImageViewer: ' + str(e))


def exportImage(self, imv, cmbColours):
    """Function executed when the Export button is clicked.  
    It exports the DICOM image and its colour table to a png graphics file."""
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
        minLevel, maxLevel = imv.getLevels()

        #Test if the user has selected a file name
        if fileName:
            exportImageViaMatplotlib(self, imv.getImageItem().image,
                                            fileName, 
                                            colourTable,
                                            minLevel,
                                            maxLevel)
    except Exception as e:
        print('Error in DisplayImageColour.exportImage: ' + str(e))
        logger.error('Error in DisplayImageColour.exportImage: ' + str(e))


def exportImageViaMatplotlib(self, pixelArray, fileName, cm_name, minLevel, maxLevel):
    """This function uses matplotlib.pyplot to save the DICOM image being viewed 
    and its colour table in a png file with the path+filename in fileName. """ 
    try:
        axisOrder = pg.getConfigOption('imageAxisOrder') 
        if axisOrder =='row-major':
            #rotate image 90 degree so as to match the screen image
            pixelArray = scipy.ndimage.rotate(pixelArray, 270)
        cmap = plt.get_cmap(cm_name)
        pos = plt.imshow(pixelArray,  cmap=cmap)
        plt.clim(int(minLevel), int(maxLevel))
        cBar = plt.colorbar()
        cBar.minorticks_on()
        plt.savefig(fname=fileName)
        plt.close()
        QMessageBox.information(self, "Export Image", "Image Saved")
    except Exception as e:
        print('Error in DisplayImageColour.exportImageViaMatplotlib: ' + str(e))
        logger.error('Error in DisplayImageColour.exportImageViaMatplotlib: ' + str(e))


def applyColourTableToSeries(self, imv, cmbColours, seriesID, chkBox=None): 
    """This function applies a user selected colour map to the current image.
    If the Apply checkbox is checked then the new colour map is also applied to 
    the whole series of DICOM images by setting the boolean flag
    overRideSeriesSavedColourmapAndLevels to True.
    """
    global userSelectionDict
    obj = userSelectionDict[seriesID]
    try:
        colourTable = cmbColours.currentText()
        if colourTable.lower() == 'custom':
            colourTable = 'gray'                
            displayImageCommon.displayColourTableInComboBox(cmbColours, 'gray')   

        displayImageCommon.setPgColourMap(colourTable, imv)
        if chkBox.isChecked():
            obj.setSeriesUpdateStatus(True)
            obj.setImageUpdateStatus(False)
        else:
            obj.setSeriesUpdateStatus(False)
               
    except Exception as e:
        print('Error in DisplayImageColour.applyColourTableToSeries: ' + str(e))
        logger.error('Error in DisplayImageColour.applyColourTableToSeries: ' + str(e))              
        

def clearUserSelection(self, imageSlider, seriesName):
    """This function removes the user selected colour tables, contrast & intensity values from
    the list of image lists that hold these values.  They are reset to the default values of
    'default' for the colour table and -1 for the contrast & intensity values"""
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
                    

def updateUserSelectedLevels(self, chkBox, 
                             intensity, 
                             contrast,
                             seriesName):
    """When the levels associated with an image are changed, their values
        are associated with that image in the list of lists userSelectionList, where each sublist 
        represents an image thus:
            [0] - Image name (used as key to search the list of lists)
            [1] - colour table name
            [2] - intensity level
            [3] - contrast level
        userSelectionList is initialised with default values in the function displayMultiImageSubWindow
        """
    try:
        if chkBox.isChecked() == False:
            if self.selectedImagePath:
                self.selectedImageName = os.path.basename(self.selectedImagePath)
            else:
                #Workaround for the fact that when the first image is displayed,
                #somehow self.selectedImageName looses its value.
                self.selectedImageName = os.path.basename(self.imageList[0])
            
            global userSelectionDict
            obj = userSelectionDict[seriesName]
            imageNumber = obj.returnImageNumber(self.selectedImageName)
            obj.updateLevels(imageNumber, intensity, contrast)
    except Exception as e:
        print('Error in DisplayImageColour.updateUserSelectedLevels: ' + str(e))
        logger.error('Error in DisplayImageColour.updateUserSelectedLevels: ' + str(e))


def updateImageLevels(self, imv, spinBoxIntensity, spinBoxContrast):
    """When the contrast and intensity values are adjusted using the spinboxes, 
    this function sets the corresponding values in the image being viewed. """
    try:
        centre = spinBoxIntensity.value()
        width = spinBoxContrast.value()
        halfWidth = width/2

        minLevel = centre - halfWidth
        maxLevel = centre + halfWidth
        #print("centre{}, width{}, minLevel{}, maxLevel{}".format(centre, width, minLevel, maxLevel))
        imv.setLevels(minLevel, maxLevel)
        imv.show()
    except Exception as e:
        print('Error in DisplayImageColour.updateImageLevels: ' + str(e))
        logger.error('Error in DisplayImageColour.updateImageLevels: ' + str(e))
        
        
def updateUserSelectedColourTable(self, cmbColours, chkBox, seriesName, firstImagePath):
    """When the colour table associated with an image is changed, the name of the new colour table
    is associated with that image in the list of lists userSelectionList, where each sublist 
    represents an image thus:
            [0] - Image name (used as key to search the list of lists)
            [1] - colour table name
            [2] - intensity level
            [3] - contrast level
        userSelectionList is initialised with default values in the function displayMultiImageSubWindow
    """
    try:
        if chkBox.isChecked() == False:
            #The apply user selection to whole series checkbox 
            #is not checked
            colourTable = cmbColours.currentText()
            if self.selectedImagePath:
                self.selectedImageName = os.path.basename(self.selectedImagePath)
            else:
                #Workaround for the fact that when the first image is displayed,
                #somehow self.selectedImageName looses its value.
                self.selectedImageName = os.path.basename(firstImagePath)
            
            global userSelectionDict
            obj = userSelectionDict[seriesName]
            imageNumber = obj.returnImageNumber(self.selectedImageName)
            if imageNumber != -1:
                #Associate the selected colour table with the image being viewed
                obj.updateColourTable(imageNumber, colourTable)
    except Exception as e:
        print('Error in DisplayImageColour.updateUserSelectedColourTable: ' + str(e))
        logger.error('Error in DisplayImageColour.updateUserSelectedColourTable: ' + str(e))      


def updateDICOM(self, seriesIDLabel, studyIDLabel, cmbColours, 
                spinBoxIntensity, spinBoxContrast):
        """This function is executed when the Update button 
        is clicked and it coordinates the calling of the functions, 
        updateWholeDicomSeries & updateDicomSeriesImageByImage."""
        try:
            logger.info("DisplayImageColour.updateDICOM called")
            seriesID = seriesIDLabel.text()
            studyID = studyIDLabel.text()
            colourMap = cmbColours.currentText()
            global userSelectionDict
            obj = userSelectionDict[seriesID]
            if obj.getSeriesUpdateStatus():
                levels = [spinBoxIntensity.value(), spinBoxContrast.value()]
                updateWholeDicomSeries(self, seriesID, studyID, colourMap, levels)
            if obj.getImageUpdateStatus():
                updateDicomSeriesImageByImage(self, seriesID, studyID, colourMap)
        except Exception as e:
            print('Error in DisplayImageColour.updateDICOM: ' + str(e))
            logger.error('Error in DisplayImageColour.updateDICOM: ' + str(e))


def updateWholeDicomSeries(self, seriesID, studyID, colourmap, levels, lut=None):
    """Updates every image in a DICOM series with one colour table and
            one set of levels"""
    try:
        logger.info("In DisplayImageColour.updateWholeDicomSeries")
        imagePathList = self.objXMLReader.getImagePathList(studyID, seriesID)

        #Iterate through list of images and update each image
        numImages = len(imagePathList)
        messageWindow.displayMessageSubWindow(self,
            "<H4>Updating {} DICOM files</H4>".format(numImages),
            "Updating DICOM images")
        messageWindow.setMsgWindowProgBarMaxValue(self, numImages)
        imageCounter = 0
        for imagePath in imagePathList:
            dataset = readDICOM_Image.getDicomDataset(imagePath) 
            # Update every DICOM file in the series                                     
            updatedDataset = saveDICOM_Image.updateSingleDicom(dataset, colourmap=colourmap, levels=levels, lut=lut)
            saveDICOM_Image.saveDicomToFile(updatedDataset, output_path=imagePath)
            imageCounter += 1
            messageWindow.setMsgWindowProgBarValue(self, imageCounter)
        messageWindow.closeMessageSubWindow(self)
    except Exception as e:
        print('Error in DisplayImageColour.updateWholeDicomSeries: ' + str(e))


def updateDicomSeriesImageByImage(self, seriesID, studyID, colourMap, lut=None):
    """Updates one or more images in a DICOM series each with potentially
    a different table and set of levels"""
    try:
        logger.info("In DisplayImageColour.updateDicomSeriesImageByImage")
       
        imagePathList = self.objXMLReader.getImagePathList(studyID, seriesID)

        #Iterate through list of images and update each image
        numImages = len(imagePathList)
        messageWindow.displayMessageSubWindow(self,
            "<H4>Updating {} DICOM files</H4>".format(numImages),
            "Updating DICOM images")
        messageWindow.setMsgWindowProgBarMaxValue(self, numImages)
        imageCounter = 0
        for imagePath in imagePathList:
            # Apply user selected colour table & levels to individual images in the series
            global userSelectionDict
            obj = userSelectionDict[seriesID]
            selectedColourMap, center, width = obj.returnUserSelection(imageCounter)
            if selectedColourMap != 'default' or center != -1 or width != -1:
                # Update an individual DICOM file in the series
                levels = [center, width]  
                dataset = readDICOM_Image.getDicomDataset(imagePath)
                updatedDataset = saveDICOM_Image.updateSingleDicom(dataset, colourmap=selectedColourMap, 
                                                    levels=levels, lut=lut)
                saveDICOM_Image.saveDicomToFile(updatedDataset, output_path=imagePath)
            imageCounter += 1
            messageWindow.setMsgWindowProgBarValue(self, imageCounter)
        messageWindow.closeMessageSubWindow(self)
    except Exception as e:
        print('Error in DisplayImageColour.updateDicomSeriesImageByImage: ' + str(e))