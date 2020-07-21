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
import logging
logger = logging.getLogger(__name__)

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


def displayImageSubWindow(self, derivedImagePath=None):
        """
        Creates a subwindow that displays the DICOM image contained in pixelArray. 
        """
        try:
            logger.info("displayImage.displayImageSubWindow called")
            pixelArray = readDICOM_Image.returnPixelArray(self.selectedImagePath)
            colourTable, lut = readDICOM_Image.getColourmap(self.selectedImagePath)
            imageViewer, layout, lblImageMissing, subWindow = \
                displayImageCommon.setUpImageViewerSubWindow(self)
            windowTitle = displayImageCommon.getDICOMFileData(self)
            subWindow.setWindowTitle(windowTitle)

            if derivedImagePath:
                lblHiddenImagePath = QLabel(derivedImagePath)
            else:
                lblHiddenImagePath = QLabel(self.selectedImagePath)
            lblHiddenImagePath.hide()
            lblHiddenStudyID = QLabel()
            lblHiddenStudyID.hide()
            lblHiddenSeriesID = QLabel()
            lblHiddenSeriesID.hide()
            
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
                                    imv, colourTable,
                                    cmbColours, lut)  
        except Exception as e:
            print('Error in displayImage.displayImageSubWindow: ' + str(e))
            logger.error('Error in  displayImage.displayImageSubWindow: ' + str(e)) 


def displayMultiImageSubWindow(self, imageList, studyName, 
                     seriesName, sliderPosition = -1):
        """
        Creates a subwindow that displays all the DICOM images in a series. 
        A slider allows the user to navigate  through the images.  A delete
        button allows the user to delete the image they are viewing.
        """
        try:
            logger.info("displayImage.displayMultiImageSubWindow called")
            self.overRideSavedColourmapAndLevels = False
            self.applyUserSelection = False
            imageViewer, layout, lblImageMissing, subWindow = \
                displayImageCommon.setUpImageViewerSubWindow(self)

            #set up list of lists to hold user selected colour table and level data
            self.userSelectionList = [[os.path.basename(imageName), 'default', -1, -1]
                                for imageName in imageList]
            
            
            #Study ID & Series ID are stored locally on the
            #sub window in case the user wishes to delete an
            #image in the series.  They may have several series
            #open at once, so the selected series on the treeview
            #may not the same as that from which the image is
            #being deleted.

            lblHiddenImagePath = QLabel('')
            lblHiddenImagePath.hide()
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
                                               imageSlider, showReleaseButton=True)

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
            print('Error in displayImage.displayMultiImageSubWindow: ' + str(e))
            logger.error('Error in displayImage.displayMultiImageSubWindow: ' + str(e))


