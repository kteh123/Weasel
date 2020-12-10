from PyQt5 import QtCore 
from PyQt5 import QtWidgets
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
import CoreModules.WEASEL.InterfaceDICOMXMLFile as interfaceDICOMXMLFile
from CoreModules.freeHandROI.GraphicsView import GraphicsView
from CoreModules.freeHandROI.ROI_Storage import ROIs 
import logging
logger = logging.getLogger(__name__)


def setUpLevelsSpinBoxes(layout, graphicsView, cmbROIs, dictROIs):
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
                spinBoxIntensity.value(), spinBoxContrast.value(), dictROIs, cmbROIs))
    spinBoxContrast.valueChanged.connect(lambda: updateImageLevels(graphicsView,
                spinBoxIntensity.value(), spinBoxContrast.value(), dictROIs, cmbROIs))  
    layout.addLayout(gridLayoutLevels) 
    return spinBoxIntensity, spinBoxContrast
    

def updateImageLevels(graphicsView, intensity, contrast, dictROIs, cmbROIs):
    mask = dictROIs.getMask(cmbROIs.currentText())
    graphicsView.graphicsItem.updateImageLevels(intensity, contrast, mask)


def setUpPixelDataWidgets(self, layout, graphicsView, dictROIs):
    pixelDataLabel = QLabel("Pixel data")
    roiMeanLabel = QLabel("ROI Mean Value")
    lblCmbROIs =  QLabel("ROIs")
    cmbROIs = QComboBox()
    cmbROIs.addItem("region1")
    cmbROIs.setCurrentIndex(0)
    btnDeleteROI = QPushButton("Delete ROI")
    btnDeleteROI.clicked.connect(lambda: deleteROI(self, cmbROIs, dictROIs, graphicsView, pixelDataLabel, roiMeanLabel))
    cmbROIs.setStyleSheet('QComboBox {font: 12pt Arial}')
    cmbROIs.currentIndexChanged.connect(
        lambda: reloadMask(self, dictROIs, cmbROIs.currentText(), graphicsView,
                           pixelDataLabel, roiMeanLabel, cmbROIs))
    cmbROIs.currentIndexChanged.connect(
        lambda: dictROIs.setPreviousRegionName(cmbROIs.currentText()))
    cmbROIs.editTextChanged.connect( lambda text: roiNameChanged(cmbROIs, dictROIs, text))
    cmbROIs.toolTip = "Displays a list of ROIs created"
    cmbROIs.setEditable(True)
    cmbROIs.setInsertPolicy(QComboBox.InsertAtCurrent)
    spacerItem = QSpacerItem(20, 20, 
                             QtWidgets.QSizePolicy.Minimum, 
                             QtWidgets.QSizePolicy.Expanding)

    groupBoxImageData = QGroupBox('Image Data')
    gridLayoutImageData = QGridLayout()
    groupBoxImageData.setLayout(gridLayoutImageData)
    layout.addWidget(groupBoxImageData)

    gridLayoutImageData.addWidget(lblCmbROIs, 0,0, alignment=Qt.AlignRight, )
    gridLayoutImageData.addWidget(cmbROIs, 0,1, alignment=Qt.AlignLeft)
    gridLayoutImageData.addWidget(btnDeleteROI, 0,2, alignment=Qt.AlignLeft, )
    gridLayoutImageData.addItem(spacerItem, 0,3, alignment=Qt.AlignLeft)
    gridLayoutImageData.addWidget(pixelDataLabel, 1, 0, 1, 2)
    gridLayoutImageData.addWidget(roiMeanLabel, 1, 2, 1, 2)
    return pixelDataLabel, roiMeanLabel, cmbROIs


def setUpImageEventHandlers(self, graphicsView, pixelDataLabel, 
                            roiMeanLabel, 
                            dictROIs, cmbROIs):
    graphicsView.graphicsItem.sigMouseHovered.connect(
    lambda: displayImageDataUnderMouse(graphicsView, pixelDataLabel))

    graphicsView.graphicsItem.sigMaskCreated.connect(
        lambda:storeMaskData(graphicsView, cmbROIs.currentText(), dictROIs))

    graphicsView.graphicsItem.sigMaskCreated.connect(
        lambda: displayROIMeanAndStd(self, roiMeanLabel, dictROIs, cmbROIs))


