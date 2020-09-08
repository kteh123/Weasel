from PyQt5 import QtCore 
from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QApplication, 
                             QMdiSubWindow, QMenu, QAction,
                            QLabel, QProgressBar, QTreeWidget, QTreeWidgetItem)

import os
import sys
import logging
import time
import CoreModules.WEASEL.Menus  as menus
logger = logging.getLogger(__name__)


def createTreeBranch(self, branchName, branch, parent, treeWidgetItemCounter, branchList = None):
    branchID = branch.attrib['id']
    thisBranch = QTreeWidgetItem(parent)
    if type(branchList) == list:
        branchList.append(thisBranch)
    treeWidgetItemCounter += 1
    self.progBar.setValue(treeWidgetItemCounter)
    thisBranch.setText(0, branchName + " - {}".format(branchID))
    thisBranch.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
    #put a checkbox in front of this branch
    thisBranch.setFlags(thisBranch.flags() | Qt.ItemIsUserCheckable)
    thisBranch.setCheckState(0, Qt.Unchecked)
    thisBranch.setExpanded(True)
    return thisBranch, treeWidgetItemCounter


def createImageLeaf(self, image, seriesBranch, treeWidgetItemCounter):
    #Extract filename from file path
    if image.find('name').text:
        imageName = os.path.basename(image.find('name').text)
    else:
        imageName = 'Name missing'
    imageDate = image.find('date').text
    imageTime = image.find('time').text
    imagePath = image.find('name').text
    imageLeaf = QTreeWidgetItem(seriesBranch)
    imageLeaf.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
    #put a checkbox in front of each image
    imageLeaf.setFlags(imageLeaf.flags() | Qt.ItemIsUserCheckable)
    imageLeaf.setCheckState(0, Qt.Unchecked)
    imageLeaf.setText(0, ' Image - ' + imageName)
    imageLeaf.setText(1, imageDate)
    imageLeaf.setText(2, imageTime)
    imageLeaf.setText(3, imagePath)
    treeWidgetItemCounter += 1
    self.progBar.setValue(treeWidgetItemCounter)


def makeDICOMStudiesTreeView(self, XML_File_Path):
        """Uses an XML file that describes a DICOM file structure to build a
        tree view showing a visual representation of that file structure."""
        try:
            logger.info("TreeView.makeDICOMStudiesTreeView called")
            if os.path.exists(XML_File_Path):
                self.DICOM_XML_FilePath = XML_File_Path
                self.DICOMfolderPath, _ = os.path.split(XML_File_Path)
                self.objXMLReader.parseXMLFile(
                    self.DICOM_XML_FilePath)
           
                numSubjects, numStudies, numSeries, numImages, numTreeViewItems \
                    = self.objXMLReader.getNumberItemsInTreeView()

                QApplication.processEvents()
                widget = QWidget()
                widget.setLayout(QVBoxLayout()) 
                subWindow = QMdiSubWindow(self)
                subWindow.setWidget(widget)
                subWindow.setObjectName("tree_view")
                subWindow.setWindowTitle("DICOM Study Structure")
                height, width = self.getMDIAreaDimensions()
                subWindow.setGeometry(0, 0, width * 0.4, height)
                self.mdiArea.addSubWindow(subWindow)

                self.lblLoading = QLabel('<H4>You are loading {} subject(s) {} study(s), with {} series containing {} images</H4>'
                 .format(numSubjects, numStudies, numSeries, numImages))
                self.lblLoading.setWordWrap(True)

                widget.layout().addWidget(self.lblLoading)
                self.progBar = QProgressBar(self)
                widget.layout().addWidget(self.progBar)
                widget.layout().setAlignment(Qt.AlignTop)

                numSubjects, numStudies, numSeries, numImages, numTreeViewItems \
                    = self.objXMLReader.getNumberItemsInTreeView()

                self.progBar.show()
                self.progBar.setMaximum(numTreeViewItems)
                self.progBar.setValue(0)
                subWindow.show()

                QApplication.processEvents()
                self.treeView = QTreeWidget()
                self.treeView.setUniformRowHeights(True)
                self.treeView.setColumnCount(4)
                self.treeView.setHeaderLabels(["DICOM Files", "Date", "Time", "Path"])
                self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)

                treeWidgetItemCounter = 0 

                subjects = self.objXMLReader.getSubjects()
                for subject in subjects:
                    studyBranch, treeWidgetItemCounter = createTreeBranch(self, 
                                                                        "Subject", 
                                                                        subject, 
                                                                        self.treeView, 
                                                                        treeWidgetItemCounter)
                    
                    for study in subject:
                        studyBranch, treeWidgetItemCounter = createTreeBranch(self, 
                                                                            "Study", 
                                                                            study, 
                                                                            studyBranch, 
                                                                            treeWidgetItemCounter)
                       
                        self.seriesBranchList = []                                                    
                        for series in study:
                            seriesBranch, treeWidgetItemCounter = createTreeBranch(self, 
                                                                                   "Series", 
                                                                                   series, 
                                                                                   studyBranch, 
                                                                                   treeWidgetItemCounter,
                                                                                   self.seriesBranchList)

                            for image in series:
                                createImageLeaf(self, image, seriesBranch, treeWidgetItemCounter)
                           
                self.treeView.resizeColumnToContents(0)
                self.treeView.resizeColumnToContents(1)
                self.treeView.resizeColumnToContents(2)
                self.treeView.hideColumn(3)
                
                #Now collapse all series branches so as to hide the images
                for branch in self.seriesBranchList:
                    if branch !=0:
                        branch.setExpanded(False)

                self.treeView.customContextMenuRequested.connect(lambda pos: menus.buildContextMenu(self, pos))
                self.treeView.itemChanged.connect(lambda item: checkChildItems(item))
                self.treeView.itemClicked.connect(lambda item: checkParentItems(item))
                self.treeView.itemSelectionChanged.connect(lambda: toggleToolButtons(self))
                self.treeView.itemDoubleClicked.connect(lambda: menus.viewImage(self))
                self.treeView.itemClicked.connect(lambda: onTreeViewItemClicked(self, self.treeView.currentItem()))
                self.treeView.show()
                
                self.lblLoading.clear()
                self.progBar.hide()
                self.progBar.reset()
                widget.layout().addWidget(self.treeView)   
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            #filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            print('Error in TreeView.makeDICOMStudiesTreeView at line {}: '.format(line_number) + str(e)) 
            logger.error('Error in TreeView.makeDICOMStudiesTreeView at line {}: '.format(line_number) + str(e)) 


