from PyQt5.QtCore import  Qt, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap, QIcon, QPixmap
from PyQt5.QtWidgets import (QMessageBox, 
                            QGridLayout,
                            QHBoxLayout,
                            QVBoxLayout,
                            QPushButton,  
                            QLabel, 
                            QSlider, 
                            QListWidget,
                            QListWidgetItem,
                            QListView,
                            QCheckBox)
import numpy as np
import copy
import itertools
import pandas as pd
import DICOM.ReadDICOM_Image as ReadDICOM_Image
from DICOM.Classes import Series
from External.PandasDICOM.DICOM_to_DataFrame import DICOM_to_DataFrame
import time
import logging
logger = logging.getLogger(__name__)

__author__ = "Steve Shillitoe"
#September 2021

listImageTypes = ["SliceLocation", "AcquisitionTime", "AcquisitionNumber", 
                  "FlipAngle", "InversionTime", "EchoTime", "DiffusionBValue", 
                  "DiffusionGradientOrientation", (0x2005, 0x1572)] # This last element is a good example of private tag

SLIDER_ICON = 'Displays/ImageViewers/ComponentsUI/Images/slider_icon.png' 

class SortedImageSlider(QSlider):
    """Subclass of the QSlider class with the added property attribute 
    which identifies what the image subset has been filtered for. 
    """
    def __init__(self,  DicomAttribute): 
       super().__init__(orientation=Qt.Horizontal)
       self.attribute =  DicomAttribute
       self.setToolTip("Images sorted according to {}".format(DicomAttribute))


class SortedImageCheckBox(QCheckBox):
    """Subclass of the QCheckBox class with the added property attribute 
    which identifies what the image subset has been filtered for and 
    columnNumber which is the number of the column in the grid layout 
    where a widget created from this class is placed. 
    """
    def __init__(self,  DicomAttribute, colNum): 
       super().__init__()
       self.setText(DicomAttribute)
       self.setToolTip("Tick the check box to create a subset of images based on {}".format(DicomAttribute))
       self.setCheckState(Qt.Unchecked)
       #set a minimum width, so that the parent grid layout
       #allocates sufficient column width for the whole
       #label to be visible
       self.setMinimumWidth(160)
       #Properties added to the QCheckBox class
       self.attribute =  DicomAttribute
       self.colNumber = colNum

    @property
    def dicomAttribute(self):
        return self.attribute

    @property
    def columnNumber(self):
        return self.colNumber


