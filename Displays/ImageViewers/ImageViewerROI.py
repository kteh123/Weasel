"""Class ImageViewerROI creates an MDI subwindow for viewing an image or series of images 
    with the facility to draw a Region of Interest ROI on the image.
"""
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
import numpy as np
import math
import DICOM.ReadDICOM_Image as ReadDICOM_Image
import DICOM.SaveDICOM_Image as SaveDICOM_Image

from Displays.ImageViewers.ComponentsUI.FreeHandROI.GraphicsView import GraphicsView
from Displays.ImageViewers.ComponentsUI.FreeHandROI.Resources import * 
from Displays.ImageViewers.ComponentsUI.ImageSliders  import ImageSliders as imageSliders
from Displays.ImageViewers.ComponentsUI.ImageLevelsSpinBoxes import ImageLevelsSpinBoxes as imageLevelsSpinBoxes
from Displays.ImageViewers.ComponentsUI.PixelValueLabel import PixelValueComponent 

import logging
logger = logging.getLogger(__name__)

__author__ = "Steve Shillitoe"
#September 2021

class Slider(QSlider):
    """
    A subclass of the PyQt5 class QSlider 
    so that the direction (Forward, Backward) of 
    slider travel is returned to the calling function.

    This class is used to create a hidden slider used 
    for zooming the image.
    """
    Nothing, Forward, Backward = 0, 1, -1
    directionChanged = pyqtSignal(int)
    def __init__(self, parent=None):
        QSlider.__init__(self, parent)
        self._direction = Slider.Nothing
        self.last = self.value()/self.maximum()
        self.valueChanged.connect(self.onValueChanged)


    def onValueChanged(self, value):
        """

        """
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
    the facility to draw an ROI on the image.  It also has multiple
    sliders for browsing series of images."""

    def __init__(self, weasel, dcm): 
        """
        When an object is created from the class ImageViewerROI, this function is called.
        It creates the MDI subwindow and adds it to the Weasel MDI area.

        If a series is to be viewed:

        1. It creates sliders for navigating the images in the series. There will be a
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
            self.weasel = weasel
            self.numberOfImages = len(self.imagePathList)
            
            if dcm.__class__.__name__ == "Image":
                self.isSeries = False
                self.isImage = True
                self.selectedImagePath = dcm.path
            else:
                self.isSeries = True
                self.isImage = False

            self.SubWindowOptions( QMdiSubWindow.RubberBandResize | QMdiSubWindow.RubberBandMove)
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

            self.setUpGraphicsView()

            self.setUpLevelsSpinBoxes()

            self.setUpZoomSlider()

            self.setUpROIButtons()

            if dcm.__class__.__name__ == "Image":
                self.displayPixelArrayOfSingleImage(self.imagePathList )
            else:
                #DICOM series selected
                self.setUpImageSliders()

            self.show()
        except Exception as e:
            print('Error in ImageViewerROI.__init__: ' + str(e))
            logger.exception('Error in ImageViewerROI.__init__: ' + str(e))


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
            print('Error in ImageViewerROI.setUpMainLayout: ' + str(e))
            logger.exception('Error in ImageViewerROI.setUpMainLayout: ' + str(e))


    def setUpRoiToolsLayout(self):
        """
        Creates a horizontal layout to contain the RIO tools
        buttons & adds it to the ROI tools group box.
        """
        self.roiToolsLayout = QHBoxLayout()
        self.roiToolsLayout.setContentsMargins(0, 0, 0, 0)
        self.roiToolsLayout.setSpacing(0)
        self.roiToolsGroupBox = QGroupBox()
        self.roiToolsGroupBox.setFixedHeight(45)
        self.roiToolsGroupBox.setLayout(self.roiToolsLayout)


    def setUpROIDropDownList(self):
        """
        Creates the ROI names drop down list or combo box with the default first
        ROI name, region1.
        The combo box is editable, so the user may change this default name.
        When the user presses the add ROI button, a new default ROI is added at 
        the end of the list in the combo box with the format regionX, where X is a number. 
        """
        self.cmbNamesROIs = QComboBox()
        self.cmbNamesROIs.setDuplicatesEnabled(False)
        self.cmbNamesROIs.addItem("region1")
        self.cmbNamesROIs.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.graphicsView.currentROIName = "region1"
        self.cmbNamesROIs.setCurrentIndex(0)
        self.cmbNamesROIs.setStyleSheet('QComboBox {font: 11pt Arial}')
        self.cmbNamesROIs.setToolTip("Displays a list of ROIs created")
        self.cmbNamesROIs.setEditable(True)
        self.cmbNamesROIs.setInsertPolicy(QComboBox.InsertAtCurrent)


    def connectSlotToSignalForROITools(self):
        """
        Connects relevant functions to the clicked event of the RIO tools buttons
        and for the RIO names drop down list connects functions to its currentIndexChanged
        and editTextChanged events. 

        Delete button clicked event connected to self.deleteROI

        New ROI button clicked event connected to newROI function of the graphicsView object 
        and loadImageInImageItem.  The latter function because the clean version of the image
        needs to be displayed.

        Reset ROI button clicked event connected to the resetROI function of the graphicsView object

        Save ROI button clicked event connected to the saveROI function

        Load ROI button clicked event connected to the loadROI function

        Erase ROI button clicked event connected to the eraseROI function.  
        The boolean variable, Checked, that represents the checked state of the
        Erase ROI button is passed into this function.

        Draw ROI button clicked event connected to the drawROI function.  
        The boolean variable, Checked, that represents the checked state of the
        draw ROI button is passed into this function.

        Paint ROI button clicked event connected to the paintROI function.  
        The boolean variable, Checked, that represents the checked state of the
        paint ROI button is passed into this function.

        Zoom button clicked event connected to the zoomImage function.  
        The boolean variable, Checked, that represents the checked state of the
        zoom button is passed into this function.

        ROI names combo box currentIndexChanged event connected to the 
        loadImageInImageItem function with the addMask argument set to True,
        so as to display the mask associated with the selected ROI with the image.

        ROI names combo box editTextChanged event connected to the roiNameChanged fuction.
        This event is 'fired' when the user edits the name of the current RIO. 
        """
        self.btnDeleteROI.clicked.connect(self.deleteROI)
        self.btnNewROI.clicked.connect(self.graphicsView.newROI) 
        self.btnNewROI.clicked.connect(lambda: self.loadImageInImageItem(False))
        self.btnResetROI.clicked.connect(self.graphicsView.resetROI)
        self.btnSaveROI.clicked.connect(self.saveROI)
        self.btnLoad.clicked.connect(self.loadROI)
        self.btnErase.clicked.connect(lambda checked: self.eraseROI(checked))
        self.btnDraw.clicked.connect(lambda checked: self.drawROI(checked))
        self.btnPaint.clicked.connect(lambda checked: self.paintROI(checked))
        self.btnZoom.clicked.connect(lambda checked: self.zoomImage(checked))
        self.cmbNamesROIs.currentIndexChanged.connect(lambda: self.loadImageInImageItem(True))
        self.cmbNamesROIs.currentIndexChanged.connect(self.setCurrentNameROI)
        self.cmbNamesROIs.editTextChanged.connect(lambda text: self.roiNameChanged(text))


    def setCurrentNameROI(self):
        """
        When a ROI is selected in the ROI drop down list, this function
        updates the previousRegionName in the dictROI dictionary, the
        data structure used to store ROI data.  This must be done in 
        case the user wishes to change the current ROI name.
        """
        currentNameROI = self.cmbNamesROIs.currentText()
        self.graphicsView.dictROIs.setPreviousRegionName(currentNameROI)


    def deleteROI(self):
        """
        Deletes the current ROI. 

        First the mask containing this ROI is deleted from the
        dictROI dictionary. Then the name of this ROI is removed
        from the ROI dropdown list. Finally, the image is reloaded
        and displayed without this ROI and the ROI mean and standard
        deviation updated. 
        """
        try:
            logger.info("ImageViewerROI.deleteROI called")
            preDeleteCurrentIndex = self.cmbNamesROIs.currentIndex()
            self.graphicsView.dictROIs.deleteMask(self.cmbNamesROIs.currentText())
            #Remove ROI from drop down list
            self.cmbNamesROIs.blockSignals(True)
            self.cmbNamesROIs.removeItem(self.cmbNamesROIs.currentIndex())
            self.cmbNamesROIs.blockSignals(False)
            #If the default first ROI is removed, add it back
            if self.cmbNamesROIs.currentIndex() == -1: 
                self.cmbNamesROIs.blockSignals(True)
                self.cmbNamesROIs.clear()
                self.cmbNamesROIs.addItem("region1")
                self.cmbNamesROIs.setCurrentIndex(0)
                self.cmbNamesROIs.blockSignals(False)
                self.clearPixelValueMeanAndStdDev()
                self.graphicsView.dictROIs.resetRegionNumber()  
            else:
                if preDeleteCurrentIndex == 0:
                    #deleting the first ROI in the list,
                    #select the next ROI in the list for display
                    newIndex = 0
                else:
                    #select the previous ROI in the list for display
                    newIndex = preDeleteCurrentIndex - 1
                self.cmbNamesROIs.setCurrentIndex(newIndex)
            self.loadImageInImageItem(True) 
            self.displayROIMeanAndStd()
        except Exception as e:
            print('Error in ImageViewerROI.deleteROI: ' + str(e))
            logger.exception('Error in ImageViewerROI.deleteROI: ' + str(e)) 


    def roiNameChanged(self, newText):
        try:
            logger.info("ImageViewerROI.roiNameChanged called")
            currentIndex = self.cmbNamesROIs.currentIndex()
            #Prevent spaces in new ROI name
            if ' ' in newText:
                newText = newText.replace(" ", "")
                self.cmbNamesROIs.setItemText(currentIndex, newText)
                self.cmbNamesROIs.setCurrentText(newText)
            index = self.cmbNamesROIs.findText(newText);
            if index == -1:
                self.cmbNamesROIs.setItemText(currentIndex, newText);
                nameChangedOK = self.graphicsView.dictROIs.renameDictionaryKey(newText)
                if nameChangedOK == False:
                    msgBox = QMessageBox()
                    msgBox.setWindowTitle("ROI Name Change")
                    msgBox.setText("This name is already in use")
                    msgBox.exec()
                    self.cmbNamesROIs.blockSignals(True)
                    cmbNamesROIs.setCurrentText(self.graphicsView.dictROIs.prevRegionName)
                    self.cmbNamesROIs.blockSignals(False)
        except Exception as e:
                print('Error in ImageViewerROI.roiNameChanged: ' + str(e))
                logger.exception('Error in ImageViewerROI.roiNameChanged: ' + str(e)) 


    def saveROI(self):
        try:
            # Save Current ROI
            logger.info("ImageViewerROI.saveROI called")
            regionName = self.cmbNamesROIs.currentText()
            # get the list of boolean masks for this series
            maskList = self.graphicsView.dictROIs.dictMasks[regionName] 
            # Convert each 2D boolean to 0s and 1s
            maskList = [np.transpose(np.array(mask, dtype=np.int)) for mask in maskList]
            suffix = str("_ROI_"+ regionName)
            if len(maskList) > 1:
                #inputPath = [i.path for i in self.weasel.images()]
                inputPath = self.imagePathList 
            else:
                inputPath = [self.selectedImagePath]
            # Saving Progress message
            self.weasel.progress_bar(msg="<H4>Saving ROIs into a new DICOM Series ({} files)</H4>".format(len(inputPath)))
            self.weasel.progressBar.set_maximum(len(inputPath))
            (subjectID, studyID, seriesID) = self.weasel.objXMLReader.getImageParentIDs(inputPath[0])
            seriesID = str(int(self.weasel.objXMLReader.getStudy(subjectID, studyID)[-1].attrib['id'].split('_')[0]) + 1)
            seriesUID = SaveDICOM_Image.generateUIDs(ReadDICOM_Image.getDicomDataset(inputPath[0]), seriesID)
            for index, path in enumerate(inputPath):
                self.weasel.progressBar.set_value(index)
                outputPath = SaveDICOM_Image.returnFilePath(path, suffix)
                SaveDICOM_Image.saveNewSingleDicomImage(outputPath, path, maskList[index], suffix, series_id=seriesID, series_uid=seriesUID, parametric_map="SEG")
                if "philips" in ReadDICOM_Image.getImageTagValue(outputPath, "Manufacturer").lower():
                    slope = ReadDICOM_Image.getImageTagValue(outputPath, "RescaleSlope")
                    SaveDICOM_Image.overwriteDicomFileTag(outputPath, (0x2005, 0x100E), 1/slope) #[(0x2005, 0x100E)]
                self.weasel.objXMLReader.insertNewImageInXMLFile(path, outputPath, suffix)
            self.weasel.progressBar.set_value(len(inputPath))
            self.weasel.progressBar.close()
            self.weasel.refresh()
            QMessageBox.information(self.weasel, "Export ROIs", "Image Saved")
        except Exception as e:
            print('Error in ImageViewerROI.saveROI: ' + str(e))
            logger.exception('Error in ImageViewerROI.saveROI: ' + str(e)) 


    def loadROI(self):
        try:
            logger.info("ImageViewerROI.loadROI called")
            # The following workflow is assumed:
            #   1. The user first loads a series of DICOM images
            #   2. Then the user chooses the series with the mask that will overlay the current viewer.

            study = self.weasel.objXMLReader.getStudy(self.subjectID, self.studyID)
            helpMsg = "Select a Series with ROI"
            listSeries = [series.attrib['id'] for series in study] # if 'ROI' in series.attrib['id']]
            list_input = {"type":"listview", "label":"Series", "list": listSeries}
            cancel, listParams = self.weasel.user_input(list_input, help_text=helpMsg, title="Load ROI")
            if cancel: return
            else:
                seriesID = listSeries[listParams[0]['value'][0]]
                imagePathList = self.weasel.objXMLReader.getImagePathList(self.subjectID, self.studyID, seriesID)
                if self.weasel.series != []:
                    #targetPath = [i.path for i in self.weasel.images()]
                    targetPath = self.imagePathList
                else:
                    targetPath = [self.selectedImagePath]
                maskInput = ReadDICOM_Image.returnSeriesPixelArray(imagePathList)
                maskInput[maskInput != 0] = 1
                maskList = [] # Output Mask
                # Consider DICOM Tag SegmentSequence[:].SegmentLabel as some 3rd software do
                if hasattr(ReadDICOM_Image.getDicomDataset(imagePathList[0]), "ContentDescription"):
                    region = ReadDICOM_Image.getSeriesTagValues(imagePathList, "ContentDescription")[0][0]
                else:
                    region = "new_region_label"
                # Affine re-adjustment
                for index, dicomFile in enumerate(targetPath):
                    self.weasel.progress_bar(msg="<H4>Loading selected ROI into target image {}</H4>".format(index + 1))
                    self.weasel.progressBar.set_maximum(len(targetPath))
                    self.weasel.progressBar.set_value(index + 1)
                    dataset_original = ReadDICOM_Image.getDicomDataset(dicomFile)
                    tempArray = np.zeros(np.shape(ReadDICOM_Image.getPixelArray(dataset_original)))
                    for maskFile in imagePathList:
                        dataset = ReadDICOM_Image.getDicomDataset(maskFile)
                        maskArray = ReadDICOM_Image.getPixelArray(dataset)
                        maskArray[maskArray != 0] = 1
                        affineResults = ReadDICOM_Image.mapMaskToImage(maskArray, dataset, dataset_original)
                        if affineResults:
                            try:
                                coords = zip(*affineResults)
                                tempArray[tuple(coords)] = list(np.ones(len(affineResults)).flatten())
                            except:
                                pass
                    maskList.append(tempArray)
                    self.weasel.progressBar.set_value(index+2)
                self.weasel.progressBar.close()

                # First populate the ROI_Storage data structure in a loop
                self.graphicsView.currentROIName = region
                for imageNumber in range(len(maskList)):  #To Do
                    self.graphicsView.currentImageNumber = imageNumber + 1
                    self.graphicsView.dictROIs.addMask(np.array(maskList[imageNumber]).astype(bool))

                # Second populate the dropdown list of region names
                self.cmbNamesROIs.blockSignals(True)
                #remove previous contents of ROI dropdown list
                self.cmbNamesROIs.clear()  
                self.cmbNamesROIs.addItems(self.graphicsView.dictROIs.getListOfRegions())
                self.cmbNamesROIs.blockSignals(False)

                # Redisplay the current image to show the mask
                self.cmbNamesROIs.blockSignals(True)
                self.cmbNamesROIs.setCurrentIndex(self.cmbNamesROIs.count() - 1)
                self.cmbNamesROIs.blockSignals(False)
                self.loadImageInImageItem(True)
        except Exception as e:
                print('Error in ImageViewerROI.loadROI: ' + str(e))
                logger.exception('Error in ImageViewerROI.loadROI: ' + str(e)) 


    def setButtonsToDefaultStyle(self):
        logger.info("DisplayImageDrawRIO.setButtonsToDefaultStyle called")
        try:
            logger.info("ImageViewerROI.setButtonsToDefaultStyle called.")
            #QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
            QApplication.restoreOverrideCursor()
            self.graphicsView.drawEnabled = False
            self.graphicsView.eraseEnabled = False
            self.graphicsView.paintEnabled = False
            if len(self.buttonList) > 0:
                for button in self.buttonList:
                    button.setStyleSheet(
                     "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
                     )
                    #button.setChecked(False)
        except Exception as e:
                print('Error in ImageViewerROI.setButtonsToDefaultStyle: ' + str(e))
                logger.exception('Error in ImageViewerROI.setButtonsToDefaultStyle: ' + str(e))  


    def drawROI(self, checked):
        logger.info("ImageViewerROI.drawROI called.")
        if checked:
            self.setButtonsToDefaultStyle()
            self.btnDraw.setStyleSheet("background-color: red")
            self.graphicsView.drawROI(checked)
        else:
            QApplication.restoreOverrideCursor()
            self.graphicsView.drawEnabled = False
            self.btnDraw.setStyleSheet(
             "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
             )


    def eraseROI(self, checked):
        logger.info("ImageViewerROI.eraseROI called.")
        if checked:
            self.setButtonsToDefaultStyle()
            self.btnErase.setStyleSheet("background-color: red")
            self.graphicsView.eraseROI(checked)
        else:
            QApplication.restoreOverrideCursor()
            self.graphicsView.eraseEnabled = False
            self.btnErase.setStyleSheet(
             "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
             )


    def paintROI(self, checked):
        logger.info("ImageViewerROI.paintROI called.")
        if checked:
            self.setButtonsToDefaultStyle()
            self.btnPaint.setStyleSheet("background-color: red")
            self.graphicsView.paintROI(checked)
        else:
            QApplication.restoreOverrideCursor()
            self.graphicsView.paintEnabled = False
            self.btnPaint.setStyleSheet(
             "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
             )


    def zoomImage(self, checked):
        logger.info("ImageViewerROI.zoomImage called.")
        if checked:
            self.setButtonsToDefaultStyle()
            self.graphicsView.setZoomEnabled(True)
            self.graphicsView.graphicsItem.paintEnabled = False
            self.graphicsView.graphicsItem.drawEnabled = False
            self.graphicsView.graphicsItem.eraseEnabled = False
            self.btnZoom.setStyleSheet("background-color: red")
        else:
            QApplication.restoreOverrideCursor()
            self.graphicsView.setZoomEnabled(False)
            self.btnZoom.setStyleSheet(
             "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
             )

    
    def getRoiMeanAndStd(self, mask, pixelArray):
        try:
            logger.info("ImageViewerROI.getRoiMeanAndStd called")
            mean = round(np.mean(np.extract(mask, pixelArray)), 1)
            std = round(np.std(np.extract(mask, pixelArray)), 1)
            return mean, std
        except Exception as e:
            print('Error in ImageViewerROI.getRoiMeanAndStd: ' + str(e))
            logger.exception('Error in ImageViewerROI.getRoiMeanAndStd: ' + str(e))


    def clearPixelValueMeanAndStdDev(self):
        self.roiMeanTxt.clear()
        self.roiStdDevTxt.clear()
        self.lblPixelValue.clear()


    def displayROIMeanAndStd(self):
        try:
            logger.info("ImageViewerROI.displayROIMeanAndStd called")
            if self.isSeries:  
                imageNumber = self.mainImageSlider.value()
            else:
                imageNumber = 1
            pixelArray = ReadDICOM_Image.returnPixelArray(self.selectedImagePath)
            regionName = self.cmbNamesROIs.currentText()
            mask = self.graphicsView.dictROIs.getMask(regionName, imageNumber)   
            if mask is not None:
                mean, std = self.getRoiMeanAndStd(mask, pixelArray)
                self.roiMeanTxt.setText("Mean: " + str(mean))
                self.roiStdDevTxt.setText("SD: " + str(std))
            else:
                self.clearPixelValueMeanAndStdDev()
        except Exception as e:
                print('Error in ImageViewerROI.displayROIMeanAndStd: ' + str(e))
                logger.exception('Error in ImageViewerROI.displayROIMeanAndStd: ' + str(e)) 


    def setUpImageEventHandlers(self):
        logger.info("ImageViewerROI.setUpImageEventHandlers called.")
        try:
            self.graphicsView.graphicsItem.sigRightMouseDrag.connect(
                lambda deltaX, deltaY: self.adjustLevelsByRightMouseButtonDrag(
                                        deltaX, deltaY))

            self.graphicsView.graphicsItem.sigMouseHovered.connect(
            lambda mouseOverImage:self.getPixelValue(mouseOverImage))

            self.graphicsView.graphicsItem.sigGetDetailsROI.connect(self.updateDetailsROI)

            self.graphicsView.graphicsItem.sigRecalculateMeanROI.connect(self.displayROIMeanAndStd)
            
            self.graphicsView.sigReloadImage.connect(lambda: self.loadImageInImageItem(True))

            self.graphicsView.sigROIChanged.connect(self.updateROIName)

            self.graphicsView.sigNewROI.connect(lambda newROIName:
                                                self.addNewROItoDropDownList(newROIName))
            self.graphicsView.sigNewROI.connect(self.clearPixelValueMeanAndStdDev)

            self.graphicsView.sigUpdateZoom.connect(lambda increment:
                                                    self.updateZoomSlider(increment))
        except Exception as e:
                print('Error in ImageViewerROI.setUpImageEventHandlers: ' + str(e))
                logger.exception('Error in ImageViewerROI.setUpImageEventHandlers: ' + str(e)) 


    def adjustLevelsByRightMouseButtonDrag(self, deltaX, deltaY):
        """
        This function allows the image intensity and contrast to be 
        adjusted by pressing the right mouse key and draging the 
        mouse pointer across the image. 

        Pressing the right mouse key & draging the mouse pointer down 
        and to the right increases the image intensity and contrast.
        Pressing the right mouse key and draging the mouse pointer up 
        and to the left decreases the image intensity and contrast.

        Input parameters
        ****************
        deltaX - change in mouse pointer position in the x direction
        deltaY - change in mouse pointer position in the y direction
        """
        try:
            self.levelsCompositeComponentLayout.blockLevelsSpinBoxSignals(True)
            centre = self.spinBoxIntensity.value()
            width = self.spinBoxContrast.value()
            if float(centre / np.shape(self.pixelArray)[1]) > 0.01:
                step_y = float(centre / np.shape(self.pixelArray)[1])
            else:
                step_y = 0.01
            if float(width / np.shape(self.pixelArray)[0]) > 0.01:
                step_x = float(width/ np.shape(self.pixelArray)[0])
            else:
                step_x = 0.01
            horizontalDiff = step_y * deltaY
            verticalDiff = step_x * deltaX # Maybe put a minus sign here
            newCentre = centre + horizontalDiff
            newWidth = width + verticalDiff
            self.spinBoxIntensity.setValue(newCentre)
            self.spinBoxContrast.setValue(newWidth)
            self.updateImageLevels()
            self.levelsCompositeComponentLayout.blockLevelsSpinBoxSignals(False)
        except Exception as e:
            print('Error in ImageViewerROI.adjustLevelsByRightMouseButtonDrag: ' + str(e))
            logger.exception('Error in ImageViewerROI.adjustLevelsByRightMouseButtonDrag: ' + str(e))

    
    def updateZoomSlider(self, increment):
        """This function updates the position of the slider on the image
        zoom slider and calculates the % zoom for display in the label zoomLabel.
        Although, the zoom slider widget is not displayed on the screen,
        this function is a convenient way to keep track of the current image
        zoom value"""
        try:
            logger.info("DisplayImageDrawRIO.updateZoomSlider called")
            self.zoomSlider.blockSignals(True)
            if increment == 0:
                self.zoomSlider.setValue(0)
                self.zoomValueLabel.setText("<H4>100%</H4>")
            else:
                newValue = self.zoomSlider.value() + increment
                newZoomValue = 100 + (newValue * 25)
                self.zoomValueLabel.setText("<H4>" + str(newZoomValue) + "%</H4>")
                if self.zoomSlider.value() < self.zoomSlider.maximum() and increment > 0:
                    self.zoomSlider.setValue(newValue)
                elif self.zoomSlider.value() > self.zoomSlider.minimum() and increment < 0:
                    self.zoomSlider.setValue(newValue)
            self.zoomSlider.blockSignals(False)
        except Exception as e:
                print('Error in ImageViewerROI.updateZoomSlider: ' + str(e))
                logger.exception('Error in ImageViewerROI.updateZoomSlider: ' + str(e))


    def addNewROItoDropDownList(self, newRegion):
        logger.info("ImageViewerROI.addNewROItoDropDownList called.")
        noDuplicate = True
        for count in range(self.cmbNamesROIs.count()):
             if self.cmbNamesROIs.itemText(count) == newRegion:
                 noDuplicate = False
                 break
        if noDuplicate:
            self.cmbNamesROIs.blockSignals(True)
            self.cmbNamesROIs.addItem(newRegion)
            self.cmbNamesROIs.setCurrentIndex(self.cmbNamesROIs.count() - 1)
            self.cmbNamesROIs.blockSignals(False)


    def updateROIName(self):
        """
        This function is connected to the sigROIChanged signal of the graphicsView object.
        It is called when the graphicsView object needs to have the current ROI name.
        """
        logger.info("ImageViewerROI.updateROIName called.")
        self.graphicsView.currentROIName = self.cmbNamesROIs.currentText()

    
    def setUpPixelValueGroupBox(self):
        """
        Creates a composite widget in a layout from the PixelValueComponent class
        and adds it to the pixelValueGroupBox group box
        """
        pixelValueComponent = PixelValueComponent()
        self.lblPixelValue = pixelValueComponent.getLabel()
        self.pixelValueGroupBox = QGroupBox("Pixel Value")
        self.pixelValueGroupBox.setFixedHeight(45)
        self.pixelValueGroupBox.setLayout(pixelValueComponent.getLayout()) 


    def setUpZoomGroupBox(self):
        """
        Sets up the label displaying the value of the image zoom.

        A QLabel widget is created and added to its own horizontal layout.
        This layout is added to a QGroupBox with the legend "Zoom"
        """
        self.zoomValueLabel = QLabel("<H4>100%</H4>")
        self.zoomValueLabel.setStyleSheet("color:red; padding-left:1; margin-left:1; font-size:8pt;")
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.zoomValueLabel, alignment = Qt.AlignCenter)
        self.zoomGroupBox = QGroupBox("Zoom")
        self.zoomGroupBox.setFixedHeight(45)
        self.zoomGroupBox.setLayout(layout) 


    def getPixelValue(self, mouseOverImage):
        """
        This function checks that the mouse pointer is over the
        image and when it is, it determines the value of the pixel
        under the mouse pointer and displays this in the label
        lblPixelValue together with the x,y coordinates of the mouse pointer.
        """
        try:
            logger.info("ImageViewerROI.getPixelValue called")
            if mouseOverImage:
                xCoord = math.floor(self.graphicsView.graphicsItem.xMouseCoord)
                yCoord = math.floor(self.graphicsView.graphicsItem.yMouseCoord)
                #correct the y coordinate value so that it has a value
                #of 0 at the bottom left corner of the image rather than
                #at the top left corner of the image
                _, nY = self.pixelArray.shape
                correctedYCoord = nY - yCoord
                pixelValue = self.graphicsView.graphicsItem.pixelValue
                strValue = str(pixelValue)
                if self.isSeries:  
                    imageNumber = self.mainImageSlider.value()
                else:
                    imageNumber = 1
                strPosition = ' @ X:' + str(xCoord) + ', Y:' + str(correctedYCoord ) + ', Z:' + str(imageNumber)
                self.lblPixelValue.setWordWrap(True)
                self.lblPixelValue.setText(strValue + '\n' + strPosition)
            else:
                 self.lblPixelValue.setText('')
        except Exception as e:
                print('Error in ImageViewerROI.getPixelValue: ' + str(e))
                logger.exception('Error in ImageViewerROI.getPixelValue: ' + str(e))


    def updateDetailsROI(self):
        logger.info("ImageViewerROI.updateDetailsROI called")
        try:
            self.graphicsView.currentROIName = self.cmbNamesROIs.currentText()
            if self.isSeries:  
                self.graphicsView.currentImageNumber = self.mainImageSlider.value()
            else:
                self.graphicsView.currentImageNumber = 1
        except Exception as e:
                print('Error in ImageViewerROI.updateDetailsROI: ' + str(e))
                logger.exception('Error in ImageViewerROI.updateDetailsROI: ' + str(e))


    def replaceMask(self):  
        logger.info("ImageViewerROI.replaceMask called")
        regionName = self.cmbNamesROIs.currentText()
        if self.isSeries:  
            imageNumber = self.mainImageSlider.value()
        else:
            imageNumber = 1
        mask = self.graphicsView.graphicsItem.getMaskData()
        self.graphicsView.dictROIs.replaceMask(regionName, mask, imageNumber)


    def setUpROIButtons(self):
        try:
            logger.info("ImageViewerROI.setUpPixelDataWidget called.")
            self.buttonList = []
            self.setUpROIDropDownList()

            self.btnDeleteROI = QPushButton() 
            self.btnDeleteROI.setToolTip('Delete the current ROI')
            self.btnDeleteROI.setIcon(QIcon(QPixmap(DELETE_ICON)))
        
            self.btnNewROI = QPushButton() 
            self.btnNewROI.setToolTip('Add a new ROI')
            self.btnNewROI.setIcon(QIcon(QPixmap(NEW_ICON)))

            self.btnResetROI = QPushButton()
            self.btnResetROI.setToolTip('Clears the ROI from the image')
            self.btnResetROI.setIcon(QIcon(QPixmap(RESET_ICON)))

            self.btnSaveROI = QPushButton()
            self.btnSaveROI.setToolTip('Saves the current ROI in DICOM format')
            self.btnSaveROI.setIcon(QIcon(QPixmap(SAVE_ICON)))

            self.btnLoad = QPushButton()
            self.btnLoad.setToolTip('Loads existing ROIs')
            self.btnLoad.setIcon(QIcon(QPixmap(LOAD_ICON)))

            self.btnErase = QPushButton()
            self.buttonList.append(self.btnErase)
            self.btnErase.setToolTip("Erase the ROI. Right click to change eraser size.")
            self.btnErase.setCheckable(True)
            self.btnErase.setIcon(QIcon(QPixmap(ERASER_CURSOR)))

            self.btnDraw = QPushButton()
            self.buttonList.append(self.btnDraw)
            self.btnDraw.setToolTip("Draw an ROI")
            self.btnDraw.setCheckable(True)
            self.btnDraw.setIcon(QIcon(QPixmap(PEN_CURSOR)))

            self.btnPaint = QPushButton()
            self.buttonList.append(self.btnPaint)
            self.btnPaint.setToolTip("Paint an ROI")
            self.btnPaint.setCheckable(True)
            self.btnPaint.setIcon(QIcon(QPixmap(BRUSH_CURSOR)))

            self.btnZoom = QPushButton()
            self.buttonList.append(self.btnZoom)
            self.btnZoom.setToolTip("Zoom In-Left Mouse Button/Zoom Out-Right Mouse Button")
            self.btnZoom.setCheckable(True)
            self.btnZoom.setIcon(QIcon(QPixmap(MAGNIFYING_GLASS_CURSOR)))

            self.roiMeanTxt = QLabel()
            self.roiMeanTxt.setStyleSheet("color : red; padding-left:0; margin-left:0; font-size:8pt;")
            self.roiMeanTxt.setToolTip("ROI Mean Value")
            self.roiStdDevTxt = QLabel()
            self.roiStdDevTxt.setStyleSheet("color : red; padding-left:0; margin-left:0; font-size:8pt;")
            self.roiStdDevTxt.setToolTip("ROI Mean Value Standard Deviation")
            self.connectSlotToSignalForROITools()

            self.roiToolsLayout.addWidget(self.cmbNamesROIs, alignment=Qt.AlignLeft)
            self.roiToolsLayout.addWidget(self.btnNewROI, alignment=Qt.AlignLeft)
            self.roiToolsLayout.addWidget(self.btnResetROI,  alignment=Qt.AlignLeft)
            self.roiToolsLayout.addWidget(self.btnDeleteROI,  alignment=Qt.AlignLeft)
            self.roiToolsLayout.addWidget(self.btnSaveROI,  alignment=Qt.AlignLeft)
            self.roiToolsLayout.addWidget(self.btnLoad,  alignment=Qt.AlignLeft)
            self.roiToolsLayout.addWidget(self.btnDraw,  alignment=Qt.AlignLeft)
            self.roiToolsLayout.addWidget(self.btnPaint,  alignment=Qt.AlignLeft)
            self.roiToolsLayout.addWidget(self.btnErase, alignment=Qt.AlignLeft)
            self.roiToolsLayout.addWidget(self.btnZoom,  alignment=Qt.AlignLeft)
            self.roiToolsLayout.addWidget(self.roiMeanTxt,  alignment=Qt.AlignLeft)
            self.roiToolsLayout.addWidget(self.roiStdDevTxt,  alignment=Qt.AlignLeft)
        except Exception as e:
               print('Error in ImageViewerROI.setUpROIButtons: ' + str(e))
               logger.exception('Error in ImageViewerROI.setUpROIButtons: ' + str(e)) 

            
    def loadImageInImageItem(self, addMask): 
        try:
            logger.info("ImageViewerROI.loadImageInImageItem called")
            
            self.graphicsView.dictROIs.setPreviousRegionName(self.cmbNamesROIs.currentText())

            if self.isSeries:  
                imageNumber = self.mainImageSlider.value()
            else:
                imageNumber = 1

            pixelArray = ReadDICOM_Image.returnPixelArray(self.selectedImagePath)

            if addMask:
                mask = self.graphicsView.dictROIs.getMask(self.cmbNamesROIs.currentText(), imageNumber)
            else:
                #This is used when an image without ROIs needs to be displayed
                #after the add new ROI button is clicked
                mask = None

            self.graphicsView.setImage(self.pixelArray, mask, self.selectedImagePath)
            self.displayROIMeanAndStd()  
            self.setUpImageEventHandlers()
        except Exception as e:
               print('Error in ImageViewerROI.loadImageInImageItem: ' + str(e))
               logger.exception('Error in ImageViewerROI.loadImageInImageItem: ' + str(e))
    

    def setUpImageLevelsLayout(self):
        self.levelsCompositeComponentLayout = imageLevelsSpinBoxes()
        self.imageLevelsGroupBox = QGroupBox()
        self.imageLevelsGroupBox.setFixedHeight(45)
        self.imageLevelsGroupBox.setLayout(self.levelsCompositeComponentLayout.getCompositeComponent())


    def setUpTopRowLayout(self):
        """
        In this function the horizontal layout is created and added to the
        main vertical layout. 
        This horizontal layout is used to contain the following in one row at the
        top of the MDI subwindow:
            1. The ROI tools group box. A row of buttons to enable 
            2. The image levels group box. Two spinboxes for the adjustment of image contrast and intensity
                in a group box.
            3. The pixel levels group box. A label displaying the  pixel value under the mouse pointer
                and its position in a group box.  
            4. The zoom amount group box.  A label displaying the zoom amount in a group box
        """
        try:
            self.topRowMainLayout = QHBoxLayout()
            
            self.setUpRoiToolsLayout()
            
            self.setUpImageLevelsLayout()

            self.setUpPixelValueGroupBox()

            self.setUpZoomGroupBox()
            
            self.topRowMainLayout.addWidget(self.roiToolsGroupBox)
            self.topRowMainLayout.addWidget(self.imageLevelsGroupBox)
            self.topRowMainLayout.addWidget(self.pixelValueGroupBox)
            self.topRowMainLayout.addWidget(self.zoomGroupBox)

            self.mainVerticalLayout.addLayout(self.topRowMainLayout)

            self.lblImageMissing = QLabel("<h4>Image Missing</h4>")
            self.lblImageMissing.hide()
            self.mainVerticalLayout.addWidget(self.lblImageMissing)
        except Exception as e:
            print('Error in ImageViewerROI.setUpTopRowLayout: ' + str(e))
            logger.exception('Error in ImageViewerROI.setUpTopRowLayout: ' + str(e))


    def setUpGraphicsView(self):
        self.graphicsView = GraphicsView(self.numberOfImages)
        self.mainVerticalLayout.addWidget(self.graphicsView)         


    def setUpLevelsSpinBoxes(self):
        try:
            self.spinBoxIntensity, self.spinBoxContrast = self.levelsCompositeComponentLayout.getSpinBoxes() 
            self.spinBoxIntensity.valueChanged.connect(self.updateImageLevels)
            self.spinBoxContrast.valueChanged.connect(self.updateImageLevels)
        except Exception as e:
            print('Error in ImageViewerROI.setUpLevelsSpinBoxes: ' + str(e))
            logger.exception('Error in ImageViewerROI.setUpLevelsSpinBoxes: ' + str(e))


    def updateImageLevels(self):
        logger.info("ImageViewerROI.updateImageLevels called.")
        try:
            if self.isSeries:  
                imageNumber = self.mainImageSlider.value()
            else:
                imageNumber = 1
            intensity = self.spinBoxIntensity.value()
            contrast = self.spinBoxContrast.value()
            mask = self.graphicsView.dictROIs.getMask(self.cmbNamesROIs.currentText(), imageNumber)
            self.graphicsView.graphicsItem.updateImageLevels(intensity, contrast, mask)
        except Exception as e:
            print('Error in ImageViewerROI.updateImageLevels when imageNumber={}: '.format(imageNumber) + str(e))
            logger.exception('Error in ImageViewerROI.updateImageLevels: ' + str(e))


    def setUpImageSliders(self):
        """
        Creates an instance of the custom, composite sliders 
        widget from the ImageSliders class and adds it to the 
        main vertical layout. 
        Also, connects its sliderMoved event to the function
        self.displayPixelArrayOfSingleImage(imagePath).
        """
        try:
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
            #with an object created from the ImageViewerROI class via the former's
            #sliderMoved event, which passes the image path of the image being viewed
            #to ImageViewerROI's displayPixelArrayOfSingleImage function for display.
            self.slidersWidget.sliderMoved.connect(lambda imagePath: 
                                                   self.displayPixelArrayOfSingleImage(imagePath))
            #Display the first image in the viewer
            self.slidersWidget.displayFirstImage()
        except Exception as e:
            print('Error in ImageViewerROI.setUpImageSliders: ' + str(e))
            logger.exception('Error in ImageViewerROI.setUpImageSliders: ' + str(e))


    def displayPixelArrayOfSingleImage(self, imagePath):
            """Displays an image's pixel array in a pyqtGraph imageView widget 
            & sets its colour table, contrast and intensity levels. 
            Also, sets the contrast and intensity in the associated histogram.
            """
            try:
                logger.info("ImageViewerROI.displayPixelArrayOfSingleImage called")

                self.selectedImagePath = imagePath
                imageName = os.path.basename(self.selectedImagePath)
                self.pixelArray = ReadDICOM_Image.returnPixelArray(self.selectedImagePath)
                

                self.setWindowTitle(self.subjectID + ' - ' + self.studyID + ' - '+ self.seriesID + ' - ' 
                         + imageName)

                #Check that pixel array holds an image & display it
                if self.pixelArray is None:
                    self.lblImageMissing.show()
                    self.graphicsView.setImage(np.array([[0,0,0],[0,0,0]]))  
                else:
                    self.loadImageInImageItem(True)
                    self.lblImageMissing.hide()
                    self.setInitialImageLevelValues()

            except Exception as e:
                print('Error in ImageViewerROI.displayPixelArrayOfSingleImage: ' + str(e))
                logger.exception('Error in ImageViewerROI.displayPixelArrayOfSingleImage: ' + str(e))


    def setUpZoomSlider(self):
        try:
            self.zoomSlider = Slider(Qt.Vertical)
            self.zoomSlider.setMinimum(0)
            self.zoomSlider.setMaximum(20)
            self.zoomSlider.setSingleStep(1)
            self.zoomSlider.setTickPosition(QSlider.TicksBothSides)
            self.zoomSlider.setTickInterval(1)
            self.zoomSlider.valueChanged.connect(lambda: 
                  self.graphicsView.zoomImage(self.zoomSlider.direction()))
        except Exception as e:
                print('Error in ImageViewerROI.setUpZoomSlider: ' + str(e))
                logger.exception('Error in ImageViewerROI.setUpZoomSlider: ' + str(e))  


    def setInitialImageLevelValues(self):
        self.spinBoxIntensity.blockSignals(True)
        self.spinBoxIntensity.setValue(self.graphicsView.graphicsItem.intensity)
        self.spinBoxIntensity.blockSignals(False)
        self.spinBoxContrast.blockSignals(True)
        self.spinBoxContrast.setValue(self.graphicsView.graphicsItem.contrast)
        self.spinBoxContrast.blockSignals(False)