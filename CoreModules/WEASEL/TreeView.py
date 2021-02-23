from PyQt5 import QtCore 
from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QApplication, QAbstractItemView,
                             QMdiSubWindow, QMenu, QAction, QDockWidget,
                            QLabel, QProgressBar, QTreeWidget, QTreeWidgetItem)
import os
import sys
import logging
import time
from collections import defaultdict
import CoreModules.WEASEL.Menus as menus
import Pipelines.ViewImage as viewImage
logger = logging.getLogger(__name__)


def createTreeBranch(self, branchName, branch, parent):
    try:
        branchID = branch.attrib['id']
        thisBranch = QTreeWidgetItem(parent)
        thisBranch.setText(0, branchName + " - {}".format(branchID))
        thisBranch.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        #put a checkbox in front of this branch
        thisBranch.setFlags(thisBranch.flags() | Qt.ItemIsUserCheckable)
        thisBranch.setCheckState(0, Qt.Unchecked)
        thisBranch.setExpanded(True)
        return thisBranch# treeWidgetItemCounter
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        #filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print('Error in TreeView.createTreeBranch at line {}: '.format(line_number) + str(e)) 
        logger.error('Error in TreeView.createTreeBranch at line {}: '.format(line_number) + str(e)) 


def createImageLeaf(self, image, seriesBranch):
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
            imageLeaf.setToolTip(0, "At least one image must be checked to view an image(s)")
            imageLeaf.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            #put a checkbox in front of each image
            imageLeaf.setFlags(imageLeaf.flags() | Qt.ItemIsUserCheckable)
            imageLeaf.setCheckState(0, Qt.Unchecked)
            imageLeaf.setText(0, ' Image - ' + imageName)
            imageLeaf.setText(1, imageDate)
            imageLeaf.setText(2, imageTime)
            imageLeaf.setText(3, imagePath)
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


def buildTreeView(self):
    try:
        self.treeView.clear()
        #treeWidgetItemCounter = 0 
        subjects = self.objXMLReader.getSubjects()
        for subject in subjects:
            subjectBranch = createTreeBranch(self, "Subject",  subject,  self.treeView)
        
            for study in subject:
                studyBranch = createTreeBranch(self, "Study",  study, subjectBranch)
                                                             
                for series in study:
                    seriesBranch = createTreeBranch(self, "Series", series,  studyBranch)
    
                    for image in series:
                        createImageLeaf(self, image, seriesBranch)
             
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
                self.DICOM_XML_FilePath = XML_File_Path
                self.DICOMfolderPath, _ = os.path.split(XML_File_Path)
                self.objXMLReader.parseXMLFile(self.DICOM_XML_FilePath)
               
                self.treeView = QTreeWidget()
                
                #Minimum width of the tree view has to be set
                #to 700 to ensure its parent, the docking widget 
                #initially displays wide enough to show the tree view
                self.treeView.setMinimumSize(700,500)
                
                #Enable multiple selection using up arrow and Ctrl keys
                self.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
                self.treeView.setUniformRowHeights(True)
                self.treeView.setColumnCount(4)
                self.treeView.setHeaderLabels(["DICOM Files", "Date", "Time", "Path"])
                self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)

                buildTreeView(self)

                self.treeView.customContextMenuRequested.connect(lambda pos: menus.displayContextMenu(self, pos))
                self.treeView.itemChanged.connect(lambda item: checkChildItems(item))
                self.treeView.itemClicked.connect(lambda item: checkParentItems(item))
                self.treeView.itemClicked.connect(lambda item, col: toggleItemCheckedState(self, item, col))
                self.treeView.itemClicked.connect(lambda: toggleMenuItems(self))
                self.treeView.itemClicked.connect(lambda: returnCheckedImages(self))
                #self.treeView.itemClicked.connect(lambda item: print(item.text(0)))#1
                #self.treeView.itemSelectionChanged.connect(lambda: print("itemSelectionChanged"))
                self.treeView.itemDoubleClicked.connect(lambda: viewImage.main(self))
                self.treeView.itemClicked.connect(lambda item: onTreeViewItemClicked(self, item))
                
                resizeTreeViewColumns(self)
                collapseSeriesBranches(self.treeView.invisibleRootItem())
                

                #Display tree view in left-hand side docked widget
                #If such a widget already exists remove it to allow
                #a new tree view to be displayed
                dockwidget = self.findChild(QDockWidget)
                if dockwidget:
                    self.removeDockWidget(dockwidget)
                    
                dockwidget =  QDockWidget("DICOM Study Structure", self, Qt.SubWindow)
                dockwidget.setAllowedAreas(Qt.LeftDockWidgetArea)
                dockwidget.setFeatures(QDockWidget.NoDockWidgetFeatures)
                self.addDockWidget(Qt.LeftDockWidgetArea, dockwidget)
                dockwidget.setWidget(self.treeView)
                self.treeView.show()
                
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
            self.objXMLReader.parseXMLFile(self.DICOM_XML_FilePath)

            # Joao Sousa suggestion
            self.treeView.hide()
            buildTreeView(self)
            resizeTreeViewColumns(self)

            #If no tree view items are now selected,
            #disable items in the Tools menu.
            toggleMenuItems(self)
            collapseSeriesBranches(self.treeView.invisibleRootItem())
            collapseStudiesBranches(self.treeView.invisibleRootItem())
            # Joao Sousa suggestion
            self.treeView.show()

            #Now collapse all series branches so as to hide the images
            #except the new series branch that has been created

            # Joao commented on the 16/10/2020
            expandTreeViewBranch(self.treeView.invisibleRootItem(), newSeriesName=newSeriesName)
        except Exception as e:
            print('Error in TreeView.refreshDICOMStudiesTreeView: ' + str(e))
            logger.error('Error in TreeView.refreshDICOMStudiesTreeView: ' + str(e))


