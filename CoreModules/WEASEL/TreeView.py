from PyQt5 import QtCore 
from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QApplication, QAbstractItemView,
                             QMdiSubWindow, QMenu, QAction,
                            QLabel, QProgressBar, QTreeWidget, QTreeWidgetItem)
import os
import sys
import logging
import time
from collections import defaultdict
import CoreModules.WEASEL.Menus  as menus
import Developer.MenuItems.ViewImage  as viewImage
logger = logging.getLogger(__name__)


def createTreeBranch(self, branchName, branch, parent, treeWidgetItemCounter):
    try:
        branchID = branch.attrib['id']
        thisBranch = QTreeWidgetItem(parent)
        treeWidgetItemCounter += 1
        self.progBar.setValue(treeWidgetItemCounter)
        thisBranch.setText(0, branchName + " - {}".format(branchID))
        thisBranch.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        #put a checkbox in front of this branch
        thisBranch.setFlags(thisBranch.flags() | Qt.ItemIsUserCheckable)
        thisBranch.setCheckState(0, Qt.Unchecked)
        thisBranch.setExpanded(True)
        return thisBranch, treeWidgetItemCounter
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        #filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print('Error in TreeView.createTreeBranch at line {}: '.format(line_number) + str(e)) 
        logger.error('Error in TreeView.createTreeBranch at line {}: '.format(line_number) + str(e)) 


def createImageLeaf(self, image, seriesBranch, treeWidgetItemCounter):
    try:
        #Extract filename from file path
        if image:
            if image.find('label') is None:
                imageName = os.path.basename(image.find('name').text)
            else:
                imageName = image.find('label').text
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
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        #filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print('Error in TreeView.createImageLeaf at line {}: '.format(line_number) + str(e)) 
        logger.error('Error in TreeView.createImageLeaf at line {}: '.format(line_number) + str(e)) 


def resizeTreeViewColumns(self):
    self.treeView.resizeColumnToContents(0)
    self.treeView.resizeColumnToContents(1)
    self.treeView.resizeColumnToContents(2)
    self.treeView.hideColumn(3)


def closeProgressBar(self):
    self.lblLoading.clear()
    self.progBar.hide()
    self.progBar.reset()


def buildTreeView(self):
    try:
        self.treeView.clear()
        treeWidgetItemCounter = 0 
        subjects = self.objXMLReader.getSubjects()
        for subject in subjects:
            subjectBranch, treeWidgetItemCounter = createTreeBranch(self, 
                                                                "Subject", 
                                                                subject, 
                                                                self.treeView, 
                                                                treeWidgetItemCounter)
        
            for study in subject:
                studyBranch, treeWidgetItemCounter = createTreeBranch(self, 
                                                                    "Study", 
                                                                    study, 
                                                                    subjectBranch, 
                                                                    treeWidgetItemCounter)
                                                             
                for series in study:
                    seriesBranch, treeWidgetItemCounter = createTreeBranch(self, 
                                                                           "Series", 
                                                                           series, 
                                                                           studyBranch, 
                                                                           treeWidgetItemCounter)
    
                    for image in series:
                        createImageLeaf(self, image, seriesBranch, treeWidgetItemCounter)
             
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        #filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print('Error in TreeView.buildTreeView at line {}: '.format(line_number) + str(e)) 
        logger.error('Error in TreeView.buildTreeView at line {}: '.format(line_number) + str(e)) 


