"""
Class for building a tree view showing a visual representation of DICOM file structure.

It uses an XML file that describes a DICOM file structure to build a
tree view showing a visual representation of that file structure.
"""

from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QApplication, QAbstractItemView,
                             QMdiSubWindow, QMenu, QAction, QHeaderView, QDockWidget,
                            QLabel, QProgressBar, QTreeWidget, QTreeWidgetItem)
import os
import sys
import logging
from CoreModules.WeaselXMLReader import WeaselXMLReader
from Displays.ImageViewers.ImageViewer import ImageViewer as imageViewer
from DICOM.Classes import (Image, Series)


logger = logging.getLogger(__name__)
__author__ = "Steve Shillitoe"


class TreeView():
    """Class TreeView uses an XML file that describes a DICOM file structure to build a
    tree view showing a visual representation of that file structure."""

    def __init__(self, weasel, XML_File_Path):
            """
            Creates the tree view in a dock widget and populates it with DICOM data.

            Placing the tree view in a dock widget ensures that it is displayed on the
            left-hand side of the MDI.
            """
            logger.info("TreeView init called")
            if os.path.exists(XML_File_Path):
                QApplication.setOverrideCursor(Qt.WaitCursor)
                self.weasel = weasel
                self.weasel.objXMLReader = WeaselXMLReader(weasel, XML_File_Path)
                self.treeViewColumnWidths = { 1: 0, 2: 0, 3: 0} 

                self.treeViewWidget = QTreeWidget()
                self.treeViewWidget.setMinimumSize(300,500)
                self.treeViewWidget.setAutoScroll(False)
                self.treeViewWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
                self.treeViewWidget.setUniformRowHeights(True)
                self.treeViewWidget.setColumnCount(4)
                self.treeViewWidget.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
                self.treeViewWidget.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
                self.treeViewWidget.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
                self.treeViewWidget.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
                self.treeViewWidget.setHeaderLabels(["", "DICOM Files", "Date", "Time", "Path"])
                self.treeViewWidget.setContextMenuPolicy(Qt.CustomContextMenu)
                self.treeViewWidget.itemDoubleClicked.connect(lambda item, col: self._displayImage(item, col))
                self.treeViewWidget.customContextMenuRequested.connect(lambda pos: self._displayContextMenu(pos))
                self.treeViewWidget.itemClicked.connect(lambda item, col: self._itemClickedEvent(item, col))
                self.treeViewWidget.itemExpanded.connect(lambda: self.treeViewWidget.resizeColumnToContents(0))

                self._buildTreeView()

                self.treeViewWidget.resizeColumnToContents(0)
                self.treeViewWidget.resizeColumnToContents(1)
                self.treeViewWidget.resizeColumnToContents(2)
                self.treeViewWidget.hideColumn(4)
                self.treeViewColumnWidths[1] = self.treeViewWidget.columnWidth(1)
                self.treeViewColumnWidths[2] = self.treeViewWidget.columnWidth(2)
                self.treeViewColumnWidths[3] = self.treeViewWidget.columnWidth(3)

                self.treeViewWidget.header().setSectionResizeMode(0, QHeaderView.Interactive)
                self.treeViewWidget.header().setSectionResizeMode(1, QHeaderView.Interactive)
                self.treeViewWidget.header().setSectionResizeMode(2, QHeaderView.Interactive)
                self.treeViewWidget.header().setSectionResizeMode(3, QHeaderView.Interactive)

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
                    dockwidget.setWidget(self.treeViewWidget)
                    self.treeViewWidget.show()
                QApplication.restoreOverrideCursor()


    def _buildTreeView(self):
        """
        This function populates the tree view with DICOM data.

        Subject, study, series and image data are read from an
        XML file containing heirarchical DICOM data and used to 
        create the branches and leaves of the tree view. 

        Subject, study & series data are displayed as the branches
        of the tree view. 
        Image data is displayed as the leaves of the tree view.
        """
        logger.info("TreeView.buildTreeView called")
        self.treeViewWidget.clear()
        self.treeViewWidget.blockSignals(True)
        for subjectElement in self.weasel.objXMLReader.root:
            subjectTreeBranch = self._createTreeBranch("Subject",  subjectElement,  self.treeViewWidget)
            for studyElement in subjectElement:
                studyTreeBranch = self._createTreeBranch("Study",  studyElement, subjectTreeBranch)
                for seriesElement in studyElement:
                    seriesTreeBranch = self._createTreeBranch("Series", seriesElement,  studyTreeBranch)
                    for imageElement in seriesElement:
                        self._createImageLeaf(imageElement, seriesTreeBranch)
        self.expand()
        self.treeViewWidget.blockSignals(False)   


    def _createTreeBranch(self, branchName, elementTreeBranch, widgetTreeParent):
        """
        Creates a branch in the tree view. 
        
        A branch has a parent branch and one or more child branches or leaves.

        Input arguments
        ***************
        branchName - Name of the data type represented by the branch. 
                    Takes the value: Subject, Study or Series.

        elementTreeBranch - Element in the XML file, whose data will be
                    represented in this branch.


        widgetTreeParent - parent branch of the branch being created.
        """
        try:
            elementTreeBranchID = elementTreeBranch.attrib['id']
            logger.info("TreeView.createTreeBranch, branch ID={}".format(elementTreeBranchID))
            item = QTreeWidgetItem(widgetTreeParent)

            #Associate and store the element in the XML file with this branch
            item.element = elementTreeBranch

            item.setText(0, '')
            item.setText(1, branchName + " - {}".format(elementTreeBranchID))
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)

            #set the checked state of the branch according
            #to the state stored in the XML file
            if elementTreeBranch.attrib['checked'] == "True":
                item.setCheckState(0, Qt.Checked)
            else:
                item.setCheckState(0, Qt.Unchecked)

            return item
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            #filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            print('Error in TreeView.createTreeBranch at line {} when branch ID={}: '.format(line_number, branchName) + str(e)) 
            logger.exception('Error in TreeView.createTreeBranch at line {}: '.format(line_number) + str(e)) 


    def _createImageLeaf(self, imageElement, parent):
        """
        Creates a leaf element in the tree view, which represents an 
        individual image.

        Input arguments
        ***************
        imageElement - The XML element containing the data for an individual image
        parent - The tree view branch acting as the parent to the leaf element 
                 being created.  It will be branch representing a series.
        """
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

            #If this image has previously been checked, 
            #set its checked state to checked.
            if imageElement.attrib['checked'] == "True":
                item.setCheckState(0, Qt.Checked)
            else:
                item.setCheckState(0, Qt.Unchecked)
            return item 


    def _displayImage(self, item, col):
        """
        This function displays a series of DICOM images or an individual image 
        when it is double-clicked in the tree view.

        The image viewer is only displayed when an item in column 1 is 
        double-clicked.  To determine if an image or a series has been
        double-clicked, the XML element describing that item is retrieved
        and it's tag examined. A tag containing the string 'image' indicates
        an image has been double-clicked. Likewise, tag containing the 
        string 'series' indicates a series has been double-clicked.

         Input Parameters
        ****************
        item  - A QTreeWidgetItem representing a DICOM image or series that has
                been double-clicked
        col - The number of the column occupied by the double-clicked item.
        """
        if col == 1:
            id = self.weasel.objXMLReader.objectID(item.element)
            if item.element.tag == 'image':
                image = Image(self, id[0], id[1], id[2], id[3])
                imageViewer(self.weasel, image)
            elif item.element.tag == 'series':
                imageList = [image.find('name').text for image in item.element]
                series = Series(self, id[0], id[1], id[2], listPaths=imageList)
                imageViewer(self.weasel, series)


    def _displayContextMenu(self, pos):
        """
        Displays a context menu for the tree view when the right
        mouse button is pressed. 

        Input arguments
        ***************
        pos - mouse pointer position when the right mouse button is pressed.
            The context menu is displayed at this position. 
        """
        try:
            logger.info("TreeView.displayContextMenu called")
            #if (self.weasel.series() != []) or (self.weasel.images() != []):
            self.weasel.menuBuilder.context.exec_(self.treeViewWidget.mapToGlobal(pos))
        except Exception as e:
            print('Error in function TreeView.displayContextMenu: ' + str(e))


    def _itemClickedEvent(self, item, col):
        """When a tree view item is selected, it is also checked
        and when a tree view item is checked, it is also selected.
        This function also sets boolean flags that indicate if a 
        subject, study, series or image is checked.

         Input Parameters
        ****************
        item  - A QTreeWidgetItem whose checkbox state has just changed
        col - The number of the column occupied by the checked/selected item.
        """
        try:
            logger.info("TreeView.itemClickedEvent called.")
            if col == 0:
                self._saveCheckedState(item)
                self._checkChildItems(item)
                self._checkParentItems(item) 
            else:              
                selectedItems = self.treeViewWidget.selectedItems()
                if selectedItems:
                    if len(selectedItems) == 1:
                        if item.checkState(0) == Qt.Checked:
                            item.setCheckState(0, Qt.Unchecked) 
                        else:
                            item.setCheckState(0, Qt.Checked) 
                        self._saveCheckedState(item)
                        self._checkChildItems(item)
                        self._checkParentItems(item)
                    else:
                        for i, item in enumerate(selectedItems):
                            if i == 0:
                                checked = item.checkState(0) == Qt.Checked
                            else:
                                if checked:
                                    item.setCheckState(0, Qt.Checked)
                                else:
                                    item.setCheckState(0, Qt.Unchecked) 
                                self._saveCheckedState(item)  
                                self._checkChildItems(item)
                                self._checkParentItems(item)              
            self.weasel.refresh_menus()
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            print('Error in itemClickedEvent at line number {} when {}: '.format(line_number, e))
            logger.exception('Error in itemClickedEvent: ' + str(e))


    def refreshDICOMStudiesTreeView(self):
        """Refreshes the Tree View and saves the checked state."""
        try:
            logger.info("TreeView.refreshDICOMStudiesTreeView called.")
            QApplication.setOverrideCursor(Qt.WaitCursor)
    
            self.treeViewColumnWidths[1] = self.treeViewWidget.columnWidth(1)
            self.treeViewColumnWidths[2] = self.treeViewWidget.columnWidth(2)
            self.treeViewColumnWidths[3] = self.treeViewWidget.columnWidth(3)
            self.treeViewWidget.hide()
            self.weasel.objXMLReader.save()
            self._buildTreeView()
            self.treeViewWidget.setColumnWidth(1, self.treeViewColumnWidths[1])
            self.treeViewWidget.setColumnWidth(2, self.treeViewColumnWidths[2])  
            self.treeViewWidget.setColumnWidth(3, self.treeViewColumnWidths[3])
            self.weasel.refresh_menus()
            self.treeViewWidget.show()
            
            QApplication.restoreOverrideCursor()
        except Exception as e:
            QApplication.restoreOverrideCursor()
            print('Error in TreeView.refreshDICOMStudiesTreeView: ' + str(e))
            logger.exception('Error in TreeView.refreshDICOMStudiesTreeView: ' + str(e))


    def close(self):
        """
        This function closes the tree view & saves the XML file 
        containing the DICOM data displayed in the tree view.
        """
        try:
            self.weasel.objXMLReader.save()
            self.weasel.objXMLReader = None
            self.treeViewWidget.clear()
            self.treeViewWidget.close()
        except Exception as e:
            print('Error in TreeView.CloseTreeView: ' + str(e))
            logger.exception('Error in TreeView.CloseTreeView: ' + str(e))


    def callUnCheckTreeViewItems(self):
        """
        This function sets the checked state of all items in the
        tree view to unchecked.  It does this by calling the
        recursive function _unCheckTreeViewItems.
        """
        try:
            logger.info("TreeView.callUnCheckTreeViewItems called")
            QApplication.setOverrideCursor(Qt.WaitCursor)
            root = self.treeViewWidget.invisibleRootItem()
            self._unCheckTreeViewItems(root)
            QApplication.restoreOverrideCursor()
        except Exception as e:
            print('Error in TreeView.callUnCheckTreeViewItems: ' + str(e))
            logger.exception('Error in TreeView.callUnCheckTreeViewItems: ' + str(e))


    def _unCheckTreeViewItems(self, item):
        """Starting at the root of the tree view, 
        this function uses recursion to set the state of child checkboxes 
        of item to unchecked.  An item could represent a subject, study or series.
        
         Input Parameters
        ****************
        item  - A QTreeWidgetItem whose checkbox state has just changed
        """
        logger.info("TreeView._unCheckTreeViewItems called")
        try:
            if item.childCount() > 0:
                itemCount = item.childCount()
                for n in range(itemCount):
                    childItem = item.child(n)
                    item.treeWidget().blockSignals(True)
                    childItem.setCheckState(0, Qt.Unchecked)
                    self._saveCheckedState(childItem)
                    item.treeWidget().blockSignals(False)
                    self._unCheckTreeViewItems(childItem)
        except Exception as e:
            print('Error in TreeView._unCheckTreeViewItems: ' + str(e))
            logger.exception('Error in TreeView._unCheckTreeViewItems: ' + str(e))


    def expand(self):
        """Resets the expanded state to default.
        
        The default state is chosen so that all checked items are exposed.
        Specifically, a node is expanded as soon as one of its children is expanded
        and a series is expanded as soon as a single image is checked
        """
        logger.info("TreeView.setExpanded called")
        try:
            root = self.treeViewWidget.invisibleRootItem()
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


    def _saveCheckedState(self, item):
        """
        This function saves the checked state of a tree view item
        to the XML element associated with it. 

        The XML element contains data describing the tree view item.

         Input Parameters
        ****************
        item  - A QTreeWidgetItem whose checkbox state has just changed
        """
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


    def _checkChildItems(self, parentItem):
        """This function uses recursion to set the state of child checkboxes to
        match that of their parent.
        
        Input Parameters
        ****************
        parentItem  - A QTreeWidgetItem whose checkbox state has just changed
        """
        logger.info("TreeView.checkChildItems called")
        #print("TreeView.checkChildItems called")
        try:
            if parentItem.childCount() > 0:
                itemCount = parentItem.childCount()
                for n in range(itemCount):
                    childItem = parentItem.child(n)
                    parentItem.treeWidget().blockSignals(True)
                    childItem.setCheckState(0, parentItem.checkState(0))
                    self._saveCheckedState(childItem)
                    parentItem.treeWidget().blockSignals(False)
                    self._checkChildItems(childItem)
        except Exception as e:
            print('Error in TreeView.checkChildItems: ' + str(e))
            logger.exception('Error in TreeView.checkChildItems: ' + str(e))


    def _checkParentItems(self, childItem):
        """This function uses recursion to set the state of Parent checkboxes to
        match the collective state of their children.
        
        Input Parameters
        ****************
        childItem  - A QTreeWidgetItem whose checkbox state has just changed
        """
        logger.info("TreeView.checkParentItems called")
        try:
            parentItem = childItem.parent()
            if parentItem:
                childItem.treeWidget().blockSignals(True)
                if _areAllChildrenChecked(parentItem):
                    parentItem.setCheckState(0, Qt.Checked)
                else:
                    parentItem.setCheckState(0, Qt.Unchecked)
                self._saveCheckedState(parentItem)
                childItem.treeWidget().blockSignals(False)
                self._checkParentItems(parentItem)
        except Exception as e:
                print('Error in TreeView.checkParentItems: ' + str(e))
                logger.exception('Error in TreeView.checkParentItems: ' + str(e))


def _areAllChildrenChecked(item):
    """ Returns True is all the children of a QTreeWidgetItem are checked
    otherwise returns False 

    Input Parameter
    ****************
    item  - A QTreeWidgetItem whose checkbox state has just changed

    Returns
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