def displayImageROISubWindow(self, derivedImagePath=None):
        """
        Creates a subwindow that displays one DICOM image and allows the creation of an ROI on it 
        """
        try:
            logger.info("DisplayImageROI displayImageROISubWindow called")
            pixelArray = readDICOM_Image.returnPixelArray(self.selectedImagePath)
        
            layout, lblImageMissing, subWindow = \
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

            graphicsView = GraphicsView()
            dictROIs = ROIs()

            if pixelArray is None:
                lblImageMissing.show()
                graphicsView.setImage(np.array([[0,0,0],[0,0,0]]))  
            else:
                graphicsView.setImage(pixelArray)
            layout.addWidget(graphicsView)

            pixelDataLabel, roiMeanLabel, cmbROIs = setUpPixelDataWidgets(self, layout, 
                                                                          graphicsView,
                                                                          dictROIs)

            setUpImageEventHandlers(self, graphicsView, pixelDataLabel, roiMeanLabel,
                                    dictROIs, cmbROIs)

            spinBoxIntensity, spinBoxContrast = setUpLevelsSpinBoxes(layout, graphicsView, cmbROIs, dictROIs)
            spinBoxIntensity.setValue(graphicsView.graphicsItem.intensity)
            spinBoxContrast.setValue(graphicsView.graphicsItem.contrast)
            setUpROITools(self, layout, graphicsView, cmbROIs, dictROIs, pixelDataLabel, roiMeanLabel)

        except (IndexError, AttributeError):
                subWindow.close()
                msgBox = QMessageBox()
                msgBox.setWindowTitle("View a DICOM series or image with an ROI")
                msgBox.setText("Select either a series or an image")
                msgBox.exec()
        except Exception as e:
            print('Error in DisplayImageROI.displayImageROISubWindow: ' + str(e))
            logger.error('Error in DisplayImageROI.displayImageROISubWindow: ' + str(e)) 


def displayMultiImageROISubWindow(self, imageList, studyName, 
                     seriesName, sliderPosition = -1):
        """
        Creates a subwindow that displays all the DICOM images in a series. 
        A slider allows the user to navigate  through the images.  
        The user may create an ROI on the series of images.
        """
        try:
            logger.info("DisplayImageROI.displayMultiImageROISubWindow called")
            layout, lblImageMissing, subWindow = \
                displayImageCommon.setUpImageViewerSubWindow(self)

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
           
            layout.addWidget(lblHiddenImagePath)
            layout.addWidget(lblHiddenSeriesID)
            layout.addWidget(lblHiddenStudyID)
           
            imageSlider = QSlider(Qt.Horizontal)

            graphicsView = GraphicsView()
            dictROIs = ROIs()
            layout.addWidget(graphicsView)
            pixelDataLabel, roiMeanLabel, cmbROIs = setUpPixelDataWidgets(self, layout, 
                                                                          graphicsView,
                                                                          dictROIs)
            spinBoxIntensity, spinBoxContrast = setUpLevelsSpinBoxes(layout, graphicsView, cmbROIs, dictROIs)
            setUpROITools(self, layout, graphicsView, cmbROIs, dictROIs, pixelDataLabel, roiMeanLabel)

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
                  lambda: imageROISliderMoved(self, seriesName, 
                                                   imageList, 
                                                   imageSlider.value(),
                                                   lblImageMissing, pixelDataLabel,
                                                   roiMeanLabel, cmbROIs, 
                                                   dictROIs,
                                                   spinBoxIntensity, 
                                                   spinBoxContrast,
                                                   graphicsView, subWindow))
           
            imageROISliderMoved(self, seriesName, 
                                    imageList, 
                                    imageSlider.value(),
                                    lblImageMissing, 
                                    pixelDataLabel, 
                                    roiMeanLabel, cmbROIs,
                                    dictROIs,
                                    spinBoxIntensity, 
                                    spinBoxContrast,
                                    graphicsView, subWindow)
            
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
        xCoord = graphicsView.graphicsItem.xMouseCoord
        yCoord = graphicsView.graphicsItem.yMouseCoord
        pixelColour = graphicsView.graphicsItem.pixelColour
        pixelValue = graphicsView.graphicsItem.pixelValue
        str ="Pixel value {}, Pixel colour {} @ X = {}, Y = {}".format(pixelValue, pixelColour,
                                                                      xCoord, yCoord)
        pixelDataLabel.setText(str)


def getRoiMeanAndStd(mask, pixelArray):
    mean = round(np.mean(np.extract(mask, pixelArray)), 3)
    std = round(np.std(np.extract(mask, pixelArray)), 3)
    return mean, std