def collapseStudiesBranches(item):
    """This function uses recursion to colapse all series branches
    
    Input Parameters
    ****************
    item  - A QTreeWidgetItem 
    """
    logger.info("TreeView.collapseStudiesBranches called")
    try:
        if item.childCount() > 0:
            itemCount = item.childCount()
            for n in range(itemCount):
                childItem = item.child(n)
                if 'study' in childItem.text(0).lower():
                    item.treeWidget().blockSignals(True)
                    childItem.setExpanded(False)
                    item.treeWidget().blockSignals(False)
                else:
                    collapseStudiesBranches(childItem)
    except Exception as e:
            print('Error in TreeView.collapseStudiesBranches: ' + str(e))
            logger.error('Error in TreeView.collapseStudiesBranches: ' + str(e))


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
                    if 'study' in branchText:
                        childItem.setExpanded(True)
                    if 'series' in branchText:
                        seriesName = branchText.replace('series -', '').strip()
                        item.treeWidget().blockSignals(True)
                        if seriesName == newSeriesName.lower():
                            item.setExpanded(True)
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
        logger.info("TreeView isAnItemSelected called.")
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
            logger.info("TreeView isAnImageSelected called.")
            if self.treeView.currentItem():
                selectedItem = self.treeView.currentItem()
                if selectedItem:
                    if 'image' in selectedItem.text(0).lower():
                        return True
                    else:
                        return False
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
            logger.info("TreeView isASeriesSelected called.")
            if self.treeView.currentItem():
                selectedItem = self.treeView.currentItem()
                if selectedItem:
                    if 'series' in selectedItem.text(0).lower():
                        return True
                    else:
                        return False
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
            logger.info("TreeView isAStudySelected called.")
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
           

