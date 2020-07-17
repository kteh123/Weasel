
from PyQt5 import QtCore 
from PyQt5.QtCore import  Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog,                            
        QMdiArea, QMessageBox, QWidget, QGridLayout, QVBoxLayout, QSpinBox,
        QMdiSubWindow, QGroupBox, QMainWindow, QHBoxLayout, QDoubleSpinBox,
        QPushButton, QStatusBar, QLabel, QAbstractSlider, QHeaderView,
        QTreeWidgetItem, QGridLayout, QSlider, QCheckBox, QLayout, 
        QProgressBar, QComboBox, QTableWidget, QTableWidgetItem, QFrame)
from PyQt5.QtGui import QCursor, QIcon, QColor

import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.readDICOM_Image as readDICOM_Image
import logging
logger = logging.getLogger(__name__)

def viewMetadata(self):
    """Creates a subwindow that displays a DICOM image's metadata. """
    try:
        logger.info("ViewMataData.viewMetadata called")
        if treeView.isAnImageSelected(self):
            imagePath = self.selectedImagePath
            imageName = self.selectedImageName
            dataset = readDICOM_Image.getDicomDataset(imagePath)
            displayMetaDataSubWindow(self, "Metadata for image {}".format(imageName), 
                                            dataset)
        elif treeView.isASeriesSelected(self):
            studyID = self.selectedStudy 
            seriesID = self.selectedSeries
            imageList = self.objXMLReader.getImagePathList(studyID, seriesID)
            firstImagePath = imageList[0]
            dataset = readDICOM_Image.getDicomDataset(firstImagePath)
            displayMetaDataSubWindow(self, "Metadata for series {}".format(seriesID), 
                                            dataset)
    except Exception as e:
        print('Error in ViewMataData.viewMetadata: ' + str(e))
        logger.error('Error in ViewMataData.viewMetadata: ' + str(e))


def displayMetaDataSubWindow(self, tableTitle, dataset):
    """
    Creates a subwindow that displays a DICOM image's metadata. 
    """
    try:
        logger.info('ViewMataData.displayMetaDataSubWindow called.')
        title = "DICOM Image Metadata"
                    
        widget = QWidget()
        widget.setLayout(QVBoxLayout()) 
        metaDataSubWindow = QMdiSubWindow(self)
        metaDataSubWindow.setAttribute(Qt.WA_DeleteOnClose)
        metaDataSubWindow.setWidget(widget)
        metaDataSubWindow.setObjectName("metaData_Window")
        metaDataSubWindow.setWindowTitle(title)
        height, width = self.getMDIAreaDimensions()
        metaDataSubWindow.setGeometry(width * 0.4,0,width*0.6,height)
        lblImageName = QLabel('<H4>' + tableTitle + '</H4>')
        widget.layout().addWidget(lblImageName)

        DICOM_Metadata_Table_View = buildTableView(self, dataset) 
            
        widget.layout().addWidget(DICOM_Metadata_Table_View)

        self.mdiArea.addSubWindow(metaDataSubWindow)
        metaDataSubWindow.show()
    except Exception as e:
        print('Error in : ViewMataData.displayMetaDataSubWindow' + str(e))
        logger.error('Error in : ViewMataData.displayMetaDataSubWindow' + str(e))


def buildTableView(self, dataset):
        """Builds a Table View displaying DICOM image metadata
        as Tag, name, VR & Value"""
        try:
            tableWidget = QTableWidget()
            tableWidget.setShowGrid(True)
            tableWidget.setColumnCount(4)

            #Create table header row
            headerItem = QTableWidgetItem(QTableWidgetItem("Tag\n")) 
            headerItem.setTextAlignment(Qt.AlignLeft)
            tableWidget.setHorizontalHeaderItem(0,headerItem)
            headerItem = QTableWidgetItem(QTableWidgetItem("Name \n")) 
            headerItem.setTextAlignment(Qt.AlignLeft)
            tableWidget.setHorizontalHeaderItem(1, headerItem)
            headerItem = QTableWidgetItem(QTableWidgetItem("VR \n")) 
            headerItem.setTextAlignment(Qt.AlignLeft)
            tableWidget.setHorizontalHeaderItem(2, headerItem)
            headerItem = QTableWidgetItem(QTableWidgetItem("Value\n")) 
            headerItem.setTextAlignment(Qt.AlignLeft)
            headerItem = tableWidget.setHorizontalHeaderItem(3 ,headerItem)

            for data_element in dataset:
                #Exclude pixel data from metadata listing
                if data_element.name == 'Pixel Data':
                    continue
                rowPosition = tableWidget.rowCount()
                tableWidget.insertRow(rowPosition)
                tableWidget.setItem(rowPosition , 0, 
                                QTableWidgetItem(str(data_element.tag)))
                tableWidget.setItem(rowPosition , 1, 
                                QTableWidgetItem(data_element.name))
                tableWidget.setItem(rowPosition , 2, 
                                QTableWidgetItem(data_element.VR))
                if data_element.VR == "UN" or data_element.VR == "OW":
                    try:
                        valueMetadata = str(data_element.value.decode('utf-8'))
                    except:
                        try:
                            valueMetadata = str(list(data_element))
                        except:
                            valueMetadata = str(data_element.value)
                else:
                    valueMetadata = str(data_element.value)
                tableWidget.setItem(rowPosition , 3, 
                                QTableWidgetItem(valueMetadata))


            #Resize columns to fit contents
            header = tableWidget.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

            return tableWidget
        except Exception as e:
            print('Error in : ViewMataData.buildTableView' + str(e))
            logger.error('Error in : ViewMataData.buildTableView' + str(e))