def setUpColourTools(self, layout, imv,
            imageOnlySelected,
            lblHiddenImagePath,
            lblHiddenSeriesID,
            lblHiddenStudyID, spinBoxIntensity, spinBoxContrast,             
            imageSlider = None, showReleaseButton = False):
        try:
            logger.info("displayImageColour.setUpColourTools called")
            groupBoxColour = QGroupBox('Colour Table')
            groupBoxLevels = QGroupBox('Levels')
            gridLayoutColour = QGridLayout()
            levelsLayout = QGridLayout()
            groupBoxColour.setLayout(gridLayoutColour)
            groupBoxLevels.setLayout(levelsLayout)
            layout.addWidget(groupBoxColour)

            chkApply = QCheckBox("Apply Selection to whole series")
            chkApply.stateChanged.connect(lambda:applyColourTableAndLevelsToSeries(self, imv, 
                                                                                        cmbColours, 
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
                      applyColourTableAndLevelsToSeries(self, imv, cmbColours, chkApply))

            btnUpdate = QPushButton('Update') 
            btnUpdate.setToolTip('Update DICOM with the new colour table')

            if imageOnlySelected:
                #only a single image is being viewed
                 btnUpdate.clicked.connect(lambda:saveDICOM_Image.updateSingleDicomImage
                                          (self, 
                                           spinBoxIntensity, spinBoxContrast,
                                           lblHiddenImagePath.text(),
                                                 lblHiddenSeriesID.text(),
                                                 lblHiddenStudyID.text(),
                                                 cmbColours.currentText(),
                                                 lut=None))
            else:
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
            spinBoxIntensity.setMaximum(100000.00)
            spinBoxContrast.setMaximum(100000.00)
            spinBoxIntensity.setWrapping(True)
            spinBoxContrast.setWrapping(True)

            if imageOnlySelected:
                spinBoxIntensity.valueChanged.connect(lambda: changeSpinBoxLevels(self,
                imv,spinBoxIntensity, spinBoxContrast))
                spinBoxContrast.valueChanged.connect(lambda: changeSpinBoxLevels(self,
                imv,spinBoxIntensity, spinBoxContrast))
            else:
                spinBoxIntensity.valueChanged.connect(lambda: changeSpinBoxLevels(self,
                    imv,spinBoxIntensity, spinBoxContrast, chkApply))
                spinBoxContrast.valueChanged.connect(lambda: changeSpinBoxLevels(self,
                    imv,spinBoxIntensity, spinBoxContrast, chkApply ))

            levelsLayout.addWidget(lblIntensity, 0,0)
            levelsLayout.addWidget(spinBoxIntensity, 0, 1)
            levelsLayout.addWidget(lblContrast, 0,2)
            levelsLayout.addWidget(spinBoxContrast, 0,3)
            gridLayoutColour.addWidget(cmbColours,0,0)

            if showReleaseButton:
                gridLayoutColour.addWidget(chkApply,0,1)
                btnReset = QPushButton('Reset') 
                btnReset.setToolTip('Return to colour tables and levels in the DICOM file')
                btnReset.clicked.connect(lambda: clearUserSelection(self, imageSlider))
                gridLayoutColour.addWidget(btnReset,0,2)
                gridLayoutColour.addWidget(btnUpdate,1,1)
                gridLayoutColour.addWidget(btnExport,1,2)
                gridLayoutColour.addWidget(groupBoxLevels, 2, 0, 1, 3)
                cmbColours.activated.connect(lambda:
                      updateUserSelectedColourTable(self, cmbColours, chkApply, spinBoxIntensity, spinBoxContrast))
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
                          imv, colourTable, cmbColours, lut=None,
                          multiImage=False, deleteButton=None):
        try:
            logger.info("displayImage.displayPixelArray called")
            if deleteButton is None:
                #create dummy button to prevent runtime error
                deleteButton = QPushButton()
                deleteButton.hide()

            #Check that pixel array holds an image & display it
            if pixelArray is None:
                lblImageMissing.show()
                if multiImage:
                    deleteButton.hide()
                imv.setImage(np.array([[0,0,0],[0,0,0]]))  
            else:
                if self.overRideSavedColourmapAndLevels:
                    centre = spinBoxIntensity.value()
                    width = spinBoxContrast.value()
                    minimumValue = centre - (width/2)
                    maximumValue = centre + (width/2)
                elif self.applyUserSelection:
                    _, centre, width = returnUserSelection(self, currentImageNumber) 
                    if centre != -1:
                        minimumValue = centre - (width/2)
                        maximumValue = centre + (width/2)
                    else:
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
                else:
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

                if multiImage:
                    deleteButton.show()
        except Exception as e:
            print('Error in displayImage.displayPixelArray: ' + str(e))
            logger.error('Error in displayImage.displayPixelArray: ' + str(e))


def blockHistogramSignals(imgView, block):
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
            logger.info("displayImage.imageSliderMoved called")
            #imageNumber = self.imageSlider.value()
            currentImageNumber = imageNumber - 1
            if currentImageNumber >= 0:
                self.selectedImagePath = imageList[currentImageNumber]
                #print("imageSliderMoved before={}".format(self.selectedImagePath))
                pixelArray = readDICOM_Image.returnPixelArray(self.selectedImagePath)
                lut = None
                if self.overRideSavedColourmapAndLevels:
                    colourTable = cmbColours.currentText()
                elif self.applyUserSelection:
                    colourTable, _, _ = returnUserSelection(self, currentImageNumber)  
                    if colourTable == 'default':
                        colourTable, lut = readDICOM_Image.getColourmap(self.selectedImagePath)
                    #print('apply User Selection, colour table {}, image number {}'.format(colourTable,currentImageNumber ))
                else:
                    colourTable, lut = readDICOM_Image.getColourmap(self.selectedImagePath)

                displayImageCommon.displayColourTableInComboBox(cmbColours, colourTable)

                displayPixelArray(self, pixelArray, currentImageNumber, 
                                       lblImageMissing,
                                       lblPixelValue,
                                       spinBoxIntensity, spinBoxContrast,
                                       imv, colourTable,
                                       cmbColours, lut,
                                       multiImage=True,  
                                       deleteButton=btnDeleteDICOMFile) 

                subWindow.setWindowTitle(seriesName + ' - ' 
                         + os.path.basename(self.selectedImagePath))
               # print("imageSliderMoved after={}".format(self.selectedImagePath))
        except Exception as e:
            print('Error in displayImage.imageSliderMoved: ' + str(e))
            logger.error('Error in displayImage.imageSliderMoved: ' + str(e))


