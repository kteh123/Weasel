from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QApplication, QAbstractItemView,
                             QMdiSubWindow, QMenu, QAction, QHeaderView, QDockWidget,
                            QLabel, QProgressBar, QTreeWidget, QTreeWidgetItem)
import os
import sys
import logging
import CoreModules.WEASEL.DisplayImageColour  as displayImageColour

logger = logging.getLogger(__name__)
__author__ = "Steve Shillitoe"


class TreeView():
    """Uses an XML file that describes a DICOM file structure to build a
    tree view showing a visual representation of that file structure."""
    def __init__(self, weasel, XML_File_Path):
        try:
            logger.info("TreeView init called")
            if os.path.exists(XML_File_Path):
                QApplication.setOverrideCursor(Qt.WaitCursor)
                self.weasel = weasel
                self.DICOM_XML_FilePath = XML_File_Path
                self.DICOMfolderPath, _ = os.path.split(XML_File_Path)
                self.weasel.objXMLReader.parseXMLFile(XML_File_Path)
                self.treeViewColumnWidths = { 1: 0, 2: 0, 3: 0} 

                self.widget = QTreeWidget()
                self.widget.setMinimumSize(300,500)
                self.widget.setAutoScroll(False)
                self.widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
                self.widget.setUniformRowHeights(True)
                self.widget.setColumnCount(4)
                self.widget.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
                self.widget.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
                self.widget.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
                self.widget.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
                self.widget.setHeaderLabels(["", "DICOM Files", "Date", "Time", "Path"])
                self.widget.setContextMenuPolicy(Qt.CustomContextMenu)
                self.widget.itemDoubleClicked.connect(lambda item, col: displayImageColour.displayImageFromTreeView(self.weasel, item, col))
                self.widget.customContextMenuRequested.connect(lambda pos: self.displayContextMenu(pos))
                self.widget.itemClicked.connect(lambda item, col: self.itemClickedEvent(item, col))

                self.buildTreeView()
                self.resizeTreeViewColumns()

                if self.weasel.cmd == False:
                    #Display tree view in left-hand side docked widget
                    #If such a widget already exists remove it to allow
                    #a new tree view to be displayed
                    dockwidget = self.weasel.findChild(QDockWidget)
                    if dockwidget:
                        self.weasel.removeDockWidget(dockwidget)

                    dockwidget =  QDockWidget("DICOM Study Structure", self.weasel, Qt.SubWindow)
                    dockwidget.setAllowedAreas(Qt.LeftDockWidgetArea)
                    dockwidget.setFeatures(QDockWidget.NoDockWidgetFeatures)
                    self.weasel.addDockWidget(Qt.LeftDockWidgetArea, dockwidget)
                    dockwidget.setWidget(self.widget)
                    self.widget.show()

                QApplication.restoreOverrideCursor()
        except Exception as e:
            QApplication.restoreOverrideCursor()
            exception_type, exception_object, exception_traceback = sys.exc_info()
            #filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            print('Error in TreeView.makeDICOMStudiesTreeView at line {}: '.format(line_number) + str(e)) 
            logger.exception('Error in TreeView.makeDICOMStudiesTreeView at line {}: '.format(line_number) + str(e)) 


    def buildTreeView(self):
        try:
            logger.info("TreeView.buildTreeView called")
            self.widget.clear()
            self.widget.blockSignals(True)
            for subjectElement in self.weasel.objXMLReader.getSubjects():
                subjectWidgetTreeBranch = self.createWidgetTreeBranch("Subject",  subjectElement,  self.widget)
                for studyElement in subjectElement:
                    studyWidgetTreeBranch = self.createWidgetTreeBranch("Study",  studyElement, subjectWidgetTreeBranch)
                    for seriesElement in studyElement:
                        seriesWidgetTreeBranch = self.createWidgetTreeBranch("Series", seriesElement,  studyWidgetTreeBranch)
                        for imageElement in seriesElement:
                            self.createImageLeaf(imageElement, seriesWidgetTreeBranch)
            self.expand()
            self.widget.blockSignals(False)   
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            #filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            print('Error in TreeView.buildTreeView at line {}: '.format(line_number) + str(e)) 
            logger.exception('Error in TreeView.buildTreeView at line {}: '.format(line_number) + str(e)) 


    def createWidgetTreeBranch(self, branchName, elementTreeBranch, widgetTreeParent):
        try:
            elementTreeBranchID = elementTreeBranch.attrib['id']
            logger.info("TreeView.createWidgetTreeBranch, branch ID={}".format(elementTreeBranchID))
            item = QTreeWidgetItem(widgetTreeParent)
            item.element = elementTreeBranch
            item.setText(0, '')
            item.setText(1, branchName + " - {}".format(elementTreeBranchID))
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)

            if elementTreeBranch.attrib['checked'] == "True":
                item.setCheckState(0, Qt.Checked)
            else:
                item.setCheckState(0, Qt.Unchecked)

            return item
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            #filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            print('Error in TreeView.createWidgetTreeBranch at line {} when branch ID={}: '.format(line_number, branchName) + str(e)) 
            logger.exception('Error in TreeView.createWidgetTreeBranch at line {}: '.format(line_number) + str(e)) 


    def createImageLeaf(self, imageElement, parent):
        try:
            #Extract filename from file path
            if imageElement:
                if imageElement.find('label') is None:
                    imageLabel = os.path.basename(imageElement.find('name').text)
                else:
                    imageLabel = imageElement.find('label').text
                imageDate = imageElement.find('date').text
                imageTime = imageElement.find('time').text
                imagePath = imageElement.find('name').text
                item = QTreeWidgetItem(parent)
                item.element = imageElement
                item.setToolTip(0, "At least one image must be checked to view an image(s)")
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                #put a checkbox in front of each image
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setText(0, '')
                item.setText(1, ' Image - ' + imageLabel)
                item.setText(2, imageDate)
                item.setText(3, imageTime)
                item.setText(4, imagePath)

                if imageElement.attrib['checked'] == "True":
                    item.setCheckState(0, Qt.Checked)
                else:
                    item.setCheckState(0, Qt.Unchecked)
                return item
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            #filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            print('Error in TreeView.createImageLeaf at line {}: '.format(line_number) + str(e)) 
            logger.exception('Error in TreeView.createImageLeaf at line {}: '.format(line_number) + str(e)) 


    def resizeTreeViewColumns(self):
        try:
            self.widget.resizeColumnToContents(0)
            self.widget.resizeColumnToContents(1)
            self.widget.resizeColumnToContents(2)
            self.widget.hideColumn(4)
            self.treeViewColumnWidths[1] = self.widget.columnWidth(1)
            self.treeViewColumnWidths[2] = self.widget.columnWidth(2)
            self.treeViewColumnWidths[3] = self.widget.columnWidth(3)
        except Exception as e:
                print('Error in TreeView.resizeTreeViewColumns: ' + str(e))
                logger.exception('Error in TreeView.resizeTreeViewColumns: ' + str(e))


    def setEvents(self):
        #connect functions to events
        #To Do replace the following function with a call to ImagerViewer class
        self.widget.itemDoubleClicked.connect(lambda item, col: displayImageColour.displayImageFromTreeView(self.weasel, item, col))
        self.widget.customContextMenuRequested.connect(lambda pos: self.displayContextMenu(pos))
        #check/uncheck child items below current checked/unchecked item
        #check/uncheck item when the item label is selected
        self.widget.itemClicked.connect(lambda item, col: toggleItemCheckedState(item, col))
        self.widget.itemChanged.connect(lambda item: checkChildItems(item))
        #check/uncheck parent items above current checked/unchecked item
        self.widget.itemChanged.connect(lambda item: checkParentItems(item))
        #check/uncheck items when a block of items is selected/unselected
        self.widget.itemSelectionChanged.connect(lambda: self.toggleBlockSelectionCheckedState())
        #build lists of checked items on the fly
        self.widget.itemClicked.connect(lambda: self.buildListsCheckedItems())
        #use lists of checked items to decide which menu items to enable
        self.widget.itemClicked.connect(lambda: self.toggleMenuItems())
        self.widget.itemCollapsed.connect(lambda item: self.saveTreeViewExpandedState(item, "False"))
        self.widget.itemExpanded.connect(lambda item: self.saveTreeViewExpandedState(item, "True"))
     
        

    def displayContextMenu(self, pos):
        try:
            logger.info("TreeView.displayContextMenu called")
            if self.isASeriesChecked or self.isAnImageChecked:
                self.weasel.menuBuilder.context.exec_(self.widget.mapToGlobal(pos))
        except Exception as e:
            print('Error in function TreeView.displayContextMenu: ' + str(e))


    def itemClickedEvent(self, item, col):
        """When a tree view item is selected, it is also checked
        and when a tree view item is checked, it is also selected.
        This function also sets boolean flags that indicate if a 
        subject, study, series or image is checked.
        """
        try:
            logger.info("TreeView.itemClickedEvent called.")
            if col == 0:
                self.saveCheckedState(item)
                self.checkChildItems(item)
                self.checkParentItems(item) 
            else:              
                selectedItems = self.widget.selectedItems()
                if selectedItems:
                    if len(selectedItems) == 1:
                        if item.checkState(0) == Qt.Checked:
                            item.setCheckState(0, Qt.Unchecked) 
                        else:
                            item.setCheckState(0, Qt.Checked) 
                        self.saveCheckedState(item)
                        self.checkChildItems(item)
                        self.checkParentItems(item)
                    else:
                        for i, item in enumerate(selectedItems):
                            if i == 0:
                                checked = item.checkState(0) == Qt.Checked
                            else:
                                if checked:
                                    item.setCheckState(0, Qt.Checked)
                                else:
                                    item.setCheckState(0, Qt.Unchecked) 
                                self.saveCheckedState(item)  
                                self.checkChildItems(item)
                                self.checkParentItems(item)              
            self.weasel.refresh_menus()
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            print('Error in itemClickedEvent at line number {} when {}: '.format(line_number, e))
            logger.exception('Error in itemClickedEvent: ' + str(e))


    def refreshDICOMStudiesTreeView(self):
        """Refreshed the Tree View and saves the checked state."""
        try:
            logger.info("TreeView.refreshDICOMStudiesTreeView called.")
            QApplication.setOverrideCursor(Qt.WaitCursor)
    
            self.treeViewColumnWidths[1] = self.widget.columnWidth(1)
            self.treeViewColumnWidths[2] = self.widget.columnWidth(2)
            self.treeViewColumnWidths[3] = self.widget.columnWidth(3)
            self.widget.hide()
            self.buildTreeView()
            self.widget.setColumnWidth(1, self.treeViewColumnWidths[1])
            self.widget.setColumnWidth(2, self.treeViewColumnWidths[2])  
            self.widget.setColumnWidth(3, self.treeViewColumnWidths[3])

            self.weasel.refresh_menus()
            self.widget.show()

            self.weasel.objXMLReader.saveXMLFile()
            
            QApplication.restoreOverrideCursor()
        except Exception as e:
            QApplication.restoreOverrideCursor()
            print('Error in TreeView.refreshDICOMStudiesTreeView: ' + str(e))
            logger.exception('Error in TreeView.refreshDICOMStudiesTreeView: ' + str(e))


    def closeTreeView(self):
        try:
            self.widget.clear()
            self.widget.close()
        except Exception as e:
            print('Error in TreeView.CloseTreeView: ' + str(e))
            logger.exception('Error in TreeView.CloseTreeView: ' + str(e))


    def callUnCheckTreeViewItems(self):
        logger.info("TreeView.callUnCheckTreeViewItems called")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        root = self.widget.invisibleRootItem()
        self.unCheckTreeViewItems(root)
        QApplication.restoreOverrideCursor()


    def unCheckTreeViewItems(self, item):
        """This function uses recursion to set the state of child checkboxes 
        of item to unchecked.
        
        Input Parameters
        ****************
        item  - A QTreeWidgetItem 
        """
        logger.info("TreeView.unCheckTreeViewItems called")
        try:
            if item.childCount() > 0:
                itemCount = item.childCount()
                for n in range(itemCount):
                    childItem = item.child(n)
                    item.treeWidget().blockSignals(True)
                    childItem.setCheckState(0, Qt.Unchecked)
                    self.saveCheckedState(childItem)
                    item.treeWidget().blockSignals(False)
                    self.unCheckTreeViewItems(childItem)
        except Exception as e:
            print('Error in TreeView.unCheckTreeViewItems: ' + str(e))
            logger.exception('Error in TreeView.unCheckTreeViewItems: ' + str(e))


    def expand(self):
        """Resets the expanded state to default.
        
        The default state is chosen so that all checked items are exposed.
        Specifically, a node is expanded as soon as one of its children is expanded
        and a series is expanded as soon as a single image is checked
        """
        logger.info("TreeView.setExpanded called")
        try:
            root = self.widget.invisibleRootItem()
            for i in range(root.childCount()):
                subject = root.child(i)
                subjectExpand = False
                for j in range(subject.childCount()):
                    study = subject.child(j) 
                    studyExpand = False
                    for k in range(study.childCount()):
                        series = study.child(k)
                        seriesExpand = False
                        for n in range(series.childCount()):
                            image = series.child(n)
                            imageChecked = image.checkState(0) == Qt.Checked
                            seriesExpand = seriesExpand or imageChecked
                        series.setExpanded(seriesExpand)
                        studyExpand = studyExpand or seriesExpand
                    study.setExpanded(studyExpand)
                    subjectExpand = subjectExpand or studyExpand
                subject.setExpanded(subjectExpand)    

        except Exception as e:
            print('Error in TreeView.setExpanded: ' + str(e))
            logger.exception('Error in TreeView.setExpanded: ' + str(e))


    def saveCheckedState(self, item):
        try:
            logger.info("TreeView.saveCheckedState called.")
            if item.checkState(0) == Qt.Checked:
                checkedState = 'True' 
            else:
                checkedState = 'False'
            item.element.set('checked', checkedState)
        except Exception as e:
                print('Error in TreeView.saveCheckedState: ' + str(e))
                logger.exception('Error in TreeView.saveCheckedState: ' + str(e))


    def checkChildItems(self, item):
        """This function uses recursion to set the state of child checkboxes to
        match that of their parent.
        
        Input Parameters
        ****************
        item  - A QTreeWidgetItem whose checkbox state has just changed
        """
        logger.info("TreeView.checkChildItems called")
        #print("TreeView.checkChildItems called")
        try:
            if item.childCount() > 0:
                itemCount = item.childCount()
                for n in range(itemCount):
                    childItem = item.child(n)
                    #Give child checkboxes the same state as their 
                    #parent checkbox
                    item.treeWidget().blockSignals(True)
                    childItem.setCheckState(0, item.checkState(0))
                    self.saveCheckedState(childItem)
                    item.treeWidget().blockSignals(False)
                    self.checkChildItems(childItem)
        except Exception as e:
            print('Error in TreeView.checkChildItems: ' + str(e))
            logger.exception('Error in TreeView.checkChildItems: ' + str(e))


    def checkParentItems(self, item):
        """This function uses recursion to set the state of Parent checkboxes to
        match collective state of their children.
        
        Input Parameters
        ****************
        item  - A QTreeWidgetItem whose checkbox state has just changed
        """
        logger.info("TreeView.checkParentItems called")
        try:
            parentItem = item.parent()
            if parentItem:
                item.treeWidget().blockSignals(True)
                if areAllChildrenChecked(parentItem):
                    parentItem.setCheckState(0, Qt.Checked)
                else:
                    parentItem.setCheckState(0, Qt.Unchecked)
                self.saveCheckedState(parentItem)
                item.treeWidget().blockSignals(False)
                self.checkParentItems(parentItem)
        except Exception as e:
                print('Error in TreeView.checkParentItems: ' + str(e))
                logger.exception('Error in TreeView.checkParentItems: ' + str(e))


    def buildListsCheckedItems(self):
        """This function generates and returns lists of checked items."""
        logger.info("TreeView.buildListsCheckedItems called")
        try:
            checkedImageList = []
            checkedSeriesList = []
            checkedStudyList = []
            checkedSubjectList = []
            root = self.widget.invisibleRootItem()
            subjectCount = root.childCount()
            for i in range(subjectCount):
                subject = root.child(i)
                if subject.checkState(0) == Qt.Checked:
                    checkedSubjectList.append(subject.text(1).replace("Subject - ", "").strip())
                studyCount = subject.childCount()
                for j in range(studyCount):
                    study = subject.child(j)
                    if study.checkState(0) == Qt.Checked:
                        subject = study.parent()
                        checkedSubjectData = []
                        checkedSubjectData.append(subject.text(1).replace("Subject - ", "").strip())
                        checkedSubjectData.append(study.text(1).replace("Study - ", "").strip())
                        checkedStudyList.append(checkedSubjectData)
                    seriesCount = study.childCount()
                    for k in range(seriesCount):
                        series = study.child(k)
                        if series.checkState(0) == Qt.Checked:
                            study = series.parent()
                            subject = study.parent() 
                            checkedSeriesData = []
                            checkedSeriesData.append(subject.text(1).replace("Subject - ", "").strip())
                            checkedSeriesData.append(study.text(1).replace("Study - ", "").strip())
                            checkedSeriesData.append(series.text(1).replace("Series - ", "").strip())
                            checkedSeriesList.append(checkedSeriesData)
                        imageCount = series.childCount()
                        for n in range(imageCount):
                            image = series.child(n)
                            if image.checkState(0) == Qt.Checked:
                                series = image.parent()
                                study = series.parent()
                                subject = study.parent()
                                checkedImagesData = []
                                checkedImagesData.append(subject.text(1).replace("Subject - ", "").strip())
                                checkedImagesData.append(study.text(1).replace("Study - ", "").strip())
                                checkedImagesData.append(series.text(1).replace("Series - ", "").strip())
                                checkedImagesData.append(image.text(4))
                                checkedImageList.append(checkedImagesData)
            return checkedImageList, checkedSeriesList, checkedStudyList, checkedSubjectList
        except Exception as e:
            print('Error in TreeView.buildListsCheckedItems: ' + str(e))
            logger.exception('Error in TreeView.buildListsCheckedItems: ' + str(e))


    @property
    def checkedImageList(self):
        images, _, _, _ = self.buildListsCheckedItems()
        return images

    @property
    def checkedSeriesList(self):
        _, series, _, _ = self.buildListsCheckedItems()
        return series

    @property
    def checkedStudyList(self):
        _, _, studies, _ = self.buildListsCheckedItems()
        return studies

    @property
    def checkedSubjectList(self):
        _, _, _, subjects = self.buildListsCheckedItems()
        return subjects

    @property
    def isAnImageChecked(self): 
        return self.checkedImageList != []

    @property
    def isASeriesChecked(self): 
        return self.checkedSeriesList != []
     
    @property
    def isAStudyChecked(self): #remove from API TreeViewState
        return self.checkedStudyList != []

    @property
    def isASubjectChecked(self): 
        return self.checkedSubjectList != []

    def isAnItemChecked(self):
        """Returns True is an item is selected in the DICOM
        tree view, else returns False"""
        return (self.checkedImageList != []) or (self.checkedSeriesList != [])


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
        for n in range(childCount):
            if item.child(n).checkState(0) == Qt.Unchecked:
                return False
        return True
    except Exception as e:
            print('Error in TreeView.areAllChildrenChecked: ' + str(e))
            logger.exception('Error in TreeView.areAllChildrenChecked: ' + str(e))