def displayROIMeanAndStd(self, roiMeanLabel, dictROIs, cmbROIs):
        pixelArray = readDICOM_Image.returnPixelArray(self.selectedImagePath)
        regionName = cmbROIs.currentText()
        mask = dictROIs.getMask(regionName)
        if mask is not None:
            mean, std = getRoiMeanAndStd(mask, pixelArray)
            str ="ROI mean = {}, standard deviation = {}".format(mean, std)
        else:
            str = ""
        
        roiMeanLabel.setText(str)
        

def storeMaskData(graphicsView, regionName, dictROIs):
        mask = graphicsView.graphicsItem.getMaskData()
        dictROIs.addRegion(regionName, mask)

       
def imageROISliderMoved(self, seriesName, imageList, imageNumber,
                        lblImageMissing, pixelDataLabel, roiMeanLabel,
                        cmbROIs, dictROIs,
                        spinBoxIntensity, spinBoxContrast,  
                        graphicsView, subWindow):
        """On the Multiple Image with ROI Display sub window, this
        function is called when the image slider is moved. 
        It causes the next image in imageList to be displayed"""
        try:
            logger.info("DisplayImageROI.imageROISliderMoved called")
            #imageNumber = self.imageSlider.value()
            currentImageNumber = imageNumber - 1
            if currentImageNumber >= 0:
                self.selectedImagePath = imageList[currentImageNumber]
                #print("imageSliderMoved before={}".format(self.selectedImagePath))
                pixelArray = readDICOM_Image.returnPixelArray(self.selectedImagePath)

                if pixelArray is None:
                    lblImageMissing.show()
                    imv.setImage(np.array([[0,0,0],[0,0,0]]))  
                else:
                    graphicsView.setImage(pixelArray)
                    spinBoxIntensity.setValue(graphicsView.graphicsItem.intensity)
                    spinBoxContrast.setValue(graphicsView.graphicsItem.contrast)
                    setUpImageEventHandlers(self, graphicsView, pixelDataLabel, 
                                            roiMeanLabel, dictROIs, cmbROIs)

                subWindow.setWindowTitle(seriesName + ' - ' 
                         + os.path.basename(self.selectedImagePath))
               # print("imageSliderMoved after={}".format(self.selectedImagePath))
        except Exception as e:
            print('Error in DisplayImageROI.imageROISliderMoved: ' + str(e))
            logger.error('Error in DisplayImageROI.imageROISliderMoved: ' + str(e))


def setUpROITools(self, layout, graphicsView, cmbROIs, dictROIs, pixelDataLabel, roiMeanLabel):
        try:
            groupBoxROI = QGroupBox('ROI')
            gridLayoutROI = QGridLayout()
            groupBoxROI.setLayout(gridLayoutROI)
            layout.addWidget(groupBoxROI)

            btnNewROI = QPushButton('New') 
            btnNewROI.setToolTip('Allows the user to create a new ROI')
            btnNewROI.clicked.connect(lambda: newROI(cmbROIs, dictROIs, graphicsView))

            btnResetROI = QPushButton('Reset')
            btnResetROI.setToolTip('Clears the ROI from the image')
            btnResetROI.clicked.connect(lambda: resetROI(self, cmbROIs, dictROIs, graphicsView,
                                                        pixelDataLabel, roiMeanLabel))

            btnSaveROI = QPushButton('Save')
            btnSaveROI.setToolTip('Saves the ROI in DICOM format')
            btnSaveROI.clicked.connect(lambda: saveROI(self, cmbROIs.currentText(), dictROIs))

            gridLayoutROI.addWidget(btnNewROI,0,0)
            gridLayoutROI.addWidget(btnResetROI,0,1)
            gridLayoutROI.addWidget(btnSaveROI,0,2)
        except Exception as e:
            print('Error in setUpROITools: ' + str(e))
            logger.error('Error in setUpROITools: ' + str(e))


def newROI(cmbROIs, dictROIs, graphicsView):
    if dictROIs.hasRegionGotMask(cmbROIs.currentText()):
        cmbROIs.blockSignals(True)
        cmbROIs.addItem(dictROIs.getNextRegionName())
        cmbROIs.setCurrentIndex(cmbROIs.count() - 1)
        cmbROIs.blockSignals(False)
        graphicsView.graphicsItem.reloadImage()
    else:
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Add new ROI")
        msgBox.setText(
            "You must add ROIs to the current region before creating a new one")
        msgBox.exec()


