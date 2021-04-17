
from PyQt5 import QtCore 
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog,                            
        QMdiArea, QMessageBox, QWidget, QGridLayout, QVBoxLayout, QSpinBox,
        QMdiSubWindow, QGroupBox, QMainWindow, QHBoxLayout, QDoubleSpinBox,
        QPushButton, QStatusBar, QLabel, QAbstractSlider, QHeaderView,
        QTreeWidgetItem, QGridLayout, QSlider, QCheckBox, QLayout, QAbstractItemView,
        QProgressBar, QComboBox, QTableWidget, QTableWidgetItem, QFrame)
from PyQt5.QtGui import QCursor, QIcon, QColor

import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.WEASEL.ReadDICOM_Image as ReadDICOM_Image
import os
import pydicom
import logging
logger = logging.getLogger(__name__)

def main(objWeasel):
    """Creates a subwindow that displays a DICOM image's metadata. """
    try:
        logger.info("ViewMetaData.viewMetadata called")
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))

        treeView.buildListsCheckedItems(objWeasel)

        if objWeasel.isASeriesChecked:
            if len(objWeasel.checkedSeriesList)>0: 
                for series in objWeasel.checkedSeriesList:
                    subjectName = series[0]
                    studyName = series[1]
                    seriesName = series[2]
                    imageList = treeView.returnSeriesImageList(objWeasel, subjectName, studyName, seriesName)
                    firstImagePath = imageList[0]
                    dataset = ReadDICOM_Image.getDicomDataset(firstImagePath)
                    displayMetaDataSubWindow(objWeasel, "Metadata for series {}".format(seriesName), 
                                            dataset)
        elif objWeasel.isAnImageChecked:
            if len(objWeasel.checkedImageList)>0: 
                for image in objWeasel.checkedImageList:
                    subjectID = image[0]
                    studyName = image[1]
                    seriesName = image[2]
                    imagePath = image[3]
                    imageName = os.path.basename(imagePath)
                    dataset = ReadDICOM_Image.getDicomDataset(imagePath)
                    displayMetaDataSubWindow(objWeasel, "Metadata for image {}".format(imageName), 
                                            dataset)

        QApplication.restoreOverrideCursor()
    except (IndexError, AttributeError):
                QApplication.restoreOverrideCursor()
                msgBox = QMessageBox()
                msgBox.setWindowTitle("View DICOM Metadata")
                msgBox.setText("Select either a series or an image")
                msgBox.exec()
    except Exception as e:
        print('Error in ViewMetaData.viewMetadata: ' + str(e))
        logger.error('Error in ViewMetaData.viewMetadata: ' + str(e))


def displayMetaDataSubWindow(objWeasel, tableTitle, dataset):
    """
    Creates a subwindow that displays a DICOM image's metadata. 
    """
    try:
        logger.info('ViewMetaData.displayMetaDataSubWindow called.')
        title = "DICOM Image Metadata"
                    
        widget = QWidget()
        widget.setLayout(QVBoxLayout()) 
        metaDataSubWindow = QMdiSubWindow(objWeasel)
        metaDataSubWindow.setAttribute(Qt.WA_DeleteOnClose)
        metaDataSubWindow.setWidget(widget)
        metaDataSubWindow.setObjectName("metaData_Window")
        metaDataSubWindow.setWindowTitle(title)
        height, width = objWeasel.getMDIAreaDimensions()
        metaDataSubWindow.setGeometry(width * 0.4,0,width*0.6,height)
        lblImageName = QLabel('<H4>' + tableTitle + '</H4>')
        widget.layout().addWidget(lblImageName)

        DICOM_Metadata_Table_View = buildTableView(objWeasel, dataset) 
            
        widget.layout().addWidget(DICOM_Metadata_Table_View)

        objWeasel.mdiArea.addSubWindow(metaDataSubWindow)
        metaDataSubWindow.show()
    except Exception as e:
        print('Error in : ViewMetaData.displayMetaDataSubWindow' + str(e))
        logger.error('Error in : ViewMetaData.displayMetaDataSubWindow' + str(e))


