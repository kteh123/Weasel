from PyQt5 import QtCore 
from PyQt5.QtCore import  Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon,  QCursor
from PyQt5.QtWidgets import (QFileDialog, QApplication,                           
                            QMessageBox, 
                            QWidget,
                            QFormLayout,
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


from CoreModules.WEASEL.UserImageColourSelection import UserSelection
import CoreModules.WEASEL.ReadDICOM_Image as ReadDICOM_Image

import logging
logger = logging.getLogger(__name__)

listImageTypes = ["SliceLocation", "AcquisitionTime", "AcquisitionNumber", 
                  "FlipAngle", "InversionTime", "EchoTime", 
                  (0x2005, 0x1572)] # This last element is a good example of private tag


class SortedImageSlider(QSlider):
    """Subclass of the QSlider class with the added property attribute 
    which identifies what the image subset has been filtered for"""
    def __init__(self,  DicomAttribute): 
       super().__init__(orientation=Qt.Horizontal)
       self.attribute =  DicomAttribute
       self.setToolTip("Images sorted according to {}".format(DicomAttribute))


class ImageSliders:
    """Creates a custom, composite widget composed of one or more sliders for 
    navigating a DICOM series of images."""

    sliderMoved = pyqtSignal(str)

    def __init__(self,  pointerToWeasel, subjectID, 
                 studyID, seriesID, imagePathList):

        self.imagePathList = imagePathList
        self.subjectID = subjectID
        self.studyID = studyID
        self.seriesID = seriesID
        ##set up list of lists to hold user selected colour table and level data
        #self.userSelectionDict = {}
        #userSelectionList = [[os.path.basename(imageName), 'default', -1, -1]
        #                    for imageName in self.imagePathList]
        ##add user selection object to dictionary
        #self.userSelectionDict[self.seriesID] = UserSelection(userSelectionList)
        
        # Global variables for the Multisliders
        self.dynamicListImageType = []
        self.shapeList = []
        self.arrayForMultiSlider = self.imagePathList # Please find the explanation of this variable at multipleImageSliderMoved(self)
        self.seriesToFormat = Series(self.pointerToWeasel, self.subjectID, self.studyID, self.seriesID, listPaths=self.imagePathList)
        #A list of the sorted image sliders, 
        #updated as they are added and removed 
        #from the subwindow
        self.listSortedImageSliders = []  

        #Create the custom, composite sliders widget
        self.setUpLayouts()
        self.createMainImageSlider()
        self.addMainImageSliderToLayout()
        self.setUpImageTypeList()
        self.setUpSliderResetButton()

        #Display the first image in the viewer
        self.mainImageSliderMoved()


    def getCustomSliderWidget(self):
        """Passes the composite slider widget to the
        parent layout on the subwindow"""
        return self.mainVerticalLayout


    def setUpLayouts(self):
        try:
            self.mainVerticalLayout = QVBoxLayout()
        
            self.mainSliderLayout = QHBoxLayout()
            self.imageTypeLayout = QHBoxLayout()
            self.sortedImageSliderLayout = QFormLayout()
        
            self.mainVerticalLayout.addLayout(self.mainSliderLayout)
            self.mainVerticalLayout.addLayout(self.imageTypeLayout)
            self.mainVerticalLayout.addLayout(self.sortedImageSliderLayout)
        except Exception as e:
            print('Error in ImageSliders.setUpLayouts: ' + str(e))
            logger.error('Error in ImageSliders.setUpLayouts: ' + str(e))

    
    def createMainImageSlider(self): 
        try:
            self.mainImageSlider = QSlider(Qt.Horizontal)
            self.mainImageSlider.setFocusPolicy(Qt.StrongFocus) # This makes the slider work with arrow keys on Mac OS
            self.mainImageSlider.setToolTip("Use this slider to navigate the series of DICOM images")
            self.mainImageSlider.setSingleStep(1)
            self.mainImageSlider.setTickPosition(QSlider.TicksBothSides)
            self.mainImageSlider.setTickInterval(1)
            self.mainImageSlider.setMinimum(1)
            self.mainImageSlider.valueChanged.connect(self.mainImageSliderMoved)
        except Exception as e:
            print('Error in ImageSliders.createMainImageSlider: ' + str(e))
            logger.error('Error in ImageSliders.createMainImageSlider: ' + str(e))

    
    def mainImageSliderMoved(self, imageNumber=None):
        """On the Multiple Image Display sub window, this
        function is called when the image slider is moved. 
        It causes the next image in imageList to be displayed
        """
        try: 
            #obj = self.userSelectionDict[self.seriesID]
            logger.info("ImageSliders.mainImageSliderMoved called")
            if imageNumber:
                self.mainImageSlider.setValue(imageNumber)
            else:
                imageNumber = self.mainImageSlider.value()
            currentImageNumber = imageNumber - 1
            if currentImageNumber >= 0:
                maxNumberImages = str(len(self.imagePathList))
                imageNumberString = "image {} of {}".format(currentImageNumber, maxNumberImages)
                self.imageNumberLabel.setText(imageNumberString)
                self.selectedImagePath = self.imagePathList[currentImageNumber]
                #Send the current image to the parent application
                self.sliderMoved.emit(self.selectedImagePath)
                #print("mainImageSliderMoved before={}".format(self.selectedImagePath))
                #self.pixelArray = ReadDICOM_Image.returnPixelArray(self.selectedImagePath)
                #self.lut = None
                #Get colour table of the image to be displayed
                #if obj.getSeriesUpdateStatus():
                #    self.colourTable = self.cmbColours.currentText()
                #elif obj.getImageUpdateStatus():
                #    self.colourTable, _, _ = obj.returnUserSelection(currentImageNumber)  
                #    if self.colourTable == 'default':
                #        self.colourTable, self.lut = ReadDICOM_Image.getColourmap(self.selectedImagePath)
                #    #print('apply User Selection, colour table {}, image number {}'.format(colourTable,currentImageNumber ))
                #else:
                #    self.colourTable, self.lut = ReadDICOM_Image.getColourmap(self.selectedImagePath)

                ##display above colour table in colour table dropdown list
                #self.displayColourTableInComboBox()

                #self.displayPixelArray() 
                
                #self.setWindowTitle(self.subjectID + ' - ' + self.studyID + ' - '+ self.seriesID + ' - ' 
                #         + os.path.basename(self.selectedImagePath))
        except TypeError as e: 
            print('Type Error in ImageSliders.mainImageSliderMoved: ' + str(e))
            logger.error('Type Error in ImageSliders.mainImageSliderMoved: ' + str(e))
        except Exception as e:
            print('Error in ImageSliders.mainImageSliderMoved: ' + str(e))
            logger.error('Error in ImageSliders.mainImageSliderMoved: ' + str(e))


    def addMainImageSliderToLayout(self):
        """Configures the width of the slider according to the number of images
        it must navigate and adds it and its associated label to the main slider
        layout"""
        try:
            maxNumberImages = len(self.imagePathList)
            self.mainImageSlider.setMaximum(maxNumberImages)
            if maxNumberImages < 4:
                self.mainImageSlider.setFixedWidth(self.width()*.2)
            elif maxNumberImages > 3 and maxNumberImages < 11:
                self.mainImageSlider.setFixedWidth(self.width()*.5)
            else:
                self.mainImageSlider.setFixedWidth(self.width()*.80)
        
            self.imageNumberLabel = QLabel()
        
            if maxNumberImages > 1:
                self.mainSliderLayout.addWidget(self.mainImageSlider)
                self.mainSliderLayout.addWidget(self.imageNumberLabel)
        
            if maxNumberImages < 11:
                self.mainSliderLayout.addStretch(1)
        except Exception as e:
            print('Error in ImageSliders.addMainImageSliderToLayout: ' + str(e))
            logger.error('Error in ImageSliders.addMainImageSliderToLayout: ' + str(e))

    
    def setUpImageTypeList(self):
        self.imageTypeList = self.createImageTypeList()
        self.imageTypeLayout.addWidget(self.imageTypeList)


    def createImageTypeList(self):
        try:
            imageTypeList = QListWidget()
            imageTypeList.setFlow(QListView.Flow.LeftToRight)
            imageTypeList.setWrapping(True)
            imageTypeList.setMaximumHeight(25)
            for imageType in listImageTypes:
                # First, check if the DICOM tag exists in the images of the series.
                if ReadDICOM_Image.getImageTagValue(self.selectedImagePath, imageType) is not None:
                    _, numAttr = ReadDICOM_Image.getSeriesTagValues(self.imagePathList, imageType)
                    # Then, check if there's more than 1 unique value for the corresponding DICOM tag
                    if numAttr > 1:
                        item = QListWidgetItem(imageType)
                        item.setToolTip("Tick the check box to create a subset of images based on {}".format(imageType))
                        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                        item.setCheckState(Qt.Unchecked)
                        imageTypeList.addItem(item)
               
            imageTypeList.itemClicked.connect(lambda item: self.addRemoveSortedImageSlider(item))
            return imageTypeList
        except Exception as e:
            print('Error in ImageSliders.createImageTypeList: ' + str(e))
            logger.error('Error in ImageSliders.createImageTypeList: ' + str(e))


    def addRemoveSortedImageSlider(self, item):
        try:
            if item.checkState() == Qt.Checked:
                imageSliderLayout = self.createSortedImageSliderLayout(item.text()) 
                self.sortedImageSliderLayout.addRow(item.text(), imageSliderLayout)  
            else:
                for rowNumber in range(0, self.sortedImageSliderLayout.rowCount()):
                    layoutItem = self.sortedImageSliderLayout.itemAt(rowNumber, QFormLayout.LabelRole)
                    if item.text() == layoutItem.widget().text():
                        self.sortedImageSliderLayout.removeRow(rowNumber)
                        self.dynamicListImageType.remove(item.text())
                        for sliderImagePair in self.listSortedImageSliders: 
                            if sliderImagePair[0].attribute == item.text(): 
                                self.listSortedImageSliders.remove(sliderImagePair) 
                        self.shapeList = []
                        if len(self.dynamicListImageType) > 1:
                            # Loop through all the existing sliders at this stage and update the setMaximum of each slider
                            for index, tag in enumerate(self.dynamicListImageType):
                                _, numAttr = ReadDICOM_Image.getSeriesTagValues(self.imagePathList, tag)
                                self.shapeList.append(numAttr)
                                self.sortedImageSliderLayout.itemAt(2*index+1).layout().itemAt(0).widget().setMaximum(numAttr)
                                currentImageNumber = self.sortedImageSliderLayout.itemAt(2*index+1).layout().itemAt(0).widget().value()
                                labelText = "image {} of {}".format(currentImageNumber, numAttr)
                                self.sortedImageSliderLayout.itemAt(2*index+1).layout().itemAt(1).widget().setText(labelText)
                            # Sort according to the tags
                            self.seriesToFormat.sort(*self.dynamicListImageType)
                            # Reshape the self.arrayForMultiSlider list of paths
                            self.arrayForMultiSlider = self.reshapePathsList()
                        elif len(self.dynamicListImageType) == 1:
                            sortedSequencePath, _, _, _ = ReadDICOM_Image.sortSequenceByTag(self.imagePathList, self.dynamicListImageType[0])
                            self.arrayForMultiSlider = sortedSequencePath
                            self.sortedImageSliderLayout.itemAt(1).layout().itemAt(0).widget().setMaximum(len(sortedSequencePath))
                            currentImageNumber = self.sortedImageSliderLayout.itemAt(1).layout().itemAt(0).widget().value()
                            labelText = "image {} of {}".format(currentImageNumber, len(sortedSequencePath))
                            self.sortedImageSliderLayout.itemAt(1).layout().itemAt(1).widget().setText(labelText)
                        else:
                            self.arrayForMultiSlider = self.imagePathList
                            self.sortedImageSliderLayout.itemAt(1).layout().itemAt(0).widget().setMaximum(len(self.imagePathList)) 
                            currentImageNumber = self.sortedImageSliderLayout.itemAt(1).layout().itemAt(0).widget().value()
                            labelText = "image {} of {}".format(currentImageNumber, len(self.imagePathList))
                            self.sortedImageSliderLayout.itemAt(1).layout().itemAt(1).widget().setText(labelText)
        except Exception as e:
            print('Error in ImageSliders.addRemoveSortedImageSlider: ' + str(e))
            logger.error('Error in ImageSliders.addRemoveSortedImageSlider: ' + str(e))


    def createSortedImageSliderLayout(self, DicomAttribute):  
        try:
            imageSlider = SortedImageSlider(DicomAttribute)
            imageLabel = QLabel()
            layout = QHBoxLayout()
            layout.addWidget(imageSlider)
            layout.addWidget(imageLabel)
            listSliderLabelPair = [imageSlider, imageLabel]
            self.listSortedImageSliders.append(listSliderLabelPair)
            # This makes the slider work with arrow keys on Mac OS
            imageSlider.setFocusPolicy(Qt.StrongFocus) 
            self.dynamicListImageType.append(DicomAttribute)
            # If there is more that 1 slider in the multi-slider layout
            if len(self.dynamicListImageType) > 1:
                # Loop through all the existing sliders at this stage and update the setMaximum of each slider
                self.shapeList = []
                for index, tag in enumerate(self.dynamicListImageType[:-1]):
                    _, numAttr = ReadDICOM_Image.getSeriesTagValues(self.imagePathList, tag)
                    self.shapeList.append(numAttr)
                    self.sortedImageSliderLayout.itemAt(2*index+1).layout().itemAt(0).widget().setMaximum(numAttr)
                    currentImageNumber = self.sortedImageSliderLayout.itemAt(2*index+1).layout().itemAt(0).widget().value()
                    labelText = "image {} of {}".format(currentImageNumber, numAttr)
                    self.sortedImageSliderLayout.itemAt(2*index+1).layout().itemAt(1).widget().setText(labelText)
                _, maxNumberImages = ReadDICOM_Image.getSeriesTagValues(self.imagePathList, DicomAttribute)
                self.shapeList.append(maxNumberImages)
                # Sort according to the tags
                self.seriesToFormat.sort(*self.dynamicListImageType)
                # Reshape the self.arrayForMultiSlider list of paths
                if np.prod(self.shapeList) > len(self.imagePathList):
                    QMessageBox.warning(self, "Maximum dimension exceeded", "The number of slider combinations exceeds the total number of images in the series")
                    self.listSortedImageSliders.remove(listSliderLabelPair)
                    return 
                else:
                    self.arrayForMultiSlider = self.reshapePathsList()
            else:
                sortedSequencePath, _, _, _ = ReadDICOM_Image.sortSequenceByTag(self.imagePathList, DicomAttribute)
                maxNumberImages = len(self.imagePathList)
                self.arrayForMultiSlider = sortedSequencePath
            imageSlider.setMaximum(maxNumberImages)
            imageSlider.setSingleStep(1)
            imageSlider.setTickPosition(QSlider.TicksBothSides)
            imageSlider.setTickInterval(1)
            imageSlider.setMinimum(1)
            imageSlider.valueChanged.connect(self.multipleImageSliderMoved)
            imageLabel.setText("image 1 of {}".format(maxNumberImages))
            
            return layout
        except Exception as e:
            print('Error in ImageSliders.createSortedImageSliderLayout: ' + str(e))
            logger.exception('Error in ImageSliders.createSortedImageSliderLayout: ' + str(e))
    

    def setUpSliderResetButton(self):
        self.resetButton = QPushButton("Reset")
        self.resetButton.setToolTip("Return this screen to the state that it had when first opened")
        self.resetButton.clicked.connect(self.resetSliders)
        self.imageTypeLayout.addWidget(self.resetButton)


    
        

            
    