def reloadImageInNewImageItem(cmbROIs, dictROIs, graphicsView, pixelDataLabel, roiMeanLabel, self):
    pixelArray = readDICOM_Image.returnPixelArray(self.selectedImagePath)
    graphicsView.setImage(pixelArray)
    setUpImageEventHandlers(self, graphicsView, pixelDataLabel, roiMeanLabel,
                                dictROIs, cmbROIs)
    

def deleteROI(self, cmbROIs, dictROIs, graphicsView, pixelDataLabel, roiMeanLabel):
    dictROIs.deleteMask(cmbROIs.currentText())
    reloadImageInNewImageItem(cmbROIs, dictROIs, graphicsView, pixelDataLabel, roiMeanLabel, self) 
    displayROIMeanAndStd(self, roiMeanLabel, dictROIs, cmbROIs)
    if cmbROIs.currentIndex() == 0 and cmbROIs.count() == 1:
        cmbROIs.clear()
        cmbROIs.addItem("region1")
        cmbROIs.setCurrentIndex(0) 
        pixelDataLabel.clear()
        roiMeanLabel.clear()
    else:
        cmbROIs.blockSignals(True)
        cmbROIs.removeItem(cmbROIs.currentIndex())
        cmbROIs.blockSignals(False)
        mask = dictROIs.getMask(cmbROIs.currentText())
        graphicsView.graphicsItem.reloadMask(mask)
  

def resetROI(self, cmbROIs, dictROIs, graphicsView,  
             pixelDataLabel, roiMeanLabel):
    dictROIs.deleteMask(cmbROIs.currentText())
    reloadImageInNewImageItem(cmbROIs, dictROIs, graphicsView, pixelDataLabel, roiMeanLabel, self) 
    pixelDataLabel.clear() 
    roiMeanLabel.clear()


def saveROI(self, regionName, dictROIs):
    # Save Current ROI
    mask = dictROIs.dictMasks[regionName] # Will return a boolean mask
    mask = np.transpose(np.array(mask, dtype=np.int)) # Convert boolean to 0s and 1s
    suffix = str("_ROI_"+ regionName)
    inputPath = self.selectedImagePath
    outputPath = saveDICOM_Image.returnFilePath(inputPath, suffix)
    saveDICOM_Image.saveDicomNewSeries([outputPath], [inputPath], [mask], suffix) # parametric_map="ROI") # Have to include an optional flag to insert dictROIs.label
    interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self, [inputPath], [outputPath], suffix)
    treeView.refreshDICOMStudiesTreeView(self)
    # CONSIDER INSERTING A SHORT LOOP HERE TO FORCE dataset.ContentLabel = regionName (DICOM Operation)
    # CONSIDER ALSO THE parametric_map OPTIONAL FLAG

    # Save all ROIs
    #for label, mask in dictROIs.dictMasks.items():
        #mask = np.transpose(np.array(mask, dtype=np.int))
        #suffix = str("_ROI_"+ label)
        #inputPath = self.selectedImagePath
        #outputPath = saveDICOM_Image.returnFilePath(inputPath, suffix)
        #saveDICOM_Image.saveDicomNewSeries([outputPath], [inputPath], [mask], suffix) #, parametric_map="ROI") # Have to include an optional flag to insert label
        #interfaceDICOMXMLFile.insertNewSeriesInXMLFile(self, [inputPath], [outputPath], suffix)
    #treeView.refreshDICOMStudiesTreeView(self)
   

def reloadMask(self, dictROIs, regionName, graphicsView,
              pixelDataLabel, roiMeanLabel, cmbROIs):
    reloadImageInNewImageItem(cmbROIs, dictROIs, graphicsView, pixelDataLabel, roiMeanLabel, self) 
    mask = dictROIs.getMask(regionName)
    if mask is not None:
       graphicsView.graphicsItem.reloadMask(mask)


def roiNameChanged(cmbROIs, dictROIs, newText):
    try:
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
            nameChangedOK = dictROIs.renameDictionaryKey(newText)
            #dictROIs.printContentsDictMasks()
            if nameChangedOK == False:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("ROI Name Change")
                msgBox.setText("This name is already in use")
                msgBox.exec()
                cmbROIs.setCurrentText(dictROIs.prevRegionName)
    except Exception as e:
            print('Error in DisplayImageDrawROI.roiNameChanged: ' + str(e))
            logger.error('Error in DisplayImageDrawROI.roiNameChanged: ' + str(e)) 
