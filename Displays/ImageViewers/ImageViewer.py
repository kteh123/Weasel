"""Class ImageViewer creates an MDI subwindow for viewing an image or series of images 
    with the facility to change the colour table applied to the image
    and adjust the image intensity and contrast.  
    It also has multiple sliders for browsing series of images."""

from PyQt5 import QtCore 
from PyQt5.QtCore import  Qt
from PyQt5.QtGui import QPixmap, QIcon,  QCursor
from PyQt5.QtWidgets import (QFileDialog, QApplication,                           
                            QMessageBox, 
                            QWidget,
                            QHBoxLayout,
                            QVBoxLayout, 
                            QMdiSubWindow, 
                            QGroupBox, 
                            QDoubleSpinBox,
                            QPushButton,  
                            QLabel, 
                            QComboBox,
                            QSlider, 
                            QComboBox,
                            QListWidget,
                            QListWidgetItem,
                            QListView)

import os
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import math
import copy
from scipy.stats import iqr
import External.pyqtgraph as pg 
import DICOM.ReadDICOM_Image as ReadDICOM_Image
import DICOM.SaveDICOM_Image as SaveDICOM_Image


from Displays.ImageViewers.DataStructures.UserImageColourSelection import UserSelection
from Displays.ImageViewers.ComponentsUI.ImageSliders import ImageSliders as imageSliders
from Displays.ImageViewers.ComponentsUI.PixelValueLabel import PixelValueComponent 
from Displays.ImageViewers.ComponentsUI.ImageLevelsSpinBoxes import ImageLevelsSpinBoxes as imageLevelsSpinBoxes
from Displays.ImageViewers.ComponentsUI.FreeHandROI.Resources import * 

import logging
logger = logging.getLogger(__name__)