def refreshDICOMStudiesTreeView(self, newSeriesName = ''):
        """Uses an XML file that describes a DICOM file structure to build a
        tree view showing a visual representation of that file structure."""
        try:
            logger.info("TreeView.refreshDICOMStudiesTreeView called.")
            #Load and parse updated XML file
            self.objXMLReader.parseXMLFile(
                    self.DICOM_XML_FilePath)
            self.treeView.clear()
            self.treeView.setColumnCount(3)
            self.treeView.setHeaderLabels(["DICOM Files", "Date", "Time", "Path"])
            treeWidgetItemCounter = 0 
            
            self.seriesBranchList.clear()

            numSubjects, numStudies, numSeries, numImages, numTreeViewItems \
                    = self.objXMLReader.getNumberItemsInTreeView()
            self.lblLoading = QLabel('<H4>You are loading {} subject(s) {} study(s), with {} series containing {} images</H4>'
                 .format(numSubjects, numStudies, numSeries, numImages))
            self.lblLoading.setWordWrap(True)
            self.progBar.show()
            self.progBar.setMaximum(numTreeViewItems)
            self.progBar.setValue(0)

            subjects = self.objXMLReader.getSubjects()
            for subject in subjects:
                    studyBranch, treeWidgetItemCounter = createTreeBranch(self, 
                                                                        "Subject", 
                                                                        subject, 
                                                                        self.treeView, 
                                                                        treeWidgetItemCounter)
                    
                    for study in subject:
                        studyBranch, treeWidgetItemCounter = createTreeBranch(self, 
                                                                            "Study", 
                                                                            study, 
                                                                            studyBranch, 
                                                                            treeWidgetItemCounter)
                       
                        self.seriesBranchList = []                                                    
                        for series in study:
                            seriesBranch, treeWidgetItemCounter = createTreeBranch(self, 
                                                                                   "Series", 
                                                                                   series, 
                                                                                   studyBranch, 
                                                                                   treeWidgetItemCounter,
                                                                                   self.seriesBranchList)

                            for image in series:
                                createImageLeaf(self, image, seriesBranch, treeWidgetItemCounter)

            self.treeView.resizeColumnToContents(0)
            self.treeView.resizeColumnToContents(1)
            self.treeView.resizeColumnToContents(2)
            #Now collapse all series branches so as to hide the images
            #except the new series branch that has been created
            expandTreeViewBranch(self, newSeriesName)
            #If no tree view items are now selected,
            #disable items in the Tools menu.
            toggleToolButtons(self)
            self.lblLoading.clear()
            self.progBar.hide()
            self.progBar.reset()
            self.treeView.hideColumn(3)
            self.treeView.show()
        except Exception as e:
            print('Error in TreeView.refreshDICOMStudiesTreeView: ' + str(e))
            logger.error('Error in TreeView.refreshDICOMStudiesTreeView: ' + str(e))