def toggleItemCheckedState(self, item, col):
        """When a tree view item is selected, it is also checked"""
        try:
            logger.info("TreeView.toggleItemCheckedState called.")
            
            #print("Check state={} selected]{}".format(item.checkState(0),item.isSelected() ))
            #if item.isSelected():
            #    if item.checkState(0)  == Qt.Checked:
            #        item.setCheckState(0, Qt.Unchecked)
            #    elif item.checkState(0)  == Qt.Unchecked:
            #        item.setCheckState(0, Qt.Checked)
            #else: #Item not selected
            #    if item.checkState(0)  == Qt.Checked:
            #        item.setSelected(True)
            #    elif item.checkState(0)  == Qt.Unchecked:
            #        item.setSelected(False)
            
            #When a user uses the arrow key to make a multiple selection
            #this loop checks all the attached checkboxes
            if self.treeView.selectedItems():
                if len(self.treeView.selectedItems()) > 1:
                    for selectedItem in self.treeView.selectedItems():
                        selectedItem.setSelected(True)
                        selectedItem.setCheckState(0, Qt.Checked)

            #if len(self.treeView.selectedItems()) == 1:
            #    selectedItem = self.treeView.currentItem()
            #    if selectedItem.checkState(0)  == Qt.Checked:
            #        selectedItem.setCheckState(0, Qt.Unchecked) 
            #    else:
            #        selectedItem.setCheckState(0, Qt.Checked)
            #else:
            #    for selectedItem in self.treeView.selectedItems():
            #        selectedItem.setCheckState(0, Qt.Checked)
                     
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            print('Error in toggleItemCheckedState at line number {} when {}: '.format(line_number, e))
            logger.error('Error in toggleItemCheckedState: ' + str(e))


def isASubjectSelected(self):
        """Returns True is a subject is selected in the DICOM
        tree view, else returns False"""
        try:
            logger.info("TreeView isASubjectSelected called.")
            selectedItem = self.treeView.currentItem()
            if selectedItem:
                if 'subject' in selectedItem.text(0).lower():
                    return True
                else:
                    return False
            else:
               return False
        except Exception as e:
            print('Error in isASubjectSelected: ' + str(e))
            logger.error('Error in isASubjectSelected: ' + str(e))


def toggleMenuItems(self):
        """TO DO"""
        try:
            logger.info("TreeView.toggleMenuItems called.")
            for menu in self.listMenus:
                menuItems = menu.actions()
                for menuItem in menuItems:
                    if not menuItem.isSeparator():
                        if not(menuItem.data() is None):
                            #Assume not all tools will act on an image
                            #Assume all tools act on a series  
                            if isASubjectSelected(self) or isAStudySelected(self):
                                #None of the menu tools operate on 
                                #studies or subjects at present
                                menuItem.setEnabled(False)    
                            elif isASeriesSelected(self):
                                 menuItem.setEnabled(True)
                            elif isAnImageSelected(self):
                                if menuItem.data():
                                    menuItem.setEnabled(True)
                                else:
                                    menuItem.setEnabled(False) 
        except Exception as e:
            print('Error in TreeView.toggleMenuItems: ' + str(e))
            logger.error('Error in TreeView.toggleMenuItems: ' + str(e))


def onTreeViewItemClicked(self, item):
    """When a DICOM study treeview item is clicked, this function
    populates the relevant class variables that store the following
    DICOM image data: study ID, Series ID, Image name, image file path"""
    logger.info("TreeView.onTreeViewItemClicked called")
    try:
        #test for returning dictionary of studyIDs:seriesIDs
        #print(returnCheckedSeries(self))
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


def returnSelectedStudies(self):
    """This function generates and returns a list of selected studies."""
    logger.info("TreeView.returnSelectedStudies called")
    try:
        root = self.treeView.invisibleRootItem()
        subjectCount = root.childCount()
        selectedStudiesList = []
        for i in range(subjectCount):
            subject = root.child(i)
            subjectFlag = True if subject.isSelected() == True else False
            studyCount = subject.childCount()
            for j in range(studyCount):
                study = subject.child(j)
                if (study.isSelected() == True or subjectFlag == True):
                    selectedStudiesList.append(study)
        return selectedStudiesList
    except Exception as e:
        print('Error in TreeView.returnSelectedStudies: ' + str(e))
        logger.error('Error in TreeView.returnSelectedStudies: ' + str(e))


def returnSelectedSeries(self):
    """This function generates and returns a list of selected series."""
    logger.info("TreeView.returnSelectedSeries called")
    try:
        root = self.treeView.invisibleRootItem()
        subjectCount = root.childCount()
        selectedSeriesList = []
        for i in range(subjectCount):
            subject = root.child(i)
            subjectFlag = True if subject.isSelected() == True else False
            studyCount = subject.childCount()
            for j in range(studyCount):
                study = subject.child(j)
                studyFlag = True if (study.isSelected() == True or subjectFlag == True) else False
                seriesCount = study.childCount()
                for n in range(seriesCount):
                    series = study.child(n)
                    if (series.isSelected() == True or studyFlag == True):
                        selectedSeriesList.append(series)
        return selectedSeriesList
    except Exception as e:
        print('Error in TreeView.returnSelectedSeries: ' + str(e))
        logger.error('Error in TreeView.returnSelectedSeries: ' + str(e))