def iterateSequenceTag(table, dataset, level=">"):
    try:
        for data_element in dataset:
            if isinstance(data_element, pydicom.dataset.Dataset):
                table = iterateSequenceTag(table, data_element, level=level)
            else:
                rowPosition = table.rowCount()
                table.insertRow(rowPosition)
                table.setItem(rowPosition , 0, QTableWidgetItem(level + str(data_element.tag)))
                table.setItem(rowPosition , 1, QTableWidgetItem(data_element.name))
                table.setItem(rowPosition , 2, QTableWidgetItem(data_element.VR))
                if data_element.VR == "OW" or data_element.VR == "OB":
                    try:
                        valueMetadata = str(data_element.value.decode('utf-8'))
                    except:
                        try:
                            valueMetadata = str(list(data_element))
                        except:
                            valueMetadata = str(data_element.value)
                else:
                    valueMetadata = str(data_element.value)
                if data_element.VR == "SQ":
                    table.setItem(rowPosition , 3, QTableWidgetItem(""))
                    table = iterateSequenceTag(table, data_element, level=level+">")
                    level = level[:-1]
                else:
                    table.setItem(rowPosition , 3, QTableWidgetItem(valueMetadata))
        return table
    except Exception as e:
        print('Error in : ViewMetaData.iterateSequenceTag' + str(e))
        logger.error('Error in : ViewMetaData.iterateSequenceTag' + str(e))


def buildTableView(objWeasel, dataset):
        """Builds a Table View displaying DICOM image metadata
        as Tag, name, VR & Value"""
        try:
            tableWidget = QTableWidget()
            tableWidget.setShowGrid(True)
            tableWidget.setColumnCount(4)
            tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
            #tableWidget.setEditTriggers(QAbstractItemView.DoubleClicked)

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
            tableWidget.setHorizontalHeaderItem(3 , headerItem)

            if dataset:
                # Loop through the DICOM group (0002, XXXX) first
                for meta_element in dataset.file_meta:
                    rowPosition = tableWidget.rowCount()
                    tableWidget.insertRow(rowPosition)
                    tableWidget.setItem(rowPosition , 0, 
                                    QTableWidgetItem(str(meta_element.tag)))
                    tableWidget.setItem(rowPosition , 1, 
                                    QTableWidgetItem(meta_element.name))
                    tableWidget.setItem(rowPosition , 2, 
                                    QTableWidgetItem(meta_element.VR))
                    if meta_element.VR == "OW" or meta_element.VR == "OB" or meta_element.VR == "UN":
                        try:
                            valueMetadata = str(list(meta_element))
                        except:
                            valueMetadata = str(meta_element.value)
                    else:
                        valueMetadata = str(meta_element.value)
                    if meta_element.VR == "SQ":
                        tableWidget.setItem(rowPosition , 3, QTableWidgetItem(""))
                        tableWidget = iterateSequenceTag(tableWidget, meta_element, level=">")
                    else:
                        tableWidget.setItem(rowPosition , 3, QTableWidgetItem(valueMetadata))
                
                for data_element in dataset:
                    # Exclude pixel data from metadata listing
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
                    if data_element.VR == "OW" or data_element.VR == "OB" or data_element.VR == "UN":
                        try:
                            #valueMetadata = str(data_element.value.decode('utf-8'))
                            valueMetadata = str(list(data_element))
                        except:
                            try:
                                #valueMetadata = str(list(data_element))
                                valueMetadata = str(data_element.value.decode('utf-8'))
                            except:
                                valueMetadata = str(data_element.value)
                    else:
                        valueMetadata = str(data_element.value)
                    if data_element.VR == "SQ":
                        tableWidget.setItem(rowPosition , 3, QTableWidgetItem(""))
                        tableWidget = iterateSequenceTag(tableWidget, data_element, level=">")
                    else:
                        tableWidget.setItem(rowPosition , 3, QTableWidgetItem(valueMetadata))


            #Resize columns to fit contents
            header = tableWidget.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode(QHeaderView.AdjustToContentsOnFirstShow))
            tableWidget.setWordWrap(True)
            #tableWidget.resizeRowsToContents()

            return tableWidget
        except Exception as e:
            print('Error in : ViewMetaData.buildTableView' + str(e))
            logger.error('Error in : ViewMetaData.buildTableView' + str(e))