def checkChildItems(item):
    """This function uses recursion to set the state of child checkboxes to
    match that of their parent.
    
    Input Parameters
    ****************
    item  - A QTreeWidgetItem whose checkbox state has just changed
    """
    logger.info("TreeView.checkChildItems called")
    try:
        if item.childCount() > 0:
            itemCount = item.childCount()
            for n in range(itemCount):
                childItem = item.child(n)
                #Give child checkboxes the same state as their 
                #parent checkboxe
                item.treeWidget().blockSignals(True)
                childItem.setCheckState(0, item.checkState(0))
                item.treeWidget().blockSignals(False)
                checkChildItems(childItem)
    except Exception as e:
            print('Error in TreeView.checkChildItems: ' + str(e))
            logger.error('Error in TreeView.checkChildItems: ' + str(e))


def checkParentItems(item):
    """This function uses recursion to set the state of Parent checkboxes to
    match collective state of their children.
    
    Input Parameters
    ****************
    item  - A QTreeWidgetItem whose checkbox state has just changed
    """
    logger.info("TreeView.checkParentItems called")
    try:
        if item.parent():
            item.treeWidget().blockSignals(True)
            if areAllChildrenChecked(item.parent()):
                item.parent().setCheckState(0, Qt.Checked)
            else:
                item.parent().setCheckState(0, Qt.Unchecked)
            item.treeWidget().blockSignals(False)
            checkParentItems(item.parent())
    except Exception as e:
            print('Error in TreeView.checkParentItems: ' + str(e))
            logger.error('Error in TreeView.checkParentItems: ' + str(e))


def areAllChildrenChecked(item):
    """ Returns True is all the children of a QTreeWidgetItem are checked
    otherwise returns False 

    Input Parameter
    ****************
    item  - A QTreeWidgetItem whose checkbox state has just changed

    Output Parameter
    *****************
    True or False
    """
    logger.info("TreeView.areAllChildrenChecked called")
    try:
        childCount = item.childCount()
        checkedCount = 0
        for n in range(childCount):
            childItem = item.child(n)
            if childItem.checkState(0)  == Qt.Checked:
                checkedCount +=1

        if checkedCount == childCount:
            return True
        else:
            return False
    except Exception as e:
            print('Error in TreeView.areAllChildrenChecked: ' + str(e))
            logger.error('Error in TreeView.areAllChildrenChecked: ' + str(e))


def expandTreeViewBranch(self, branchText = ''):
        """TO DO"""
        try:
            logger.info("TreeView.expandTreeViewBranch called.")
            for branch in self.seriesBranchList:
                seriesID = branch.text(0).replace('Series -', '')
                seriesID = seriesID.strip()
                if seriesID == branchText:
                    branch.setExpanded(True)
                else:
                    branch.setExpanded(False)
        except Exception as e:
            print('Error in TreeView.expandTreeViewBranch: ' + str(e))
            logger.error('Error in TreeView.expandTreeViewBranch: ' + str(e))


def isAnItemSelected(self):
    """Returns True is an item is selected DICOM
    tree view, else returns False"""
    try:
        logger.info("WEASEL isAnItemSelected called.")
        if self.treeView.selectedItems():
            return True
        else:
            return False
    except Exception as e:
        print('Error in isAnItemSelected: ' + str(e))
        logger.error('Error in isAnItemSelected: ' + str(e))


def isAnImageSelected(self):
        """Returns True is a single image is selected in the DICOM
        tree view, else returns False"""
        try:
            logger.info("WEASEL isAnImageSelected called.")
            selectedItem = self.treeView.currentItem()
            if selectedItem:
                if 'image' in selectedItem.text(0).lower():
                    return True
                else:
                    return False
            else:
               return False
        except Exception as e:
            print('Error in isAnImageSelected: ' + str(e))
            logger.error('Error in isAnImageSelected: ' + str(e))
            

