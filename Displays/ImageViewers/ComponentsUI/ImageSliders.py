from PyQt5.QtCore import  Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import (QMessageBox, 
                            QFormLayout,
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

import logging
logger = logging.getLogger(__name__)

__author__ = "Steve Shillitoe"
#September 2021

listImageTypes = ["SliceLocation", "AcquisitionTime", "AcquisitionNumber", 
                  "FlipAngle", "InversionTime", "EchoTime", 
                  (0x2005, 0x1572)] # This last element is a good example of private tag


class SortedImageSlider(QSlider):
    """Subclass of the QSlider class with the added property attribute 
    which identifies what the image subset has been filtered for. 
    """
    def __init__(self,  DicomAttribute): 
       super().__init__(orientation=Qt.Horizontal)
       self.attribute =  DicomAttribute
       self.setToolTip("Images sorted according to {}".format(DicomAttribute))


class ImageSliders(QObject):
    """Creates a custom, composite widget composed of one or more sliders for 
    navigating a DICOM series of images."""

    sliderMoved = pyqtSignal(str)


    def __init__(self,  pointerToWeasel, subjectID, 
                 studyID, seriesID, imagePathList):
        try:
            #Super class QObject to provide support for pyqtSignal
            super().__init__()
            self.imagePathList = imagePathList
            self.subjectID = subjectID
            self.studyID = studyID
            self.seriesID = seriesID
            self.weasel = pointerToWeasel
            self.selectedImagePath = imagePathList[0]
        
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
            self.__createMainImageSlider()
            self.__addMainImageSliderToLayout()
            self.__setUpDisplayMultiSlidersCheckbox()
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
            self.sortedImageSliderLayout = QFormLayout()
        
            self.mainVerticalLayout.addLayout(self.mainSliderLayout)
            self.mainVerticalLayout.addLayout(self.imageTypeLayout)
            self.mainVerticalLayout.addLayout(self.sortedImageSliderLayout)
        except Exception as e:
            print('Error in ImageSliders.__setUpLayouts: ' + str(e))
            logger.error('Error in ImageSliders.__setUpLayouts: ' + str(e))

    
    def __createMainImageSlider(self): 
        try:
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

    
    def __mainImageSliderMoved(self, imageNumber=None):
        """On the Multiple Image Display sub window, this
        function is called when the image slider is moved. 
        It causes the next image in imageList to be displayed
        """
        try: 
            logger.info("ImageSliders.__mainImageSliderMoved called")
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

                    
        except TypeError as e: 
            print('Type Error in ImageSliders.__mainImageSliderMoved: ' + str(e))
            logger.error('Type Error in ImageSliders.__mainImageSliderMoved: ' + str(e))
        except Exception as e:
            print('Error in ImageSliders.__mainImageSliderMoved: ' + str(e))
            logger.error('Error in ImageSliders.__mainImageSliderMoved: ' + str(e))


    def __addMainImageSliderToLayout(self):
        """Configures the width of the slider according to the number of images
        it must navigate and adds it and its associated label to the main slider
        layout"""
        try:
            maxNumberImages = len(self.imagePathList)
            self.mainImageSlider.setMaximum(maxNumberImages)
            widthSubWindow = self.weasel.mdiArea.width()
            if maxNumberImages < 4:
                self.mainImageSlider.setFixedWidth(widthSubWindow*.2)
            elif maxNumberImages > 3 and maxNumberImages < 11:
                self.mainImageSlider.setFixedWidth(widthSubWindow*.5)
            else:
                self.mainImageSlider.setFixedWidth(widthSubWindow*.80)
        
            self.imageNumberLabel = QLabel()
        
            if maxNumberImages > 1:
                self.mainSliderLayout.addWidget(self.mainImageSlider)
                self.mainSliderLayout.addWidget(self.imageNumberLabel)

            if maxNumberImages < 11:
                self.mainSliderLayout.addStretch(1)
        except Exception as e:
            print('Error in ImageSliders.__addMainImageSliderToLayout: ' + str(e))
            logger.error('Error in ImageSliders.__addMainImageSliderToLayout: ' + str(e))

    
    def __setUpDisplayMultiSlidersCheckbox(self):
        self.showImageTypeListCheckBox = QCheckBox()
        self.checkboxLabel = QLabel("Display multiple Sliders")
        self.showImageTypeListCheckBox.stateChanged.connect(lambda state: self.displayHideMultiSliders(state))
        self.imageTypeLayout.addWidget(self.showImageTypeListCheckBox)
        self.imageTypeLayout.addWidget(self.checkboxLabel, stretch=1, alignment=Qt.AlignLeft)


    def displayHideMultiSliders(self, state):
        if state == Qt.Checked:
            self.__setUpImageTypeList()
            tagsList = [self.imageTypeList.item(i).text() for i in range(self.imageTypeList.count())]
            self.dicomTable = DICOM_to_DataFrame(self.imagePathList, tags=tagsList)
        elif state == Qt.Unchecked:
            #remove multiple sliders
            self.imageTypeList.deleteLater()
            self.dynamicListImageType.clear()
            self.listSortedImageSliders.clear()
            self.shapeList = []
            for rowNumber in range(0, self.sortedImageSliderLayout.rowCount()):
                self.sortedImageSliderLayout.removeRow(rowNumber)
                       

    def __setUpImageTypeList(self):
        self.imageTypeList = self.__createImageTypeList()
        self.imageTypeLayout.addWidget( self.imageTypeList,  alignment=Qt.AlignLeft)
        self.imageTypeLayout.addStretch(2)


    def __createImageTypeList(self):
        try:
            imageTypeList = QListWidget()
            imageTypeList.setFlow(QListView.Flow.LeftToRight)
            imageTypeList.setWrapping(True)
            imageTypeList.setMaximumHeight(25)
            self.dicomTable = DICOM_to_DataFrame(self.imagePathList, tags=listImageTypes) # Consider commenting if it takes too long
            for imageType in listImageTypes:
                # First, check if the DICOM tag exists in the images of the series.
                if ReadDICOM_Image.getImageTagValue(self.selectedImagePath, imageType):# is not None:
                    numAttr = len(self.dicomTable[imageType].unique())
                    #_, numAttr = ReadDICOM_Image.getSeriesTagValues(self.imagePathList, imageType)
                    # Then, check if there's more than 1 unique value for the corresponding DICOM tag
                    if numAttr > 1:
                        item = QListWidgetItem(imageType)
                        item.setToolTip("Tick the check box to create a subset of images based on {}".format(imageType))
                        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                        item.setCheckState(Qt.Unchecked)
                        imageTypeList.addItem(item)
               
            imageTypeList.itemClicked.connect(lambda item: self.__addRemoveSortedImageSlider(item))
            return imageTypeList
        except Exception as e:
            print('Error in ImageSliders.__createImageTypeList: ' + str(e))
            logger.error('Error in ImageSliders.__createImageTypeList: ' + str(e))


    def __addRemoveSortedImageSlider(self, item):
        try:
            if item.checkState() == Qt.Checked:
                self.__createSortedImageSlider(item.text())
            else:
                self.__removeSortedImageSlider(item.text())
        except Exception as e:
            print('Error in ImageSliders.__addRemoveSortedImageSlider: ' + str(e))
            logger.error('Error in ImageSliders.__addRemoveSortedImageSlider: ' + str(e))


    def __updateSliders(self):
        ##Remove sorted image sliders
        while self.sortedImageSliderLayout.rowCount() > 0:
            rowNumber = self.sortedImageSliderLayout.rowCount() - 1
            self.sortedImageSliderLayout.removeRow(rowNumber)
        ## Iterate through the list of checked DICOM tags
        self.shapeList = []
        self.listSortedImageSliders = []
        for tag in self.dynamicListImageType:
            numAttr = len(self.dicomTable[tag].unique())
            self.shapeList.append(numAttr)
            imageSlider = SortedImageSlider(tag)
            imageLabel = QLabel()
            layout = QHBoxLayout()
            layout.addWidget(imageSlider)
            layout.addWidget(imageLabel)
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
            if layout is not None:
                self.sortedImageSliderLayout.addRow(tag, layout)

        # Create a new slider with empty label string if there is more than 1 image per combination of tags
        if np.prod(self.shapeList) != len(self.imagePathList):
            imageSlider = SortedImageSlider('')
            imageLabel = QLabel()
            layout = QHBoxLayout()
            layout.addWidget(imageSlider)
            layout.addWidget(imageLabel)
            listSliderLabelPair = [imageSlider, imageLabel]
            self.listSortedImageSliders.append(listSliderLabelPair)
            imageSlider.setFocusPolicy(Qt.StrongFocus)
            imageSlider.setSingleStep(1)
            imageSlider.setTickPosition(QSlider.TicksBothSides)
            imageSlider.setTickInterval(1)
            imageSlider.setMinimum(1)
            if layout is not None:
                self.sortedImageSliderLayout.addRow('', layout)
            subTable = copy.copy(self.dicomTable)
            # Filter first values of each slider
            for tag in self.dynamicListImageType:
                listAttr = sorted(self.dicomTable[tag].unique())
                subTable = subTable[subTable[tag] == listAttr[0]]
            starting_point_lenght = len(subTable.index.to_list())
            imageSlider.setMaximum(starting_point_lenght)
            imageSlider.valueChanged.connect(self.__multipleImageSliderMoved)
            imageLabel.setText("image 1 of {}".format(starting_point_lenght))


    def __createSortedImageSlider(self, DicomAttribute):
        try:
            attributeList, _ = ReadDICOM_Image.getSeriesTagValues(self.imagePathList, DicomAttribute)
            attributeListUnique = []
            for x in attributeList:
                if x not in attributeListUnique:
                    attributeListUnique.append(x)
            self.dynamicListImageType.append(DicomAttribute)
            self.__updateSliders()
        except Exception as e:
            print('Error in ImageSliders.__createSortedImageSlider: ' + str(e))
            logger.exception('Error in ImageSliders.__createSortedImageSlider: ' + str(e))
    

    def __removeSortedImageSlider(self, DicomAttribute):
        try:
            attributeList, _ = ReadDICOM_Image.getSeriesTagValues(self.imagePathList, DicomAttribute)
            attributeListUnique = []
            for x in attributeList:
                if x not in attributeListUnique:
                    attributeListUnique.append(x)
            self.dynamicListImageType.remove(DicomAttribute)
            self.__updateSliders()
        except Exception as e:
            print('Error in ImageSliders.__removeSortedImageSlider: ' + str(e))
            logger.exception('Error in ImageSliders.__removeSortedImageSlider: ' + str(e))


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
        except Exception as e:
            print('Error in ImageSliders.__multipleImageSliderMoved: ' + str(e))
            logger.exception('Error in ImageSliders.__multipleImageSliderMoved: ' + str(e))
    

    def __setUpSliderResetButton(self):
        self.resetButton = QPushButton("Reset")
        self.resetButton.setToolTip("Return this screen to the state that it had when first opened")
        self.resetButton.clicked.connect(self.__resetSliders)
        self.imageTypeLayout.addWidget(self.resetButton)


    def __resetSliders(self):
        try:
            ##Remove sorted image sliders
            while self.sortedImageSliderLayout.rowCount() > 0:
                rowNumber = self.sortedImageSliderLayout.rowCount() - 1
                self.sortedImageSliderLayout.removeRow(rowNumber)

            #Uncheck all checkboxes in image type list 
            for index in xrange(self.imageTypeList.count()):
                self.imageTypeList.item(index).setCheckState(Qt.Unchecked)
            
            #Reinialise Global variables for the Multisliders
            self.listSortedImageSliders = []
            self.dynamicListImageType = []
            self.shapeList = []

            #Reset the main image slider
            self.__mainImageSliderMoved(1)
        except Exception as e:
            print('Error in ImageSliders.__resetSliders: ' + str(e))
            logger.error('Error in ImageSliders.__resetSliders: ' + str(e))


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
        

            
    