def makeDICOMStudiesTreeView(self, XML_File_Path):
        """Uses an XML file that describes a DICOM file structure to build a
        tree view showing a visual representation of that file structure."""
        try:
            logger.info("TreeView.makeDICOMStudiesTreeView called")
            if os.path.exists(XML_File_Path):
                widget = QWidget()
                widget.setLayout(QVBoxLayout()) 
                subWindow = QMdiSubWindow(self)
                subWindow.setWidget(widget)
                subWindow.setObjectName("tree_view")
                subWindow.setWindowTitle("DICOM Study Structure")
                height, width = self.getMDIAreaDimensions()
                subWindow.setGeometry(0, 0, width * 0.4, height)
                self.mdiArea.addSubWindow(subWindow)
                subWindow.show()

                self.DICOM_XML_FilePath = XML_File_Path
                self.DICOMfolderPath, _ = os.path.split(XML_File_Path)
                self.objXMLReader.parseXMLFile(self.DICOM_XML_FilePath)
                
                self.lblLoading = QLabel()
                widget.layout().addWidget(self.lblLoading)

                self.progBar = QProgressBar(self)
                widget.layout().addWidget(self.progBar)
                widget.layout().setAlignment(Qt.AlignTop)

                numTreeViewItems = setupLoadingLabel(self, self.lblLoading)
                initialiseProgressBar(self, numTreeViewItems)
               
                self.treeView = QTreeWidget()
                #Enable multiple selection using up arrow and Ctrl keys
                self.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
                self.treeView.setUniformRowHeights(True)
                self.treeView.setColumnCount(4)
                self.treeView.setHeaderLabels(["DICOM Files", "Date", "Time", "Path"])
                self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
                widget.layout().addWidget(self.treeView)

                buildTreeView(self)

                self.treeView.customContextMenuRequested.connect(lambda pos: menus.displayContextMenu(self, pos))
                self.treeView.itemChanged.connect(lambda item: checkChildItems(item))
                self.treeView.itemClicked.connect(lambda item: checkParentItems(item))
                self.treeView.itemSelectionChanged.connect(lambda: toggleToolButtons(self))
                self.treeView.itemDoubleClicked.connect(lambda: viewImage.main(self))
                self.treeView.itemClicked.connect(lambda: onTreeViewItemClicked(self, self.treeView.currentItem()))
                self.treeView.show()
                
                resizeTreeViewColumns(self)
                collapseSeriesBranches(self.treeView.invisibleRootItem())
                closeProgressBar(self)    
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            #filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            print('Error in TreeView.makeDICOMStudiesTreeView at line {}: '.format(line_number) + str(e)) 
            logger.error('Error in TreeView.makeDICOMStudiesTreeView at line {}: '.format(line_number) + str(e)) 


def setupLoadingLabel(self, lblLoading):
    numSubjects, numStudies, numSeries, numImages, numTreeViewItems \
            = self.objXMLReader.getNumberItemsInTreeView()
    lblLoading.setText('<H4>You are loading {} subject(s) {} study(s), with {} series containing {} images</H4>'
         .format(numSubjects, numStudies, numSeries, numImages))
    self.lblLoading.setWordWrap(True)
    return numTreeViewItems


def initialiseProgressBar(self, numTreeViewItems):
    self.progBar.show()
    self.progBar.setMaximum(numTreeViewItems)
    self.progBar.setValue(0)


def refreshDICOMStudiesTreeView(self, newSeriesName = ''):
        """Uses an XML file that describes a DICOM file structure to build a
        tree view showing a visual representation of that file structure."""
        try:
            logger.info("TreeView.refreshDICOMStudiesTreeView called.")
            #Load and parse updated XML file
            self.objXMLReader.parseXMLFile(self.DICOM_XML_FilePath)
            # Joao Sousa suggestion
            # self.treeView.hide()
            numTreeViewItems = setupLoadingLabel(self, self.lblLoading)
            initialiseProgressBar(self, numTreeViewItems)

            buildTreeView(self)

            #resizeTreeViewColumns(self)
            closeProgressBar(self)

            #If no tree view items are now selected,
            #disable items in the Tools menu.
            toggleToolButtons(self)
            # Joao Sousa suggestion
            # self.treeView.show()
            # collapseSeriesBranches(self.treeView.invisibleRootItem())

            #Now collapse all series branches so as to hide the images
            #except the new series branch that has been created
            expandTreeViewBranch(self.treeView.invisibleRootItem(), newSeriesName)
        except Exception as e:
            print('Error in TreeView.refreshDICOMStudiesTreeView: ' + str(e))
            logger.error('Error in TreeView.refreshDICOMStudiesTreeView: ' + str(e))


def collapseSeriesBranches(item):
    """This function uses recursion to colapse all series branches
    
    Input Parameters
    ****************
    item  - A QTreeWidgetItem 
    """
    logger.info("TreeView.collapseSeriesBranches called")
    try:
        if item.childCount() > 0:
            itemCount = item.childCount()
            for n in range(itemCount):
                childItem = item.child(n)
                if 'series' in childItem.text(0).lower():
                    item.treeWidget().blockSignals(True)
                    childItem.setExpanded(False)
                    item.treeWidget().blockSignals(False)
                else:
                    collapseSeriesBranches(childItem)
    except Exception as e:
            print('Error in TreeView.collapseSeriesBranches: ' + str(e))
            logger.error('Error in TreeView.collapseSeriesBranches: ' + str(e))


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
                #childItem.setSelected(item.checkState(0))
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
                #item.parent().setSelected(True)
            else:
                item.parent().setCheckState(0, Qt.Unchecked)
                #item.parent().setSelected(False)
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