def deleteImageInMultiImageViewer(self, currentImagePath, 
                                      studyID, seriesID,
                                      lastSliderPosition):
    """When the Delete button is clicked on the multi image viewer,
    this function deletes the physical image and removes the 
    reference to it in the XML file."""
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
        print('Error in displayImage.deleteImageInMultiImageViewer: ' + str(e))
        logger.error('Error in displayImage.deleteImageInMultiImageViewer: ' + str(e))


def exportImage(self, imv, cmbColours):
    try:
        colourTable = cmbColours.currentText()
        imageName = os.path.basename(self.selectedImagePath) + '.png'
        fileName, _ = QFileDialog.getSaveFileName(caption="Enter a file name", 
                                                    directory=imageName, 
                                                    filter="*.png")
        minLevel, maxLevel = imv.getLevels()
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


def applyColourTableAndLevelsToSeries(self, imv, cmbColours, chkBox=None): 
        try:
            colourTable = cmbColours.currentText()
            if colourTable == 'custom':
                colourTable = 'gray'                
                displayImageCommon.displayColourTableInComboBox(cmbColours, 'gray')   

            displayImageCommon.setPgColourMap(colourTable, imv)
            if chkBox.isChecked():
                self.overRideSavedColourmapAndLevels = True
                self.applyUserSelection = False
            else:
                self.overRideSavedColourmapAndLevels = False
               
        except Exception as e:
            print('Error in DisplayImageColour.applyColourTableAndLevelsToSeries: ' + str(e))
            logger.error('Error in DisplayImageColour.applyColourTableAndLevelsToSeries: ' + str(e))              
        

def clearUserSelection(self, imageSlider):
    self.applyUserSelection = False
    #reset list of image lists that hold user selected colour table, min and max levels
    for image in self.userSelectionList:
        image[1] = 'default'
        image[2] = -1
        image[3] = -1
        #reload current image to display it without user selected 
        #colour table and levels.
        #This is done by advancing the slider and then moving it i 
        #to the original image
    if imageSlider:
        imageNumber = imageSlider.value()
        if imageNumber == 1:
            tempNumber = imageNumber + 1
        else:
            tempNumber = imageNumber - 1

        imageSlider.setValue(tempNumber)
        imageSlider.setValue(imageNumber)
                    

def changeSpinBoxLevels(self, imv, spinBoxIntensity, spinBoxContrast, chkBox=None):
    try:
        centre = spinBoxIntensity.value()
        width = spinBoxContrast.value()
        halfWidth = width/2

        minLevel = centre - halfWidth
        maxLevel = centre + halfWidth
        #print("centre{}, width{}, minLevel{}, maxLevel{}".format(centre, width, minLevel, maxLevel))
        imv.setLevels(minLevel, maxLevel)
        imv.show()

        if chkBox:
            if chkBox.isChecked() == False:
                self.applyUserSelection = True
            
                if self.selectedImagePath:
                    self.selectedImageName = os.path.basename(self.selectedImagePath)
                else:
                    #Workaround for the fact that when the first image is displayed,
                    #somehow self.selectedImageName looses its value.
                    self.selectedImageName = os.path.basename(self.imageList[0])
                    
                for imageNumber, image in enumerate(self.userSelectionList):
                    if image[0] == self.selectedImageName:
                        #Associate the levels with the image being viewed
                        self.userSelectionList[imageNumber][2] =  centre
                        self.userSelectionList[imageNumber][3] =  width
                        break
    except Exception as e:
        print('Error in DisplayImageColour.changeSpinBoxLevels: ' + str(e))
        logger.error('Error in DisplayImageColour.changeSpinBoxLevels: ' + str(e))
        
        