def isASeriesSelected(self):
        """Returns True is a series is selected in the DICOM
        tree view, else returns False"""
        try:
            logger.info("WEASEL isASeriesSelected called.")
            selectedItem = self.treeView.currentItem()
            if selectedItem:
                if 'series' in selectedItem.text(0).lower():
                    return True
                else:
                    return False
            else:
               return False
        except Exception as e:
            print('Error in isASeriesSelected: ' + str(e))
            logger.error('Error in isASeriesSelected: ' + str(e))


def isAStudySelected(self):
        """Returns True is a study is selected in the DICOM
        tree view, else returns False"""
        try:
            logger.info("WEASEL isAStudySelected called.")
            selectedItem = self.treeView.currentItem()
            if selectedItem:
                if 'study' in selectedItem.text(0).lower():
                    return True
                else:
                    return False
            else:
               return False
        except Exception as e:
            print('Error in isAStudySelected: ' + str(e))
            logger.error('Error in isAStudySelected: ' + str(e))


def toggleToolButtons(self):
        """TO DO"""
        try:
            logger.info("TreeView.toggleToolButtons called.")
            tools = self.toolsMenu.actions()
            for tool in tools:
                if not tool.isSeparator():
                    if not(tool.data() is None):
                        #Assume not all tools will act on an image
                         #Assume all tools act on a series   
                        if isASeriesSelected(self):
                             tool.setEnabled(True)
                        elif isAnImageSelected(self):
                            if tool.data():
                                tool.setEnabled(True)
                            else:
                                tool.setEnabled(False) 
        except Exception as e:
            print('Error in TreeView.toggleToolButtons: ' + str(e))
            logger.error('Error in TreeView.toggleToolButtons: ' + str(e))



def onTreeViewItemClicked(self, item):
    """When a DICOM study treeview item is clicked, this function
    populates the relevant class variables that store the following
    DICOM image data: study ID, Series ID, Image name, image file path"""
    logger.info("TreeView.onTreeViewItemClicked called")
    try:
        #test for returning dictionary of studyIDs:seriesIDs
        #print(returnSelectedSeries(self))
        if item.text(0):
            selectedText = item.text(0)
            if 'study' in selectedText.lower():
                studyID = selectedText.replace('Study -', '').strip()
                self.selectedStudy = studyID
                self.selectedSeries = ''
                self.selectedImagePath = ''
                self.selectedImageName = ''
                self.statusBar.showMessage('Study - ' + studyID + ' selected.')
            elif 'series' in selectedText.lower():
                seriesID = selectedText.replace('Series -', '').strip()
                studyID = item.parent().text(0).replace('Study -', '').strip()
                self.selectedStudy = studyID
                self.selectedSeries = seriesID
                self.selectedImagePath = ''
                self.selectedImageName = ''
                fullSeriesID = studyID + ': ' + seriesID + ': no image selected.'
                self.statusBar.showMessage('Study and series - ' +  fullSeriesID)
            elif 'image' in selectedText.lower():
                imageID = selectedText.replace('Image -', '')
                imagePath =item.text(3)
                seriesID = item.parent().text(0).replace('Series -', '').strip()
                studyID = item.parent().parent().text(0).replace('Study -', '').strip()
                self.selectedStudy = studyID
                self.selectedSeries = seriesID
                self.selectedImagePath = imagePath.strip()
                self.selectedImageName = imageID.strip()
                fullImageID = studyID + ': ' + seriesID + ': '  + imageID
                self.statusBar.showMessage('Image - ' + fullImageID + ' selected.')

    except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            #filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            print('Error in TreeView.onTreeViewItemClicked at line {}: '.format(line_number) + str(e))
            logger.error('Error in TreeView.onTreeViewItemClicked at line {}: '.format(line_number) + str(e))


def returnSelectedSeries(self):
    """This function generates and returns a list of selected series."""
    logger.info("TreeView.returnSelectedSeries called")
    try:
        root = self.treeView.invisibleRootItem()
        studyCount = root.childCount()
        selectedSeriesDict = {}
        for i in range(studyCount):
            study = root.child(i)
            seriesCount = study.childCount()
            selectedSeriesDict[studyID] = []
            for n in range(seriesCount):
                series = study.child(n)
                if series.checkState(0) == Qt.Checked:
                    studyID = study.text(0).replace('Study -', '').strip()
                    selectedSeriesDict[studyID].append(series.text(0).replace('Series -', '').strip())

        return selectedSeriesDict
    except Exception as e:
            print('Error in TreeView.returnSelectedSeries: ' + str(e))
            logger.error('Error in TreeView.returnSelectedSeries: ' + str(e))