def expandTreeViewBranch(item, newSeriesName = ''):
        """TO DO"""
        try:
            logger.info("TreeView.expandTreeViewBranch called.")
            if item.childCount() > 0:
                itemCount = item.childCount()
                for n in range(itemCount):
                    childItem = item.child(n)
                    branchText = childItem.text(0).lower()
                    if 'series' in branchText:
                        seriesName = branchText.replace('series -', '').strip()
                        item.treeWidget().blockSignals(True)
                        if seriesName == newSeriesName.lower():
                            childItem.setExpanded(True)
                        else:
                            childItem.setExpanded(False)
                        item.treeWidget().blockSignals(False)
                    else:
                        expandTreeViewBranch(childItem, newSeriesName)
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
            for menu in self.listMenus:
                menuItems = menu.actions()
                for menuItem in menuItems:
                    if not menuItem.isSeparator():
                        if not(menuItem.data() is None):
                            #Assume not all tools will act on an image
                             #Assume all tools act on a series   
                            if isASeriesSelected(self):
                                 menuItem.setEnabled(True)
                            elif isAnImageSelected(self):
                                if menuItem.data():
                                    menuItem.setEnabled(True)
                                else:
                                    menuItem.setEnabled(False) 
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
        # print(returnSelectedSeries(self))
        if item:
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
        subjectCount = root.childCount()
        selectedSeriesDict = {}
        for i in range(subjectCount):
            subject = root.child(i)
            studyCount = subject.childCount()
            subjectID = subject.text(0).replace('Subject -', '').strip()
            selectedSeriesDict[subjectID] = defaultdict(list)
            for j in range(studyCount):
                study = subject.child(j)
                seriesCount = study.childCount()
                studyID = study.text(0).replace('Study -', '').strip()
                selectedSeriesDict[subjectID][studyID] = []
                for n in range(seriesCount):
                    series = study.child(n)
                    if series.checkState(0) == Qt.Checked:
                        selectedSeriesDict[subjectID][studyID].append(series.text(0).replace('Series -', '').strip())

        return selectedSeriesDict
    except Exception as e:
        print('Error in TreeView.returnSelectedSeries: ' + str(e))
        logger.error('Error in TreeView.returnSelectedSeries: ' + str(e))
    

def returnSelectedImages(self):
    """This function generates and returns a list of selected images."""
    logger.info("TreeView.returnSelectedImages called")
    try:
        root = self.treeView.invisibleRootItem()
        subjectCount = root.childCount()
        selectedImagesDict = {}
        for i in range(subjectCount):
            subject = root.child(i)
            studyCount = subject.childCount()
            subjectID = subject.text(0).replace('Subject -', '').strip()
            selectedImagesDict[subjectID] = defaultdict(list)
            for j in range(studyCount):
                study = subject.child(j)
                seriesCount = study.childCount()
                studyID = study.text(0).replace('Study -', '').strip()
                selectedImagesDict[subjectID][studyID] = defaultdict(list)
                for k in range(seriesCount):
                    series = study.child(k)
                    imageCount = series.childCount()
                    seriesID = series.text(0).replace('Series -', '').strip()
                    selectedImagesDict[subjectID][studyID][seriesID] = []
                    for n in range(imageCount):
                        image = series.child(n)
                        if image.checkState(0) == Qt.Checked:
                            selectedImagesDict[subjectID][studyID][seriesID].append(image.text(3))

        return selectedImagesDict
    except Exception as e:
        print('Error in TreeView.returnSelectedImages: ' + str(e))
        logger.error('Error in TreeView.returnSelectedImages: ' + str(e))


def getPathParentNode(self, inputPath):
    """This function returns a list of subjectID, studyID an seriesID based on the given filepath."""
    logger.info("TreeView.getPathParentNode called")
    try:
        root = self.treeView.invisibleRootItem()
        subjectCount = root.childCount()
        for i in range(subjectCount):
            subject = root.child(i)
            studyCount = subject.childCount()
            for j in range(studyCount):
                study = subject.child(j)
                seriesCount = study.childCount()
                for k in range(seriesCount):
                    series = study.child(k)
                    imageCount = series.childCount()
                    for n in range(imageCount):
                        image = series.child(n)
                        if image.text(3) == inputPath:
                            subjectID = subject.text(0).replace('Subject -', '').strip()
                            studyID = study.text(0).replace('Study -', '').strip()
                            seriesID = series.text(0).replace('Series -', '').strip()
                            return subjectID, studyID, seriesID

    except Exception as e:
        print('Error in TreeView.getPathParentNode: ' + str(e))
        logger.error('Error in TreeView.getPathParentNode: ' + str(e))