def updateUserSelectedColourTable(self, cmbColours, chkBox, spinBoxIntensity, spinBoxContrast):
        if chkBox.isChecked() == False:
            self.applyUserSelection = True
            colourTable = cmbColours.currentText()
            #print(self.userSelectionList)
            if self.selectedImagePath:
                self.selectedImageName = os.path.basename(self.selectedImagePath)
            else:
                #Workaround for the fact that when the first image is displayed,
                #somehow self.selectedImageName looses its value.
                self.selectedImageName = os.path.basename(self.imageList[0])
            #print("self.selectedImageName={}".format(self.selectedImageName))
            imageNumber = -1
            for imageNumber, image in enumerate(self.userSelectionList):
                if image[0] == self.selectedImageName:
                    break
        
            #Associate the selected colour table, contrast & intensity with the image being viewed
            self.userSelectionList[imageNumber][1] =  colourTable
           

def returnImageNumber(self):
    imageNumber = -1
    for count, image in enumerate(self.userSelectionList, 0):
        if image[0] == self.selectedImageName:
            imageNumber = count
            break
    return imageNumber


def updateUserSelectedLevels(self, spinBoxIntensity, spinBoxContrast):
        if self.applyUserSelection:
            imageNumber = returnImageNumber(self)
            if imageNumber != -1:
                self.userSelectionList[imageNumber][2] =  spinBoxIntensity.value()
                self.userSelectionList[imageNumber][3] =  spinBoxContrast.value()


def returnUserSelection(self, imageNumber):
        colourTable = self.userSelectionList[imageNumber][1] 
        intensity = self.userSelectionList[imageNumber][2]
        contrast = self.userSelectionList[imageNumber][3] 
        return colourTable, intensity, contrast


def updateDICOM(self, seriesIDLabel, studyIDLabel, cmbColours, spinBoxIntensity, spinBoxContrast):
        try:
            logger.info("DisplayImageColour.updateDICOM called")
            seriesID = seriesIDLabel.text()
            studyID = studyIDLabel.text()
            colourMap = cmbColours.currentText()
            if self.overRideSavedColourmapAndLevels:
                levels = [spinBoxIntensity.value(), spinBoxContrast.value()]
                updateDicomSeriesOneColour(self, seriesID, studyID, colourMap, levels)
            if self.applyUserSelection:
                updateDicomSeriesManyColours(self, seriesID, studyID, colourMap)
        except Exception as e:
            print('Error in DisplayImageColour.updateDICOM: ' + str(e))
            logger.error('Error in DisplayImageColour.updateDICOM: ' + str(e))


def updateDicomSeriesOneColour(self, seriesID, studyID, colourmap, levels, lut=None):
    """Updates every image in a DICOM series with one colour table and
            one set of levels"""
    try:
        logger.info("In DisplayImageColour.updateDicomSeriesOneColour")
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
        print('Error in DisplayImageColour.updateDicomSeriesOneColour: ' + str(e))


def updateDicomSeriesManyColours(self, seriesID, studyID, colourMap, lut=None):
    """Updates one or more images in a DICOM series with a different table and set of levels"""
    try:
        logger.info("In DisplayImageColour.updateDicomSeriesManyColours")
       
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
            # Apply user selected colour table & levels to individual images in the series
            selectedColourMap, center, width = returnUserSelection(self, imageCounter)
            if selectedColourMap != 'default' or center != -1 or width != -1:
                # Update an individual DICOM file in the series
                levels = [center, width]  
                updatedDataset = saveDICOM_Image.updateSingleDicom(dataset, colourmap=selectedColourMap, 
                                                    levels=levels, lut=lut)
                saveDICOM_Image.saveDicomToFile(updatedDataset, output_path=imagePath)
            imageCounter += 1
            messageWindow.setMsgWindowProgBarValue(self, imageCounter)
        messageWindow.closeMessageSubWindow(self)
    except Exception as e:
        print('Error in DisplayImageColour.updateDicomSeriesManyColours: ' + str(e))