class ImageSliders(QObject):
    """Creates a custom, composite widget composed of one or more sliders for 
    navigating a DICOM series of images."""

    sliderMoved = pyqtSignal(str)

    def __init__(self,  pointerToWeasel, subjectID, 
                 studyID, seriesID, imagePathList):
        try:
            #Super class QObject to provide support for pyqtSignal
            start = time.perf_counter()
            super().__init__()
            self.imagePathList = imagePathList
            self.subjectID = subjectID
            self.studyID = studyID
            self.seriesID = seriesID
            self.weasel = pointerToWeasel
            self.selectedImagePath = imagePathList[0]
            self.widthSubWindow = self.weasel.mdiArea.width()
        
            # Global variables for the Multisliders
            self.dynamicListImageType = []
            self.shapeList = []
            self.multiSliderPositionList = []
            self.dicomTable = pd.DataFrame()
            #A list of the sorted image sliders, 
            #updated as they are added and removed 
            #from the subwindow
            self.listSortedImageSliders = []

            #Create the custom, composite sliders widget
            self.__setUpLayouts()
            self. __addMultiSliderButtonToLayout()
            self.__createMainImageSlider()
            self.__addMainImageSliderToLayout()
            print("Time to instanciate ImageSliders object = {} seconds".format(time.perf_counter()-start))
        except Exception as e:
            print('Error in ImageSliders.__init__: ' + str(e))
            logger.error('Error in ImageSliders.__init__: ' + str(e))


    def getCustomSliderWidget(self):
        """A public function that passes the 
        composite slider widget to the
        parent layout on the subwindow"""
        return self.mainVerticalLayout


    def getMainSlider(self):
        """A public function that passes the main image 
        slider to Weasel"""
        return self.mainImageSlider


    def displayFirstImage(self):
        """A public function that displays the first image 
        in Weasel"""
        self.__mainImageSliderMoved(1)


    def __setUpLayouts(self):
        try:
            self.mainVerticalLayout = QVBoxLayout()
        
            self.mainSliderLayout = QHBoxLayout()
            self.imageTypeLayout = QHBoxLayout()
            self.sortedImageSliderLayout = QGridLayout()
            #The grid layout is added to the horizontal layout in order to
            #prevent it expanding too far to the right when it only contains
            #a few widgets.
            self.imageTypeLayout.addLayout(self.sortedImageSliderLayout)
            self.imageTypeLayout.addStretch()
            self.sortedImageSliderLayout.setHorizontalSpacing(0)
            self.sortedImageSliderLayout.setContentsMargins(0, 0, 0, 0)
            self.mainVerticalLayout.addLayout(self.mainSliderLayout)
            self.mainVerticalLayout.addLayout(self.imageTypeLayout)
        except Exception as e:
            print('Error in ImageSliders.__setUpLayouts: ' + str(e))
            logger.error('Error in ImageSliders.__setUpLayouts: ' + str(e))

    
    def __createMainImageSlider(self): 
        try:
            logger.info("ImageSliders.__createMainImageSlider called")
            self.mainImageSlider = QSlider(Qt.Horizontal)
            self.mainImageSlider.setFocusPolicy(Qt.StrongFocus) # This makes the slider work with arrow keys on Mac OS
            self.mainImageSlider.setToolTip("Use this slider to navigate the series of DICOM images")
            self.mainImageSlider.setSingleStep(1)
            self.mainImageSlider.setTickPosition(QSlider.TicksBothSides)
            self.mainImageSlider.setTickInterval(1)
            self.mainImageSlider.setMinimum(1)
            self.mainImageSlider.valueChanged.connect(self.__mainImageSliderMoved)
        except Exception as e:
            print('Error in ImageSliders.__createMainImageSlider: ' + str(e))
            logger.error('Error in ImageSliders.__createMainImageSlider: ' + str(e))


    def __addMainImageSliderToLayout(self):
        """Configures the width of the slider according to the number of images
        it must navigate and adds it and its associated label to the main slider
        layout"""
        try:
            maxNumberImages = len(self.imagePathList)
            self.mainImageSlider.setMaximum(maxNumberImages)
            
            if maxNumberImages < 4:
                self.mainImageSlider.setFixedWidth(self.widthSubWindow*.2)
            elif maxNumberImages > 3 and maxNumberImages < 11:
                self.mainImageSlider.setFixedWidth(self.widthSubWindow*.5)
            else:
                self.mainImageSlider.setFixedWidth(self.widthSubWindow*.80)
        
            self.imageNumberLabel = QLabel()
        
            if maxNumberImages > 1:
                self.mainSliderLayout.addWidget(self.mainImageSlider)
                self.mainSliderLayout.addWidget(self.imageNumberLabel)

            if maxNumberImages < 11:
                self.mainSliderLayout.addStretch(1)
        except Exception as e:
            print('Error in ImageSliders.__addMainImageSliderToLayout: ' + str(e))
            logger.error('Error in ImageSliders.__addMainImageSliderToLayout: ' + str(e))


    def __mainImageSliderMoved(self, imageNumber=None):
        """On the Multiple Image Display sub window, this
        function is called when the image slider is moved. 
        It causes the next image in imageList to be displayed
        """
        try: 
            logger.info("ImageSliders.__mainImageSliderMoved called")
            start = time.perf_counter()
            if imageNumber:
                self.mainImageSlider.setValue(imageNumber)
            else:
                imageNumber = self.mainImageSlider.value()
            currentImageNumber = imageNumber - 1
            if currentImageNumber >= 0:
                maxNumberImages = str(len(self.imagePathList))
                imageNumberString = "image {} of {}".format(imageNumber, maxNumberImages)
                self.imageNumberLabel.setText(imageNumberString)
                self.selectedImagePath = self.imagePathList[currentImageNumber]

                if len(self.listSortedImageSliders) > 0:
                    self.multiSliderPositionList = []
                    subTable = copy.copy(self.dicomTable)
                    for index, tag in enumerate(self.dynamicListImageType):
                        tagValue = subTable.loc[self.selectedImagePath, tag]
                        listAttr = sorted(subTable[tag].unique())
                        newIndex = listAttr.index(tagValue)
                        self.multiSliderPositionList.append(newIndex)
                        maxAttr = self.listSortedImageSliders[index][0].maximum()
                        self.listSortedImageSliders[index][0].blockSignals(True)
                        self.listSortedImageSliders[index][1].blockSignals(True)
                        self.listSortedImageSliders[index][0].setValue(newIndex+1)
                        self.listSortedImageSliders[index][1].setText("image {} of {}".format(newIndex+1, maxAttr))
                        self.listSortedImageSliders[index][0].blockSignals(False)
                        self.listSortedImageSliders[index][1].blockSignals(False)
                        # subTable will be needed in the case of extra "nameless" slider
                        subTable = subTable[subTable[tag] == tagValue]
                    if len(self.listSortedImageSliders) > len(self.dynamicListImageType):
                        newIndex = subTable.index.to_list().index(self.selectedImagePath)
                        self.multiSliderPositionList.append(newIndex)
                        maxAttr = self.listSortedImageSliders[index+1][0].maximum()
                        self.listSortedImageSliders[index+1][0].blockSignals(True)
                        self.listSortedImageSliders[index+1][1].blockSignals(True)
                        self.listSortedImageSliders[index+1][0].setValue(newIndex+1)
                        self.listSortedImageSliders[index+1][1].setText("image {} of {}".format(newIndex+1, maxAttr))
                        self.listSortedImageSliders[index+1][0].blockSignals(False)
                        self.listSortedImageSliders[index+1][1].blockSignals(False)

                #Send the file path of current image to the parent application
                self.sliderMoved.emit(self.selectedImagePath)
                print("Main Image Slider moved = {} seconds".format(time.perf_counter() - start))
        except TypeError as e: 
            print('Type Error in ImageSliders.__mainImageSliderMoved: ' + str(e))
            logger.error('Type Error in ImageSliders.__mainImageSliderMoved: ' + str(e))
        except Exception as e:
            print('Error in ImageSliders.__mainImageSliderMoved: ' + str(e))
            logger.error('Error in ImageSliders.__mainImageSliderMoved: ' + str(e))


    def __addMultiSliderButtonToLayout(self):
        """Creates toggle button (off-grey, on-red) to display/hide
        a checkbox for each DICOM attribute to sort images by.
        """
        try:
            self.btnMultiSliders = QPushButton()
            self.btnMultiSliders.setToolTip("Display Multiple Sliders")
            self.btnMultiSliders.setCheckable(True)
            self.btnMultiSliders.setIcon(QIcon(QPixmap(SLIDER_ICON)))
            self.mainSliderLayout.addWidget(self.btnMultiSliders)
            self.btnMultiSliders.clicked.connect(lambda setRed: self.__displayHideImageTypeCheckBoxes(setRed))
        except Exception as e:
            print('Error in ImageSliders.__addMultiSliderButtonToLayout: ' + str(e))
            logger.error('Error in ImageSliders.__addMultiSliderButtonToLayout: ' + str(e))
    

    ##Functions below support the display/hiding of the multi-sliders##   
    def __displayHideImageTypeCheckBoxes(self, state):
        """This function shows or hides a checkbox for each DICOM attribute
        
        It is executed when the multi-sliders toggle button is clicked
        """
        try:
            if state == True:
                logger.info("ImageSliders.__displayHideImageTypeCheckBoxes to display image type checkboxes")
                #make button red to show it is clicked
                self.btnMultiSliders.setStyleSheet("background-color: red")
                self.__setUpImageTypeCheckBoxes()
                tagsList = [self.checkboxList[i].dicomAttribute for i in range(len(self.checkboxList))]
                self.dicomTable = DICOM_to_DataFrame(self.imagePathList, tags=tagsList)
            elif state == False:
                logger.info("ImageSliders.__displayHideImageTypeCheckBoxes to hide image type checkboxes")
                #reset the button to grey
                self.btnMultiSliders.setStyleSheet(
                 "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #CCCCBB, stop: 1 #FFFFFF)"
                 )
                #hide image sliders by deleting them from the grid layout
                self.__clearAllMultiImageWidgets()
                #self.imageTypeList.clear()
                self.dynamicListImageType.clear()
                self.listSortedImageSliders.clear()
                self.shapeList = []    
        except Exception as e:
            print('Error in ImageSliders.__displayHideImageTypeCheckBoxes: ' + str(e))
            logger.exception('Error in ImageSliders.__displayHideImageTypeCheckBoxes: ' + str(e))
            
    
    def __clearAllMultiImageWidgets(self, leaveCheckBoxes=False):
        """Clears all widgets related with multi-sliders,
        if the multi-sliders toggle button is off.
        """
        try:
            
            widgets = [self.sortedImageSliderLayout.itemAt(i).widget() 
                       for i in range(self.sortedImageSliderLayout.count())]
            for widget in widgets:
                    if leaveCheckBoxes:
                        if isinstance(widget, SortedImageCheckBox):
                            continue
                    widget.deleteLater()
                    widget = None
        except Exception as e:
            print('Error in ImageSliders.__clearAllMultiImageWidgets when widget = {}: '.format(type(widget)) + str(e))
            logger.error('Error in ImageSliders.__clearAllMultiImageWidgets: ' + str(e))   


    def __setUpImageTypeCheckBoxes(self):
        """This method searches for the DICOM tags in listImageTypes that are present
        in the DICOM files and presents them with checkboxes in the image viewer.
        """
        try:
            self.dicomTable = DICOM_to_DataFrame(self.imagePathList, tags=listImageTypes) # Consider commenting if it takes too long
            columnNumber = 0 
            self.checkboxList = []
            for index, imageType in enumerate(listImageTypes):
                # First, check if the DICOM tag exists in the images of the series.
                if ReadDICOM_Image.getImageTagValue(self.selectedImagePath, imageType) is not None:
                    numAttr = len(self.dicomTable[imageType].unique())
                    #_, numAttr = ReadDICOM_Image.getSeriesTagValues(self.imagePathList, imageType)
                    # Then, check if there's more than 1 unique value for the corresponding DICOM tag
                    if numAttr > 1:
                        tempCheckBoxObject = self.__createSortedImageCheckBox(imageType, columnNumber)
                        self.checkboxList.append(tempCheckBoxObject)
                        #add to first row (0) of the layout
                        self.sortedImageSliderLayout.addWidget(tempCheckBoxObject, 0, columnNumber)
                        columnNumber +=3
        except Exception as e:
            print('Error in ImageSliders.__setUpImageTypeCheckBoxes: ' + str(e))
            logger.error('Error in ImageSliders.___setUpImageTypeCheckBoxes: ' + str(e))


    def __createSortedImageCheckBox(self, imageType, colNumber):
        try:
            tempCheckBox = SortedImageCheckBox(imageType, colNumber) 
            tempCheckBox.stateChanged.connect(
                lambda state: self.__displayHideImageTypeSlider(state,  imageType))
            return tempCheckBox
        except Exception as e:
            print('Error in ImageSliders.__createSortedImageCheckBox: ' + str(e))
            logger.error('Error in ImageSliders.__createSortedImageCheckBox: ' + str(e))


    def __displayHideImageTypeSlider(self, state, attribute):
        """This function displays or hides the slider associated with a checkbox"""
        logger.info("ImageSliders.____displayHideMultiSliders called")
        if state == Qt.Checked:
            self.dynamicListImageType.append(attribute)
        elif state == Qt.Unchecked:
            self.dynamicListImageType.remove(attribute)   
        self.__updateSliders()
    
    def getCheckBoxColumnNumber(self, attribute):
        for chkBox in self.checkboxList:
            if chkBox.dicomAttribute == attribute:
                return chkBox.columnNumber
                break


    def __updateSliders(self):
        """This method updates the state of the multi-sliders. However, it doesn't follow a
        simple or classic update/refresh style and approach.
        First, this method clears all widgets related to multi-sliders first. Then, based on the checked
        ImageTypes (aka DICOM tags), it creates new sliders so that these are in accordance with the current state of
        the image viewer (total number of images + checked DICOM tags).
        This means that the new sliders might have different lenghts.
        """
        try:
            #Remove sorted image sliders
            self.__clearAllMultiImageWidgets(leaveCheckBoxes=True)
   
            self.shapeList = []
            self.listSortedImageSliders = []
           
            for tag in self.dynamicListImageType:
                columnNumber = self.getCheckBoxColumnNumber(tag)
                numAttr = len(self.dicomTable[tag].unique())
                self.shapeList.append(numAttr)
                imageSlider = SortedImageSlider(tag)
                imageLabel = QLabel()
                listSliderLabelPair = [imageSlider, imageLabel]
                self.listSortedImageSliders.append(listSliderLabelPair)
                imageSlider.setFocusPolicy(Qt.StrongFocus) 
                imageSlider.setMaximum(numAttr)
                imageSlider.setSingleStep(1)
                imageSlider.setTickPosition(QSlider.TicksBothSides)
                imageSlider.setTickInterval(1)
                imageSlider.setMinimum(1)
                imageSlider.valueChanged.connect(self.__multipleImageSliderMoved)
                imageLabel.setText("image 1 of {}".format(numAttr))
            
                self.sortedImageSliderLayout.addWidget(imageSlider, 0, columnNumber+1, alignment=Qt.AlignLeft)
                self.sortedImageSliderLayout.addWidget(imageLabel, 0, columnNumber+2, alignment=Qt.AlignLeft)
                
            
            # Create a new slider with empty label string if there is more than 1 image per combination of tags
            if np.prod(self.shapeList) != len(self.imagePathList) and len(self.dynamicListImageType) > 0:
                imageSlider = SortedImageSlider('Instance')
                instanceLabel = QLabel('Instance')
                imageLabel = QLabel()
                listSliderLabelPair = [imageSlider, imageLabel]
                self.listSortedImageSliders.append(listSliderLabelPair)
                imageSlider.setFocusPolicy(Qt.StrongFocus)
                imageSlider.setSingleStep(1)
                imageSlider.setTickPosition(QSlider.TicksBothSides)
                imageSlider.setTickInterval(1)
                imageSlider.setMinimum(1)
                #Add to second row of the layout
                self.sortedImageSliderLayout.addWidget(instanceLabel, 1, 0, alignment=Qt.AlignHCenter)
                self.sortedImageSliderLayout.addWidget(imageSlider, 1, 1, alignment=Qt.AlignLeft)
                self.sortedImageSliderLayout.addWidget(imageLabel, 1, 2, alignment=Qt.AlignLeft)
                
                subTable = copy.copy(self.dicomTable)
                # Filter first values of each slider
                
                for tag in self.dynamicListImageType:
                    listAttr = sorted(self.dicomTable[tag].unique())
                    subTable = subTable[subTable[tag] == listAttr[0]]
                starting_point_lenght = len(subTable.index.to_list())
                imageSlider.setMaximum(starting_point_lenght)
                imageSlider.valueChanged.connect(self.__multipleImageSliderMoved)
                imageLabel.setText("image 1 of {}".format(starting_point_lenght))
        except Exception as e:
            print('Error in ImageSliders.__updateSliders when tag={}: '.format(tag) + str(e))
            logger.exception('Error in ImageSliders.__updateSliders: ' + str(e))

    
    def __multipleImageSliderMoved(self):  
        """This function is attached to the slider moved event of each 
        multiple slider.  The slider is identified by the DicomAttribute parameter. 
        The slider being moved determines the image displayed in the image viewer"""
        try:
            indexDict = {}
            #Create a dictionary of DICOM attribute:slider index pairs
            self.multiSliderPositionList = []
            for sliderImagePair in self.listSortedImageSliders:
                #update the text of the image x of y label
                indexDict[sliderImagePair[0].attribute] = sliderImagePair[0].value()
                currentImageNumberThisSlider = sliderImagePair[0].value()
                maxNumberImagesThisSlider =  sliderImagePair[0].maximum()
                labelText = "image {} of {}".format(currentImageNumberThisSlider, maxNumberImagesThisSlider)
                sliderImagePair[1].setText(labelText)
                self.multiSliderPositionList.append(currentImageNumberThisSlider-1)
            subTable = copy.copy(self.dicomTable)
            for index, tag in enumerate(self.dynamicListImageType):
                position = self.multiSliderPositionList[index]
                listAttr = sorted(self.dicomTable[tag].unique())
                subTable = subTable[subTable[tag] == listAttr[position]]
            if len(subTable.index.to_list()) > 1:
                self.selectedImagePath = subTable.index.to_list()[self.multiSliderPositionList[-1]]
            else:    
                self.selectedImagePath = subTable.index.to_list()[0]
            self.sliderMoved.emit(self.selectedImagePath)
            
            #update the position of the main slider so that it points to the
            #same image as the sorted image sliders.
            indexImageInMainList = self.imagePathList.index(self.selectedImagePath)
            self.mainImageSlider.setValue(indexImageInMainList+1)
        except IndexError:
            print("Warning - due to the DICOM attribute sliders you have selected, you may not be able to navigate the series of images.")
            QMessageBox.warning(self.weasel, "Warning Message", "Due to the DICOM attribute sliders you have selected, you may not be able to navigate the series of images.")
        except Exception as e:
            print('Error in ImageSliders.__multipleImageSliderMoved: ' + str(e))
            logger.exception('Error in ImageSliders.__multipleImageSliderMoved: ' + str(e))
           

    def __imageDeleted(self, newImagePathList):
        try:
            #newImagePathList is the original image file path list
            #but with the file path of the deleted image removed.
            self.imagePathList = newImagePathList
            self.mainImageSlider.setMaximum(len(newImagePathList))
            imageNumber = self.mainImageSlider.value()
            imageIndex = imageNumber - 1
            self.selectedImagePath = self.imagePathList[imageIndex]
            #Send the new current image to the parent application
            self.sliderMoved.emit(self.selectedImagePath)
            
            #To Do 
            #adjust the lists attached to sorted image list sliders
            #by removing the deleted image from the slider if present
            #and calling setMaximum(len(image list)) for each slider
            if len(self.listSortedImageSliders) > 0:
                tagsList = [self.imageTypeList.item(i).text() for i in range(self.imageTypeList.count())]
                self.dicomTable = DICOM_to_DataFrame(self.imagePathList, tags=tagsList)
                self.__updateSliders()
        except Exception as e:
            print('Error in ImageSliders.__imageDeleted: ' + str(e))