__author__ = "Steve Shillitoe"
#September 2021

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
    """This class inherits from the PyQt5 class QMdiSubWindow to create
    an MDI subwindow for viewing an image or series of images.
    It has the facility to change the colour table applied to the image
    and adjust the image intensity and contrast.  
    It also has multiple sliders for browsing series of images."""

    def __init__(self, weasel, dcm): 
        """
        When an object is created from the class ImageViewer, this function is called.
        It creates the MDI subwindow and adds it to the Weasel MDI area.

        If a series is to be viewed:

        1. It creates a data structure for storing user selected colour table 
            and image contrast and intensity data.

        2. It creates sliders for navigating the images in the series. There will be a
            main slider for navigating the whole DICOM series and auxiliary sliders to
            navigate subsets of images sorted by DICOM attributes.

        All the inner layouts and widgets are contained within one outer
        vertical layout created in the function setUpMainLayout.
        """
        try:
            super().__init__()

            self.subjectID = dcm.subjectID
            self.studyID = dcm.studyID
            self.seriesID = dcm.seriesID
            if dcm.__class__.__name__ == "Image":
                self.imagePathList = dcm.path
            elif dcm.__class__.__name__ == "Series":
                self.imagePathList = dcm.images

            self.selectedImagePath = ""
            self.imageNumber = -1
            self.colourTable = ""
            self.cmbColours = QComboBox()  
            self.lut = ""
            self.weasel = weasel

            if dcm.__class__.__name__ == "Image":
                self.isSeries = False
                self.isImage = True
                self.selectedImagePath = dcm.path
            else:
                self.isSeries = True
                self.isImage = False

            self.setWindowFlags(Qt.CustomizeWindowHint | 
                                          Qt.WindowCloseButtonHint | 
                                          Qt.WindowMinimizeButtonHint |
                                          Qt.WindowMaximizeButtonHint)
        
            height, width = self.weasel.getMDIAreaDimensions()
            #self.subWindowWidth = width
            #Set dimensions of the subwindow to fit the MDI area
            self.setGeometry(0, 0, width, height)
            #Consider using  0, 0, width/2, width/2 if not happy with initial size
            #Add subwindow to MDI
            self.weasel.mdiArea.addSubWindow(self)
             
            if self.isSeries: #DICOM series selected.
                #Create data structure for storing user selected
                #colour table and levels data
                self.userSelection = UserSelection(self.imagePathList)
                
            self.setUpMainLayout()

            self.setUpTopRowLayout()

            self.setUpGraphicsView()

            self.setUpLevelsSpinBoxes()
    
            self.setUpHistogram() #At the right-hand side of the image, adjusts levels
        
            if dcm.__class__.__name__ == "Image":
                self.displayPixelArrayOfSingleImage(self.imagePathList) 
            else:
                #DICOM series selected
                self.setUpImageSliders()

            self.show()
        except Exception as e:
            print('Error in ImageViewer.__init__: ' + str(e))
            logger.error('Error in ImageViewer.__init__: ' + str(e))


    def setUpMainLayout(self):
        """
        All the inner layouts and widgets are contained within one outer
        vertical layout called self.mainVerticalLayout that is created in 
        this function.
        """
        try:
            self.mainVerticalLayout = QVBoxLayout()
            self.widget = QWidget()
            self.widget.setLayout(self.mainVerticalLayout)
            self.setWidget(self.widget)
        except Exception as e:
            print('Error in ImageViewer.setUpMainLayout: ' + str(e))
            logger.error('Error in ImageViewer.setUpMainLayout: ' + str(e))


    def setUpImageSliders(self):
        try:
            logger.info("ImageViewer.setpUpImageSliders called.")
            #create an instance of the ImageSliders class
            self.slidersWidget = imageSliders(self.weasel, 
                                             self.subjectID, 
                                             self.studyID, 
                                             self.seriesID, 
                                             self.imagePathList)

            self.mainVerticalLayout.addLayout(
                    self.slidersWidget.getCustomSliderWidget())

            self.mainImageSlider = self.slidersWidget.getMainSlider()

            #This is how an object created from the ImageSliders class communicates
            #with an object created from the ImageViewer class via the former's
            #sliderMoved event, which passes the image path of the image being viewed
            #to ImageViewer's displayPixelArrayOfSingleImage function for display.
            self.slidersWidget.sliderMoved.connect(lambda imagePath: 
                                                   self.displayPixelArrayOfSingleImage(imagePath))
            #Display the first image in the viewer
            self.slidersWidget.displayFirstImage()
        except Exception as e:
            print('Error in ImageViewer.setUpImageSliders: ' + str(e))
            logger.error('Error in ImageViewer.setUpImageSliders: ' + str(e))


    def setUpColourTableDropDown(self):                                                  
        self.cmbColours.blockSignals(True)
        self.cmbColours.addItems(listColours)
        self.cmbColours.setCurrentIndex(0)
        self.cmbColours.blockSignals(False)
        self.cmbColours.setToolTip('Select a colour table to apply to the image')
        if self.isImage:
            self.cmbColours.currentIndexChanged.connect(self.applyColourTableToAnImage)
        elif self.isSeries:
            self.cmbColours.currentIndexChanged.connect(self.applyColourTableToSeries)

        self.colourTableLayout.addWidget(self.cmbColours)


    def setUpApplyUserSelectionButton(self):
        self.btnApply = QPushButton() 
        self.btnApply.setCheckable(True)
        self.btnApply.setIcon(QIcon(QPixmap(APPLY_SERIES_ICON)))
        self.btnApply.setToolTip(
                    "Click to apply colour table and levels selected by the user to the whole series")
        self.btnApply.clicked.connect(self.applyColourTableToSeries)


    def setUpUpdateUserSelectionToDICOMButton(self):
        self.btnUpdate = QPushButton() 
        self.btnUpdate.setIcon(QIcon(QPixmap(SAVE_ICON)))
        self.btnUpdate.setToolTip('Update DICOM with the new colour table, contrast & intensity levels')
        if self.isImage:
            self.btnUpdate.clicked.connect(self.updateSingleDicomImage)
        elif self.isSeries:
            self.btnUpdate.clicked.connect(self.updateDicomSeries)


    def setUpExportImageButton(self):
        self.btnExport = QPushButton() 
        self.btnExport.setIcon(QIcon(QPixmap(EXPORT_ICON)))
        self.btnExport.setToolTip('Exports the image to an external graphic file.')
        self.btnExport.clicked.connect(self.exportImage)


    def setUpResetButton(self):
        self.btnReset = QPushButton() 
        self.btnReset.setIcon(QIcon(QPixmap(RESET_ICON)))
        self.btnReset.setToolTip('Return to colour tables and levels in the DICOM file')


    def setUpColourTableGroupBox(self):
        self.colourTableLayout = QHBoxLayout()
        self.colourTableLayout.setContentsMargins(0, 2, 0, 0)
        self.colourTableLayout.setSpacing(5)
        self.colourTableGroupBox = QGroupBox()
        self.colourTableGroupBox.setFixedHeight(50)
        self.colourTableGroupBox.setLayout(self.colourTableLayout)

        self.setUpColourTableDropDown()

        self.setUpApplyUserSelectionButton()

        self.setUpUpdateUserSelectionToDICOMButton()  #To Do
  
        self.setUpExportImageButton()

        self.setUpResetButton()

        self.setUpDeleteImageButton()

        if self.isImage: 
            self.colourTableLayout.addWidget(self.btnReset)
            self.colourTableLayout.addWidget(self.btnUpdate)
            self.colourTableLayout.addWidget(self.btnExport)
            self.colourTableLayout.addWidget(self.deleteButton)
            self.btnReset.clicked.connect(lambda: self.displayPixelArrayOfSingleImage(self.imagePathList))                                                     
        elif self.isSeries:
            #Viewing a DICOM series, so show the Reset button
            #and Apply to Series checkbox
            self.colourTableLayout.addWidget(self.btnApply)  
            #Clicking Reset button deletes user selected colour table and contrast 
            #and intensity levelts and returns images to values in the original DICOM file.
            self.btnReset.clicked.connect(self.clearUserSelection)
            self.colourTableLayout.addWidget(self.btnReset)
            self.colourTableLayout.addWidget(self.btnUpdate)
            self.colourTableLayout.addWidget(self.btnExport)
            self.colourTableLayout.addWidget(self.deleteButton)
            self.cmbColours.activated.connect(self.updateImageUserSelection)


    def setUpImageLevelsGroupBox(self):
        """
        Creates an instance of the imageLevelsSpinBoxes
        custom composite component that
        comprises a horizontal layout containing two spinboxes, 
        one for adjusting the image intensity, 
        the other for adjusting the image contrast. 
        This composite component is added to a group box
        """
        self.levelsCompositeComponentLayout = imageLevelsSpinBoxes()
        self.imageLevelsGroupBox = QGroupBox()
        self.imageLevelsGroupBox.setFixedWidth(200)
        self.imageLevelsGroupBox.setFixedHeight(50)
        self.imageLevelsGroupBox.setLayout(
            self.levelsCompositeComponentLayout.getCompositeComponent())


    def setUpTopRowLayout(self):
        """
        In this function the horizontal layout is created and added to the
        main vertical layout. 
        This horizontal layout is used to contain the following in one row at the
        top of the MDI subwindow:
            1. The colour table group box
            2. The image levels group box
            3. The pixel levels group box
        """
        try:
            self.topRowMainLayout = QHBoxLayout()

            self.setUpColourTableGroupBox()
            self.setUpImageLevelsGroupBox()
            self.setUpPixelValueGroupBox()

            self.topRowMainLayout.addWidget(self.colourTableGroupBox)
            self.topRowMainLayout.addWidget(self.imageLevelsGroupBox) 
            self.topRowMainLayout.addWidget(self.pixelValueGroupBox)

            self.mainVerticalLayout.addLayout(self.topRowMainLayout)

            self.lblImageMissing = QLabel("<h4>Image Missing</h4>")
            self.lblImageMissing.hide()
            self.mainVerticalLayout.addWidget(self.lblImageMissing)
        except Exception as e:
            print('Error in ImageViewer.setUpTopRowLayout: ' + str(e))
            logger.error('Error in ImageViewer.setUpTopRowLayout: ' + str(e))


    def setUpGraphicsView(self):
        """
        Using the PyQtGraph package, creates a graphicsView widget for displaying DICOM images and adds
        it to the main vertical layout.
        """
        try:
            self.graphicsView = pg.ImageView(view=pg.PlotItem()) #view=pg.PlotItem() adds axes to image
            self.mainVerticalLayout.addWidget(self.graphicsView, stretch=1)
        except Exception as e:
            print('Error in ImageViewer.setUpGraphicsView: ' + str(e))
            logger.error('Error in ImageViewer.setUpGraphicsView: ' + str(e))


    def setUpDeleteImageButton(self):
        try:
            self.deleteButton = QPushButton()
            self.deleteButton.setToolTip(
                'Deletes the DICOM image being viewed')
            self.deleteButton.setIcon(QIcon(QPixmap(DELETE_ICON)))
            self.deleteButton.clicked.connect(self.deleteImageInMultiImageViewer)
            #self.imageLayout.addWidget(self.deleteButton)
        except Exception as e:
            print('Error in ImageViewer.setUpDeleteImageButton: ' + str(e))
            logger.error('Error in ImageViewer.setUpDeleteImageButton: ' + str(e))
 

    def setUpPixelValueGroupBox(self):
        pixelValueComponent = PixelValueComponent()
        self.lblPixelValue = pixelValueComponent.getLabel()
        self.pixelValueGroupBox = QGroupBox("Pixel Value")
        self.pixelValueGroupBox.setFixedHeight(50)
        self.pixelValueGroupBox.setLayout(pixelValueComponent.getLayout())  

  
    def getPixelValue(self, pos, imageNumber=1):
        """
        This function checks that the mouse pointer is over the
        image and when it is, it determines the value of the pixel
        under the mouse pointer and displays this in the label
        lblPixelValue.
        """
        try:
            container =  self.graphicsView.getView()
            if container.sceneBoundingRect().contains(pos): 
                mousePoint = container.getViewBox().mapSceneToView(pos) 
                x_i = math.floor(mousePoint.x())
                y_i = math.floor(mousePoint.y()) 
                #correct the y coordinate value so that it has a value
                #of 0 at the bottom left corner of the image rather than
                #at the top left corner of the image
                _, nY = self.pixelArray.shape
                correctedYCoord = nY -  y_i
                z_i =  imageNumber
                if ((len(np.shape(self.pixelArray)) == 2) 
                    and y_i >= 0 and y_i < self.pixelArray.shape [ 1 ] 
                    and x_i >= 0 and x_i < self.pixelArray.shape [ 0 ]): 
                        self.lblPixelValue.setText(
                        "<h4> {} @ X: {}, Y: {}, Z: {} ({})</h4>".format (self.pixelArray[ x_i, y_i ],x_i, correctedYCoord, z_i, ReadDICOM_Image.getImageTagValue(self.selectedImagePath, "SliceLocation")))
                elif ((len(np.shape(self.pixelArray)) == 3) 
                        and x_i >= 0 and x_i < self.pixelArray.shape [ 1 ] 
                        and y_i >= 0 and y_i < self.pixelArray.shape [ 2 ]):
                            z_i = math.floor(self.graphicsView.timeIndex(self.graphicsView.timeLine)[1])
                            self.lblPixelValue.setText(
                                "<h4> {} @ X: {}, Y: {}, Z: {} ({})</h4>".format (self.pixelArray[ x_i, y_i ],x_i, correctedYCoord, z_i, ReadDICOM_Image.getImageTagValue(self.selectedImagePath, "SliceLocation")))
                else:
                    self.lblPixelValue.setText("")
            else:
                self.lblPixelValue.setText("")
                   
        except Exception as e:
            print('Error in ImageViewer.getPixelValue: ' + str(e))
            logger.error('Error in ImageViewer.getPixelValue: ' + str(e))


    def setUpLevelsSpinBoxes(self):
        """Connects the valueChanged event of the two spinboxes used to adjust
           image contrast and intensity to the updateImageLevels function that updates 
           the contrast and intensity of the image.  Additionally, if a DICOM series
           is being viewed, the valueChanged event is connected to a function that saves
           the user selected image levels.
        """
        try:
            self.spinBoxIntensity, self.spinBoxContrast = self.levelsCompositeComponentLayout.getSpinBoxes()
            self.spinBoxIntensity.valueChanged.connect(self.updateImageLevels)
            self.spinBoxContrast.valueChanged.connect(self.updateImageLevels)
            if self.isSeries: 
                self.spinBoxIntensity.valueChanged.connect(self.updateImageUserSelection)
                self.spinBoxContrast.valueChanged.connect(self.updateImageUserSelection)
        except Exception as e:
            print('Error in ImageViewer.setUpLevelsSpinBoxes: ' + str(e))
            logger.error('Error in ImageViewer.setUpLevelsSpinBoxes: ' + str(e))


    def setUpHistogram(self):
        """
        Connects the histogram object on the right-handside of the image to the
        2 levels spinboxes, so they are updated when the histogram is adjusted.
        """
        self.histogramObject = self.graphicsView.getHistogramWidget().getHistogram()
        self.histogramObject.sigLevelsChanged.connect(self.getHistogramLevels)
        self.graphicsView.ui.roiBtn.hide()
        self.graphicsView.ui.menuBtn.hide()

    
    def deleteImageInMultiImageViewer(self):
        """When the Delete button is clicked on the multi image viewer,
        this function deletes the physical image, removes the 
        reference to it in the XML file and removes it from the image viewer.
        """
        try:
            logger.info("ImageViewer.deleteImageInMultiImageViewer called")
            imageName = os.path.basename(self.selectedImagePath)
            buttonReply = QMessageBox.question(self.weasel, 
                'Delete DICOM image', "You are about to delete image {}".format(imageName), 
                QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)

            if buttonReply == QMessageBox.Ok:
                #Advance the image sliders by one image unless we are
                #deleting the last image, then move the slider to the
                #first image in the list.
                

                #Delete physical file
                if os.path.exists(self.selectedImagePath):
                    os.remove(self.selectedImagePath)

                #Remove deleted image from the list
                self.imagePathList.remove(self.selectedImagePath)

                #Pass the new imagePathList to the sliders widget and
                #display the next image
                self.slidersWidget.imageDeleted(self.imagePathList)

                #Remove deleted image from the user selection 
                #data structure
                self.userSelection.deleteOneImageInUserSelection(os.path.basename(self.selectedImagePath))

                #Update the XML file
                #Get the series containing this image and count the images it contains
                #If it is the last image in a series then remove the
                #whole series from XML file
                #If it is not the last image in a series
                #just remove the image from the XML file 
                if len(self.imagePathList) == 0:
                    #no images left in the series, so remove it from the xml file
                    self.weasel.objXMLReader.removeOneSeriesFromStudy(self.subjectID, 
                                                                               self.studyID, 
                                                                               self.seriesID)
                elif len(self.imagePathList) > 0:
                    #1 or more images in the series, 
                    #so just remove the image from its series in the xml file
                    self.weasel.objXMLReader.removeOneImageFromSeries(self.subjectID, 
                        self.studyID, self.seriesID, self.selectedImagePath)

                #Update tree view with xml file modified above
                self.weasel.treeView.refreshDICOMStudiesTreeView()

        except Exception as e:
            print('Error in ImageViewer.deleteImageInMultiImageViewer: ' + str(e))
            logger.error('Error in ImageViewer.deleteImageInMultiImageViewer: ' + str(e))


    def deleteImageInMultiImageViewer_old(self):
        """When the Delete button is clicked on the multi image viewer,
        this function deletes the physical image, removes the 
        reference to it in the XML file and removes it from the image viewer.
        """
        try:
            logger.info("ImageViewer.deleteImageInMultiImageViewer called")
            lastSliderPosition = self.mainImageSlider.value()
            #currentImagePath = self.imagePathList[self.mainImageSlider.value()-1]
            imageName = os.path.basename(self.selectedImagePath)
            #print ('study id {} series id {}'.format(studyName, seriesName))
            buttonReply = QMessageBox.question(self.weasel, 
                'Delete DICOM image', "You are about to delete image {}".format(imageName), 
                QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)

            if buttonReply == QMessageBox.Ok:
                #Delete physical file
                if os.path.exists(self.selectedImagePath):
                    os.remove(self.selectedImagePath)
                #Remove deleted image from the list
                self.imagePathList.remove(self.selectedImagePath)

                if len(self.imagePathList) == 0:
                    #Only redisplay the multi-image viewer if there
                    #are still images in the series to display
                    #The image list is empty, so do not redisplay
                    #multi image viewer 
                    pass   
                elif len(self.imagePathList) == 1:
                    #There is only one image left in the display
                    self.mainImageSlider.setValue(1)
                    #displayMultiImageSubWindow(self, imageList, subjectID, studyName, seriesName)
                elif len(self.imagePathList) + 1 == lastSliderPosition:    
                        #we are deleting the last image in the series of images
                        #so move the slider back to the penultimate image in list 
                    self.mainImageSlider.setValue(len(self.imagePathList))
                    #displayMultiImageSubWindow(self, imageList, subjectID,
                                        #studyName, seriesName, len(imageList))
                else:
                    #We are deleting an image at the start of the list
                    #or in the body of the list. Move slider forwards to 
                    #the next image in the list.
                    self.mainImageSlider.setValue(lastSliderPosition)
                    #displayMultiImageSubWindow(self, imageList, subjectID,
                    #                    studyName, seriesName, lastSliderPosition)
     
                #Now update XML file
                #Get the series containing this image and count the images it contains
                #If it is the last image in a series then remove the
                #whole series from XML file
                #If it is not the last image in a series
                #just remove the image from the XML file 
                if len(self.imagePathList) == 0:
                    #no images left in the series, so remove it from the xml file
                    self.weasel.objXMLReader.removeOneSeriesFromStudy(self.subjectID, 
                                                                               self.studyID, 
                                                                               self.seriesID)
                elif len(self.imagePathList) > 0:
                    #1 or more images in the series, 
                    #so just remove the image from its series in the xml file
                    self.weasel.objXMLReader.removeOneImageFromSeries(self.subjectID, 
                        self.studyID, self.seriesID, self.selectedImagePath)
                #Update tree view with xml file modified above
                self.weasel.treeView.refreshDICOMStudiesTreeView()
        except Exception as e:
            print('Error in ImageViewer.deleteImageInMultiImageViewer: ' + str(e))
            logger.error('Error in ImageViewer.deleteImageInMultiImageViewer: ' + str(e))


    def exportImage(self):
        """Function executed when the Export button is clicked.  
        It exports the DICOM image and its colour table to a png graphics file.
        It launches a file dialog, so that the user can select the file path to 
        the png file in which the exported file will be stored. It also collects 
        the name of the image colour table and the image levels.
        """
        try:
            self.colourTable = self.cmbColours.currentText()
            #Default file name is derived from the DICOM image name
            defaultImageName = os.path.basename(self.selectedImagePath) 
            #remove .dcm extension
            defaultImageName = os.path.splitext(defaultImageName)[0] + '.png'
            #Display a save file dialog to get the full file path and name of
            #where to export the DICOM image & its colour table to a png file
            fileName, _ = QFileDialog.getSaveFileName(caption="Enter a file name", 
                                                        directory=defaultImageName, 
                                                        filter="*.png")

            #Test if the user has selected a file name
            if fileName:
                self.exportImageViaMatplotlib(fileName)
        except Exception as e:
            print('Error in ImageViewer.exportImage: ' + str(e))
            logger.error('Error in ImageViewer.exportImage: ' + str(e))


    def exportImageViaMatplotlib(self, fileName):
        """This function uses matplotlib.pyplot to save the DICOM image being viewed 
        and its colour table in a png file with the path+filename in fileName. 
    
        Input Parmeters
        ***************
            fileName - file path to the png file in which the exported file will be stored.
        """ 
        try:
            #axisOrder = pg.getConfigOption('imageAxisOrder') 
            #if axisOrder =='row-major':
            #Transpose the array so as to match the screen image 
            # (a transpose is already applied when reading DICOM image)
            pixelArray = np.transpose(self.pixelArray)
            cmap = plt.get_cmap(self.colourTable)
            pos = plt.imshow(pixelArray, cmap=cmap)
            minValue, maxValue = self.graphicsView.getLevels()
            plt.clim(int(minValue), int(maxValue))
            cBar = plt.colorbar()
            cBar.minorticks_on()
            plt.savefig(fname=fileName)
            plt.close()
            QMessageBox.information(self, "Export Image", "Image Saved")
        except Exception as e:
            print('Error in ImageViewer.exportImageViaMatplotlib: ' + str(e))
            logger.error('Error in ImageViewer.exportImageViaMatplotlib: ' + str(e))

    
    def updateImageLevels(self):
        """When the contrast and intensity values are adjusted using the spinboxes, 
        this function sets the corresponding values in the image being viewed. 
        """
        try:
            centre = self.spinBoxIntensity.value()
            width = self.spinBoxContrast.value()
            halfWidth = width/2
            minimumValue = centre - halfWidth
            maximumValue = centre + halfWidth
            self.graphicsView.setLevels(minimumValue, maximumValue)
            self.graphicsView.show()
        except Exception as e:
            print('Error in ImageViewer.updateImageLevels: ' + str(e))
            logger.error('Error in ImageViewer.updateImageLevels: ' + str(e))


    def getHistogramLevels(self):
        """
        This function ensures that the intensity and contrast spinboxes
        show the correct values when the histogram on the right of the
        image is manually adjusted.
        
        The max and min levels of the image are retrieved from the 
        graphicsView object in pyqtGraph and used to calculate
        the intensity (centre) and contrast (width) values of the image.
        Then the contrast & intensity spinboxes are set to these values.
        """
        minLevel, maxLevel =  self.graphicsView.getLevels()
        width = maxLevel - minLevel
        centre = minLevel + (width/2)
        self.spinBoxIntensity.setValue(centre)
        self.spinBoxContrast.setValue(width)


    def getColourTableForThisImage(self):
        try:
            logger.info("ImageViewer.getColourTableForThisImage called")
            if self.isSeries:
                if self.userSelection.getSeriesUpdateStatus():
                    self.colourTable = self.cmbColours.currentText()
                elif self.userSelection.getImageUpdateStatus():
                    imageName = os.path.basename(self.selectedImagePath)
                    self.colourTable, _, _ = self.userSelection.returnUserSelection(imageName)  
                    if self.colourTable == 'default':
                        self.colourTable, self.lut = ReadDICOM_Image.getColourmap(self.selectedImagePath)
                else:  #no user selection, so get colour table saved to DICOM
                    self.colourTable, self.lut = ReadDICOM_Image.getColourmap(self.selectedImagePath)
            elif self.isImage: 
                self.colourTable, self.lut = ReadDICOM_Image.getColourmap(self.selectedImagePath)
        except Exception as e:
                print('Error in ImageViewer.getColourTableForThisImage: ' + str(e))
                logger.error('Error in ImageViewer.getColourTableForThisImage: ' + str(e))


    def getAndSetLevels(self):
        try:
            success = False
            if self.isSeries: 
                success, minimumValue, maximumValue = self.returnUserSelectedLevels()
                width = maximumValue - minimumValue
                centre = minimumValue + (width/2)
            if not success or self.isImage:
                centre, width, maximumValue, minimumValue = self.readLevelsFromDICOMImage()

            self.levelsCompositeComponentLayout.blockLevelsSpinBoxSignals(True)
            self.spinBoxIntensity.setValue(centre)
            self.spinBoxContrast.setValue(width)
            self.levelsCompositeComponentLayout.blockLevelsSpinBoxSignals(False)
            return maximumValue, minimumValue
        except Exception as e:
            print('Error in ImageViewer.getAndSetLevels: ' + str(e))
            logger.exception('Error in ImageViewer.getAndSetLevels: ' + str(e))  


    def getAndSetLevelsSpinBoxStepSize(self, maximumValue, minimumValue):
        try:
            if (minimumValue < 1 and minimumValue > -1) and (maximumValue < 1 and maximumValue > -1):
                spinBoxStep = float((maximumValue - minimumValue) / 200) # It takes 100 clicks to walk through the middle 50% of the signal range
            else:
                spinBoxStep = int((maximumValue - minimumValue) / 200) # It takes 100 clicks to walk through the middle 50% of the signal range
        
            self.spinBoxIntensity.setSingleStep(spinBoxStep)
            self.spinBoxContrast.setSingleStep(spinBoxStep)
        except Exception as e:
            print('Error in ImageViewer.getAndSetLevelsSpinBoxStepSize: ' + str(e))
            logger.exception('Error in ImageViewer.getAndSetLevelsSpinBoxStepSize: ' + str(e))

    
    def displayPixelArrayOfSingleImage(self, imagePath):
        """Displays an image's pixel array in a pyqtGraph imageView widget 
        & sets its colour table, contrast and intensity levels. 
        Also, sets the contrast and intensity in the associated histogram.
        """
        try:
            logger.info("ImageViewer.displayPixelArrayOfSingleImage called")
            self.selectedImagePath = imagePath
            imageName = os.path.basename(self.selectedImagePath)
            self.pixelArray = ReadDICOM_Image.returnPixelArray(self.selectedImagePath)

            imageNumber = 1
                
            self.lut = None

            #Get colour table of the image to be displayed
            self.getColourTableForThisImage()

            #display above colour table in colour table dropdown list
            self.displayColourTableInComboBox()

            self.setWindowTitle(self.subjectID + ' - ' + self.studyID + ' - '+ self.seriesID + ' - ' 
                        + imageName)

            #Check that pixel array holds an image & display it
            if self.pixelArray is None:
                #the image is missing, so show a black screen
                self.lblImageMissing.show()
                self.deleteButton.hide()
                self.graphicsView.setImage(np.array([[0,0,0],[0,0,0]]))  
            else:
                self.lblImageMissing.hide() 
                maximumValue, minimumValue = self.getAndSetLevels()
                
                if len(np.shape(self.pixelArray)) < 3:
                        self.graphicsView.setImage(self.pixelArray, 
                                                autoHistogramRange=True, 
                                                levels=(minimumValue, maximumValue))
                else:
                        self.graphicsView.setImage(self.pixelArray, 
                                                autoHistogramRange=True, 
                                                xvals=np.arange(np.shape(self.pixelArray)[0] + 1), 
                                                levels=(minimumValue, maximumValue))
                
                self.getAndSetLevelsSpinBoxStepSize(maximumValue, minimumValue)
        
                #Add Colour Table or look up table To Image
                self.setPgColourMap()  
  
                self.graphicsView.getView().scene().sigMouseMoved.connect(
                        lambda pos: self.getPixelValue(pos))
                self.graphicsView.getView().scene().sigMouseDragged.connect(
                        lambda ev: self.adjustLevelsByRightButtonDrag(ev))
        except Exception as e:
            print('Error in ImageViewer.displayPixelArrayOfSingleImage: ' + str(e))
            logger.exception('Error in ImageViewer.displayPixelArrayOfSingleImage: ' + str(e))


    def adjustLevelsByRightButtonDrag(self, ev):
        try:
            self.levelsCompositeComponentLayout.blockLevelsSpinBoxSignals(True)
            centre = self.spinBoxIntensity.value()
            width = self.spinBoxContrast.value()
            delta = ev.screenPos() - ev.lastScreenPos()
            if float(centre / np.shape(self.pixelArray)[1]) > 0.01:
                step_y = float(centre / np.shape(self.pixelArray)[1])
            else:
                step_y = 0.01
            if float(width / np.shape(self.pixelArray)[0]) > 0.01:
                step_x = float(width/ np.shape(self.pixelArray)[0])
            else:
                step_x = 0.01
            horizontalDiff = step_y * delta.y()
            verticalDiff = step_x * delta.x() # Maybe put a minus sign here
            newCentre = centre + horizontalDiff
            newWidth = width + verticalDiff
            self.spinBoxIntensity.setValue(newCentre)
            self.spinBoxContrast.setValue(newWidth)
            self.updateImageLevels()
            self.levelsCompositeComponentLayout.blockLevelsSpinBoxSignals(False)
        except Exception as e:
            print('Error in ImageViewer.adjustLevelsByRightButtonDrag: ' + str(e))
            logger.exception('Error in ImageViewer.adjustLevelsByRightButtonDrag: ' + str(e))


    def updateImageUserSelection(self):
        """
            """
        try:
            logger.info('updateImageUserSelection called')
            if not self.btnApply.isChecked():
                #The apply user selection to whole series checkbox 
                #is not checked
                self.colourTable = self.cmbColours.currentText()
                intensity = self.spinBoxIntensity.value()
                contrast = self.spinBoxContrast.value()

                if self.selectedImagePath:
                    self.selectedImageName = os.path.basename(self.selectedImagePath)
                else:
                    #Workaround for the fact that when the first image is displayed,
                    #somehow self.selectedImageName looses its value.
                    self.selectedImageName = os.path.basename(self.imagePathList[0])
            
                #print("self.selectedImageName ={}".format(self.selectedImageName))
                #print("colourTable = {}".format(self.colourTable))
                self.userSelection.updateUserSelection(self.selectedImageName, self.colourTable, intensity, contrast)
        except Exception as e:
            print('Error in ImageViewer.updateImageUserSelection: ' + str(e))
            logger.error('Error in ImageViewer.updateImageUserSelection: ' + str(e))


    def applyColourTableToAnImage(self):
        self.colourTable = self.cmbColours.currentText()
        if self.colourTable.lower() == 'custom':
            self.colourTable = 'gray'                
            self.displayColourTableInComboBox()   
        self.setPgColourMap()


    def applyColourTableToSeries(self): 
        """This function applies a user selected colour map to the current image.
        If the Apply checkbox is checked then the new colour map is also applied to 
        the whole series of DICOM images by setting a boolean flag to True.
        """
        try:
            self.applyColourTableToAnImage()
        
            if self.btnApply.isChecked():
                self.btnApply.setStyleSheet("background-color: red")
                self.userSelection.setSeriesUpdateStatus(True)
                self.userSelection.setImageUpdateStatus(False)
            else:
                self.userSelection.setSeriesUpdateStatus(False)
                self.btnApply.setStyleSheet(
                "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
                )     
        except Exception as e:
            print('Error in ImageViewer.applyColourTableToSeries: ' + str(e))
            logger.error('Error in ImageViewer.applyColourTableToSeries: ' + str(e))


    def clearUserSelection(self):
        """This function removes the user selected colour tables, contrast & intensity values from
        the list of image lists that hold these values.  They are reset to the default values of
        'default' for the colour table and -1 for the contrast & intensity values
        """
        self.userSelection.clearUserSelection()

        #reload current image to display it without user selected 
        #colour table and levels.
        #This is done by advancing the slider and then moving it  
        #back to the original image
        imageNumber = self.slidersWidget.getMainSlider().value() #self.mainImageSlider.value()
        if imageNumber == 1:
            tempNumber = imageNumber + 1
        else:
            tempNumber = imageNumber - 1

        self.slidersWidget.getMainSlider().setValue(tempNumber)
        self.slidersWidget.getMainSlider().setValue(imageNumber)
    

    def returnUserSelectedLevels(self):
        """
        When the user has selected new image levels that must override the 
        levels saved in the DICOM series/image, this function returns those selected levels
        Output parameters
        *****************
        success - boolean, set to true if level values are successfully retrieved
        maximumValue - Maximum pixel value in the image
        minimumValue - Minimum pixel value in the image
        """
        try:
            logger.info("ImageViewer.returnUserSelectedLevels called")
      
            minimumValue = -1
            maximumValue = -1
            success = False
            
            if self.userSelection.getSeriesUpdateStatus():
                #Get the ordinal number of the image being viewed in the image list
                currentImageNumber = self.slidersWidget.getMainSlider().value() - 1
                centre = self.spinBoxIntensity.value()
                width = self.spinBoxContrast.value()
                #apply contrast and intensity values
                #selected in the GUI spinboxes
                #for the whole series to this image
                minimumValue = centre - (width/2)
                maximumValue = centre + (width/2)
                success = True
            elif self.userSelection.getImageUpdateStatus():
                #the user has opted to change the levels of individual images
                #in a series.
                #if user selected levels exist for this image, retrieve them
                imageName = os.path.basename(self.selectedImagePath)
                _, centre, width = self.userSelection.returnUserSelection(imageName) 
                if centre != -1:
                    #saved values exist, so use them
                    minimumValue = centre - (width/2)
                    maximumValue = centre + (width/2)
                    success = True

            return success, minimumValue, maximumValue
        except Exception as e:
            print('Error in ImageViewer.returnUserSelectedLevels: ' + str(e))
            logger.error('Error in ImageViewer.returnUserSelectedLevels: ' + str(e))

    def setPgColourMap(self):
        """This function converts a matplotlib colour map into
        a colour map that can be used by the pyqtGraph imageView widget.
        """
        try:
            if self.colourTable == None or self.colourTable == "":
                self.colourTable = 'gray'

            if self.cmbColours is not None:
                self.displayColourTableInComboBox()   
        
            if self.colourTable == 'custom':
                colors = self.lut
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
            print('Error in ImageViewer.setPgColourMap: ' + str(e))
            logger.error('Error in ImageViewer.setPgColourMap: ' + str(e))


    def readLevelsFromDICOMImage(self): 
        """Reads levels directly from the DICOM image
        Output Parameters
        *****************
        centre - Image intensity
        width - Image contrast
        maximumValue - Maximum pixel value in the image
        minimumValue - Minimum pixel value in the image
        """
        try:
            logger.info("ImageViewer.readLevelsFromDICOMImage called")
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
                if [0x2005, 0x100E] in dataset: # 'Philips Rescale Slope'
                    centre = centre / dataset[(0x2005, 0x100E)].value
                    width = width / dataset[(0x2005, 0x100E)].value
                maximumValue = centre + width/2
                minimumValue = centre - width/2
            elif dataset and hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
                # In Enhanced MRIs, this display will retrieve the centre and width values of the first slice
                slope = dataset.PerFrameFunctionalGroupsSequence[0].PixelValueTransformationSequence[0].RescaleSlope
                intercept = dataset.PerFrameFunctionalGroupsSequence[0].PixelValueTransformationSequence[0].RescaleIntercept
                centre = dataset.PerFrameFunctionalGroupsSequence[0].FrameVOILUTSequence[0].WindowCenter # * slope + intercept
                width = dataset.PerFrameFunctionalGroupsSequence[0].FrameVOILUTSequence[0].WindowWidth # * slope
                if [0x2005, 0x100E] in dataset: # 'Philips Rescale Slope'
                    centre = centre / dataset[(0x2005, 0x100E)].value
                    width = width / dataset[(0x2005, 0x100E)].value
                maximumValue = centre + width/2
                minimumValue = centre - width/2 
            else:
                minimumValue = np.amin(self.pixelArray) if (np.median(self.pixelArray) - iqr(self.pixelArray, 
                rng=(1, 99))/2) < np.amin(self.pixelArray) else np.median(self.pixelArray) - iqr(self.pixelArray, rng=(1, 99))/2
                maximumValue = np.amax(self.pixelArray) if (np.median(self.pixelArray) + iqr(self.pixelArray, rng=(
                1, 99))/2) > np.amax(self.pixelArray) else np.median(self.pixelArray) + iqr(self.pixelArray, rng=(1, 99))/2
                centre = minimumValue + (abs(maximumValue) - abs(minimumValue))/2
                width = maximumValue - abs(minimumValue)

            return centre, width, maximumValue, minimumValue
        except Exception as e:
            print('Error in ImageViewer.readLevelsFromDICOMImage: ' + str(e))
            logger.error('Error in ImageViewer.readLevelsFromDICOMImage: ' + str(e))


    def updateSingleDicomImage(self):
        """
        This function is executed when the Update button 
        is clicked and the user is viewing a singe DICOM image.
        """
        try:
            buttonReply = QMessageBox.question(self.weasel, 
                'Update DICOM', "You are about to overwrite this DICOM File. Please click OK to proceed.", 
                QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
            if buttonReply == QMessageBox.Ok:
                SaveDICOM_Image.updateSingleDicomImage(self.weasel, 
                                                    self.spinBoxIntensity,
                                                    self.spinBoxContrast,
                                                    self.imagePathList,
                                                    self.seriesID,
                                                    self.studyID,
                                                    self.colourTable,
                                                    lut=None)
        except Exception as e:
            print('Error in ImageViewer.updateSingleDicomImage: ' + str(e))
            logger.error('Error in ImageViewer.updateSingleDicomImage: ' + str(e))


    def updateDicomSeries(self):
        """
        This function is executed when the Update button 
        is clicked and the user is viewing a series of DICOM images.
        It coordinates the calling of the functions, 
        updateWholeDicomSeries & updateDicomSeriesImageByImage.
        """
        try:
            logger.info("ImageViewer.updateDICOM called")
            buttonReply = QMessageBox.question(self.weasel, 
                          'Update DICOM', "You are about to overwrite this series of DICOM Files. Please click OK to proceed.", 
                          QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
            if buttonReply == QMessageBox.Ok:
                colourTable = self.cmbColours.currentText()
                if self.userSelection.getSeriesUpdateStatus():
                    levels = [self.spinBoxIntensity.value(), self.spinBoxContrast.value()]
                    self.updateWholeDicomSeries(levels)
                if self.userSelection.getImageUpdateStatus():
                    self.updateDicomSeriesImageByImage() 
        except Exception as e:
            print('Error in ImageViewer.updateDicomSeries: ' + str(e))
            logger.error('Error in ImageViewer.updateDicomSeries: ' + str(e))


    def updateWholeDicomSeries(self, levels):
        """
        Updates every image in a DICOM series with one colour table and
                one set of levels
            
          Input Parmeters
          ***************
            levels  - 2 item list containing the image contrast and intensity values as integers, 
                        [contrast, intensity]
            """
        try:
            logger.info("In ImageViewer.updateWholeDicomSeries")

            #Iterate through list of images and update each image
            numImages = len(self.imagePathList)
            self.weasel.progress_bar(msg="<H4>Updating {} DICOM files</H4>".format(numImages))
            self.weasel.progressBar.set_maximum(numImages)
            imageCounter = 0
            for imagePath in self.imagePathList:
                dataset = ReadDICOM_Image.getDicomDataset(imagePath) 
                # Update every DICOM file in the series                                     
                updatedDataset = SaveDICOM_Image.updateSingleDicom(dataset, colourmap=self.colourTable, 
                                                                   levels=levels, lut=self.lut)
                SaveDICOM_Image.saveDicomToFile(updatedDataset, output_path=imagePath)
                imageCounter += 1
                self.weasel.progressBar.set_value(imageCounter)
            self.weasel.progressBar.close()
        except Exception as e:
            print('Error in ImageViewer.updateWholeDicomSeries: ' + str(e))


    def updateDicomSeriesImageByImage(self):
        """Updates one or more images in a DICOM series each with potentially
        a different table and set of levels
        """
        try:
            logger.info("In ImageViewer.updateDicomSeriesImageByImage")
       
            #Iterate through list of images and update each image
            numImages = len(self.imagePathList)
            self.weasel.progress_bar(msg="<H4>Updating {} DICOM files</H4>".format(numImages))
            self.weasel.progressBar.set_maximum(numImages)
            imageCounter = 0
       
            for imageCounter, imagePath in enumerate(self.imagePathList, 0):
                #print('In updateDicomSeriesImageByImage, series name={}'.format(seriesName))
                # Apply user selected colour table & levels to individual images in the series
                imageName = os.path.basename(imagePath)
                selectedColourMap, center, width = self.userSelection.returnUserSelection(imageName)
                #print('selectedColourMap, center, width = {}, {}, {}'.format(selectedColourMap, center, width))
                if selectedColourMap != 'default' and center != -1 and width != -1:
                    # Update an individual DICOM file in the series
                    #print('In If, imageCounter = {}, imagePath={}'.format(imageCounter, imagePath))
                    levels = [center, width]  
                    dataset = ReadDICOM_Image.getDicomDataset(imagePath)
                    updatedDataset = SaveDICOM_Image.updateSingleDicom(dataset, colourmap=selectedColourMap, 
                                                        levels=levels, lut=None)
                    SaveDICOM_Image.saveDicomToFile(updatedDataset, output_path=imagePath)
                self.weasel.progressBar.set_value(imageCounter)
            self.weasel.progressBar.close()
        except Exception as e:
            print('Error in ImageViewer.updateDicomSeriesImageByImage: ' + str(e))


    def displayColourTableInComboBox(self):
        """
        This function causes the combobox widget cmbColours to 
        display the name of the colour table stored in the string
        variable colourTable. 
        """
        try:
            self.cmbColours.blockSignals(True)
            self.cmbColours.setCurrentText(self.colourTable)
            self.cmbColours.blockSignals(False)
        except Exception as e:
                print('Error in ImageViewer.displayColourTableInComboBox: ' + str(e))
                logger.error('Error in ImageViewer.displayColourTableInComboBox: ' + str(e))