def returnSelectedImages(self):
    """This function generates and returns a list of selected images."""
    logger.info("TreeView.returnSelectedImages called")
    try:
        root = self.treeView.invisibleRootItem()
        subjectCount = root.childCount()
        selectedImages = []
        for i in range(subjectCount):
            subject = root.child(i)
            subjectFlag = True if subject.isSelected() == True else False
            studyCount = subject.childCount()
            for j in range(studyCount):
                study = subject.child(j)
                studyFlag = True if (study.isSelected() == True or subjectFlag == True) else False
                seriesCount = study.childCount()
                for k in range(seriesCount):
                    series = study.child(k)
                    seriesFlag = True if (series.isSelected() == True or studyFlag == True) else False
                    imageCount = series.childCount()
                    for n in range(imageCount):
                        image = series.child(n)
                        if (image.isSelected() == True or seriesFlag == True):
                            selectedImages.append(image)
        return selectedImages
    except Exception as e:
        print('Error in TreeView.returnSelectedSeries: ' + str(e))
        logger.error('Error in TreeView.returnSelectedSeries: ' + str(e))


def returnCheckedStudies(self):
    """This function generates and returns a list of checked series."""
    logger.info("TreeView.returnCheckedStudies called")
    try:
        root = self.treeView.invisibleRootItem()
        subjectCount = root.childCount()
        checkedStudiesList = []
        for i in range(subjectCount):
            subject = root.child(i)
            studyCount = subject.childCount()
            for j in range(studyCount):
                study = subject.child(j)   
                if study.checkState(0) == Qt.Checked:
                    checkedStudiesList.append(study)
        return checkedStudiesList
    except Exception as e:
        print('Error in TreeView.returnCheckedStudies: ' + str(e))
        logger.error('Error in TreeView.returnCheckedStudies: ' + str(e))


def returnCheckedSeries(self):
    """This function generates and returns a list of checked series."""
    logger.info("TreeView.returnCheckedSeries called")
    try:
        root = self.treeView.invisibleRootItem()
        subjectCount = root.childCount()
        checkedSeriesList = []
        for i in range(subjectCount):
            subject = root.child(i)
            studyCount = subject.childCount()
            for j in range(studyCount):
                study = subject.child(j)
                seriesCount = study.childCount()
                for n in range(seriesCount):
                    series = study.child(n)
                    if series.checkState(0) == Qt.Checked:
                        checkedSeriesList.append(series)
        return checkedSeriesList
    except Exception as e:
        print('Error in TreeView.returnCheckedSeries: ' + str(e))
        logger.error('Error in TreeView.returnCheckedSeries: ' + str(e))
    

def returnCheckedImages(self):
    """This function generates and returns a list of checked images."""
    logger.info("TreeView.returnCheckedImages called")
    try:
        self.checkedImageList = []
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
                        if image.checkState(0) == Qt.Checked:
                            checkedImagesData = []
                            series = image.parent()
                            study = series.parent()
                            checkedImagesData.append(study.text(0).lower().replace("study", "").replace("-","").strip())
                            checkedImagesData.append(series.text(0).lower().replace("series", "").replace("-","").strip())
                            checkedImagesData.append(image.text(3))
                            self.checkedImageList.append(checkedImagesData)
        
        #print("self.checkedImageList = {}".format(self.checkedImageList))
    except Exception as e:
        print('Error in TreeView.returnCheckedImages: ' + str(e))
        logger.error('Error in TreeView.returnCheckedImages: ' + str(e))


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
                            return (subjectID, studyID, seriesID)
    except Exception as e:
        print('Error in TreeView.getPathParentNode: ' + str(e))
        logger.error('Error in TreeView.getPathParentNode: ' + str(e))