from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QApplication, QAbstractItemView,
                             QMdiSubWindow, QMenu, QAction, QHeaderView, QDockWidget,
                            QLabel, QProgressBar, QTreeWidget, QTreeWidgetItem)
import os
import sys
import logging
import time
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
                #set checked and expanded attributes to False
                # Joao commented on 23/07/2021 because it was decided to load the state in the XML file and not reset it.
                #start_time=time.time()
                #if pointerToWeasel.cmd == False: pointerToWeasel.objXMLReader.callResetXMLTree()   
                #end_time=time.time()
                #MakeXMLTreeTime = end_time - start_time 
                #print('Make XML Tree Time  = {}'.format(MakeXMLTreeTime))

                self.checkedImageList = []
                self.checkedSeriesList = []
                self.checkedStudyList = []
                self.checkedSubjectList = []

                self.treeViewColumnWidths = { 1: 0, 2: 0, 3: 0} # Needs to be removed from Weasel.py

                self.widget = QTreeWidget()
                
                #Minimum width of the tree view has to be set
                #to 300 to ensure its parent, theF docking widget 
                #initially displays wide enough to show the tree view
                self.widget.setMinimumSize(300,500)
                
                #prevent tree view shifting to the left when an item is clicked.
                self.widget.setAutoScroll(False)
                
                #Enable multiple selection using up arrow and Ctrl keys
                self.widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
                self.widget.setUniformRowHeights(True)
                self.widget.setColumnCount(4)
                self.widget.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
                self.widget.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
                self.widget.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
                self.widget.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
                self.widget.setHeaderLabels(["", "DICOM Files", "Date", "Time", "Path"])
                self.widget.setContextMenuPolicy(Qt.CustomContextMenu)

                self.buildTreeView(refresh=True)
                self.resizeTreeViewColumns()
                self.setEvents()
                # Comment these 2 lines since the purpose is to reload the XML and current state
                #collapseSeriesBranches(pointerToWeasel.widget.invisibleRootItem())
                #collapseStudiesBranches(pointerToWeasel.widget.invisibleRootItem())

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


    def buildTreeView(self, refresh=False):
        try:
            logger.info("TreeView.buildTreeView called")
            self.widget.clear()
            #block tree view signals to prevent recursive
            #searchs when each item is added to the tree view.
            self.widget.blockSignals(True)
            subjects = self.weasel.objXMLReader.getSubjects()
            for subject in subjects:
                subjectBranch = createTreeBranch("Subject",  subject,  self.widget, refresh)
                for study in subject:
                    studyBranch = createTreeBranch("Study",  study, subjectBranch, refresh)
                    for series in study:
                        seriesBranch = createTreeBranch("Series", series,  studyBranch, refresh)
                        for image in series:
                            createImageLeaf(image, seriesBranch, refresh)
            self.widget.blockSignals(False)   
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            #filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            print('Error in TreeView.buildTreeView at line {}: '.format(line_number) + str(e)) 
            logger.exception('Error in TreeView.buildTreeView at line {}: '.format(line_number) + str(e)) 


    def resizeTreeViewColumns(self):
        try:
            self.widget.resizeColumnToContents(0)
            self.widget.resizeColumnToContents(1)
            self.widget.resizeColumnToContents(2)
            self.widget.hideColumn(4)
            self.treeViewColumnWidths[1] = self.widget.columnWidth(1)
            self.treeViewColumnWidths[2] = self.widget.columnWidth(2)
            self.treeViewColumnWidths[3] = self.widget.columnWidth(3)
            #print("pointerToWeasel.treeViewColumnWidths={}".format(pointerToWeasel.treeViewColumnWidths))
        except Exception as e:
                print('Error in TreeView.resizeTreeViewColumns: ' + str(e))
                logger.exception('Error in TreeView.resizeTreeViewColumns: ' + str(e))


    def setEvents(self):
        #connect functions to events
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
                self.weasel.context.exec_(self.widget.mapToGlobal(pos))
        except Exception as e:
            print('Error in function TreeView.displayContextMenu: ' + str(e))


    def refreshDICOMStudiesTreeView(self, newSeriesName = ''):
        """Refreshed the Tree View and saves the checked state."""
        try:
            logger.info("TreeView.refreshDICOMStudiesTreeView called.")
            QApplication.setOverrideCursor(Qt.WaitCursor)
            start_time=time.time()
    
            #Save current tree view checked state to the xml tree in memory,
            #so that the tree view can be rebuilt with that checked state
            self.weasel.objXMLReader.saveTreeViewCheckedStateToXML(self.checkedSubjectList,
                                                            self.checkedStudyList,
                                                            self.checkedSeriesList,
                                                            self.checkedImageList)

            #store current column widths to be able
            #to restore them when the tree view is refreshed
            self.treeViewColumnWidths[1] = self.widget.columnWidth(1)
            self.treeViewColumnWidths[2] = self.widget.columnWidth(2)
            self.treeViewColumnWidths[3] = self.widget.columnWidth(3)
            # Joao Sousa suggestion
            self.widget.hide()
            self.buildTreeView(refresh=True)
            self.widget.setColumnWidth(1, self.treeViewColumnWidths[1])
            self.widget.setColumnWidth(2, self.treeViewColumnWidths[2])  
            self.widget.setColumnWidth(3, self.treeViewColumnWidths[3])

            #If no tree view items are now selected,
            #disable items in the Tools menu.
            self.toggleMenuItems()
            
            # Joao Sousa suggestion
            self.widget.show()

            #Save XML file to disc
            self.weasel.objXMLReader.saveXMLFile()
            
            end_time=time.time()
            refreshTreeViewTime = end_time - start_time 
            #print('refresh TreeView Time  = {}'.format(refreshTreeViewTime))
            QApplication.restoreOverrideCursor()
        except Exception as e:
            QApplication.restoreOverrideCursor()
            print('Error in TreeView.refreshDICOMStudiesTreeView: ' + str(e))
            logger.exception('Error in TreeView.refreshDICOMStudiesTreeView: ' + str(e))


    def saveTreeViewExpandedState(self, item, expandedState='True'):
        try:
            logger.info("TreeView.saveTreeViewExpandedState called.")
            if self.isASubjectSelected(item):
                subjectID = item.text(1).replace("Subject - ", "").strip()
                #print("subject selected subjectID={} state={}".format(subjectID, expandedState ))
                self.weasel.objXMLReader.setSubjectExpandedState( subjectID, expandedState)
            elif self.isAStudySelected(item):
                subjectID = item.parent().text(1).replace("Subject - ", "").strip()
                studyID = item.text(1).replace("Study - ", "").strip()
                self.weasel.objXMLReader.setStudyExpandedState( subjectID, studyID, expandedState)
            elif self.isASeriesSelected(item):
                subjectID = item.parent().parent().text(1).replace("Subject - ", "").strip()
                studyID = item.parent().text(1).replace("Study - ", "").strip()
                seriesID = item.text(1).replace("Series - ", "").strip()
                self.weasel.objXMLReader.setSeriesExpandedState(subjectID, studyID, seriesID, expandedState)
        except Exception as e:
                print('Error in TreeView.saveTreeViewExpandedState: ' + str(e))
                logger.exception('Error in TreeView.saveTreeViewExpandedState: ' + str(e))


    def toggleBlockSelectionCheckedState(self):
        try:
            logger.info("TreeView.toggleBlockSelectionCheckedState called.")
            if self.widget.selectedItems():
                noSelectedItems = len(self.widget.selectedItems())
                if noSelectedItems > 1:
                    loopCounter = 0
                    for selectedItem in self.widget.selectedItems():
                        #selectedItem.setSelected(True)
                        #reverse checked status of each selected item
                        #skip the first iteration because this was covered
                        #in the above if statement.
                        loopCounter += 1
                        if loopCounter == 1 or loopCounter == noSelectedItems:
                            continue
                        if selectedItem.checkState(0)  == Qt.Checked:
                            selectedItem.setCheckState(0, Qt.Unchecked)
                        elif selectedItem.checkState(0)  == Qt.Unchecked:
                            selectedItem.setCheckState(0, Qt.Checked)               
        except Exception as e:
            print('Error in TreeView.toggleBlockSelectionCheckedState: ' + str(e))
            logger.exception('Error in TreeView.toggleBlockSelectionCheckedState: ' + str(e))  


    def toggleMenuItems(self):
            """TO DO"""
            try:
                logger.info("TreeView.toggleMenuItems called.")
                for menu in self.weasel.listMenus:
                    menuItems = menu.actions()
                    for menuItem in menuItems:
                        if not menuItem.isSeparator():
                            if not(menuItem.data() is None):
                                #Assume not all tools will act on an image
                                #Assume all tools act on a series 
                                #
                                #Disable all menu items to account for the
                                #case when all checkboxes are unchecked. 
                                #Then enable depending on what is checked.
                                menuItem.setEnabled(False)  
                                if self.isASeriesChecked:
                                    menuItem.setEnabled(True)
                                elif self.isAnImageChecked:
                                    if menuItem.data():
                                        menuItem.setEnabled(True)
                                    else:
                                        menuItem.setEnabled(False) 
            except Exception as e:
                print('Error in TreeView.toggleMenuItems: ' + str(e))
                logger.exception('Error in TreeView.toggleMenuItems: ' + str(e))

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
        unCheckTreeViewItems(root)
        QApplication.restoreOverrideCursor()


    def buildListsCheckedItems(self):
        """This function generates and returns lists of checked items."""
        logger.info("TreeView.buildListsCheckedItems called")
        try:
            start_time=time.time()
            self.checkedImageList = []
            self.checkedSeriesList = []
            self.checkedStudyList = []
            self.checkedSubjectList = []
            root = self.widget.invisibleRootItem()
            subjectCount = root.childCount()
            for i in range(subjectCount):
                subject = root.child(i)
                if subject.checkState(0) == Qt.Checked:
                    self.checkedSubjectList.append(subject.text(1).replace("Subject - ", "").strip())
                studyCount = subject.childCount()
                for j in range(studyCount):
                    study = subject.child(j)
                    if study.checkState(0) == Qt.Checked:
                        checkedSubjectData = []
                        parentStudy = study.parent()
                        checkedSubjectData.append(parentStudy.text(1).replace("Subject - ", "").strip())
                        checkedSubjectData.append(study.text(1).replace("Study - ", "").strip())
                        self.checkedStudyList.append(checkedSubjectData)
                    seriesCount = study.childCount()
                    for k in range(seriesCount):
                        series = study.child(k)
                        if series.checkState(0) == Qt.Checked:
                            checkedSeriesData = []
                            parentSeries = series.parent()
                            grandParentSeries = parentSeries.parent() 
                            checkedSeriesData.append(grandParentSeries.text(1).replace("Subject - ", "").strip())
                            checkedSeriesData.append(parentSeries.text(1).replace("Study - ", "").strip())
                            checkedSeriesData.append(series.text(1).replace("Series - ", "").strip())
                            self.checkedSeriesList.append(checkedSeriesData)
                        imageCount = series.childCount()
                        for n in range(imageCount):
                            image = series.child(n)
                            if image.checkState(0) == Qt.Checked:
                                checkedImagesData = []
                                series = image.parent()
                                study = series.parent()
                                subject = study.parent()
                                checkedImagesData.append(subject.text(1).replace("Subject - ", "").strip())
                                checkedImagesData.append(study.text(1).replace("Study - ", "").strip())
                                checkedImagesData.append(series.text(1).replace("Series - ", "").strip())
                                checkedImagesData.append(image.text(4))
                                self.checkedImageList.append(checkedImagesData)

            end_time=time.time()
            buildCheckedListTime = end_time - start_time 
            #print('buildCheckedListTime Time  = {}'.format(buildCheckedListTime))
        except Exception as e:
            print('Error in TreeView.buildListsCheckedItems: ' + str(e))
            logger.exception('Error in TreeView.buildListsCheckedItems: ' + str(e))


    @property
    def isAnImageChecked(self): 
        flag = False
        root = self.widget.invisibleRootItem()
        subjectCount = root.childCount()
        checkedImagesList = []
        for i in range(subjectCount):
            subject = root.child(i)
            studyCount = subject.childCount()
            for j in range(studyCount):
                study = subject.child(j)
                seriesCount = study.childCount()
                for n in range(seriesCount):
                    series = study.child(n)
                    imagesCount = series.childCount()
                    for k in range(imagesCount):
                        image = series.child(k)
                        if image.checkState(0) == Qt.Checked:
                            flag = True
                            break
        return flag

    @property
    def isASeriesChecked(self): 
        flag = False
        root = self.widget.invisibleRootItem()
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
                        flag = True
                        break
        return flag
     
    @property
    def isAStudyChecked(self): #remove from API TreeViewState
        flag = False
        root = self.widget.invisibleRootItem()
        subjectCount = root.childCount()
        checkedStudiesList = []
        for i in range(subjectCount):
            subject = root.child(i)
            studyCount = subject.childCount()
            for j in range(studyCount):
                study = subject.child(j)   
                if study.checkState(0) == Qt.Checked:
                    flag = True
                    break
        return flag

    @property
    def isASubjectChecked(self): 
        flag = False
        root = self.widget.invisibleRootItem()
        subjectCount = root.childCount()
        checkedSubjectsList = []
        for i in range(subjectCount):
            subject = root.child(i)
            if subject.checkState(0) == Qt.Checked:
                flag = True
                break
        return flag

    def isAnItemChecked(self):
        """Returns True is an item is selected in the DICOM
        tree view, else returns False"""
        try:
            logger.info("TreeView.isAnItemChecked called.")
            if self.isAnImageChecked or self.isASeriesChecked:
                return True
            else:
                return False
        except Exception as e:
            print('Error in isAnItemChecked: ' + str(e))
            logger.exception('Error in isAnItemChecked: ' + str(e))

    def returnCheckedSubjects(self):
        """This function generates and returns a list of checked series."""
        logger.info("TreeView.returnCheckedSubjects called")
        try:
            root = self.widget.invisibleRootItem()
            subjectCount = root.childCount()
            checkedSubjectsList = []
            for i in range(subjectCount):
                subject = root.child(i)
                if subject.checkState(0) == Qt.Checked:
                    checkedSubjectsList.append(subject)
            return checkedSubjectsList
        except Exception as e:
            print('Error in TreeView.returnCheckedSubjects: ' + str(e))
            logger.exception('Error in TreeView.returnCheckedSubjects: ' + str(e))

    def returnCheckedStudies(self):
        """This function generates and returns a list of checked series."""
        logger.info("TreeView.returnCheckedStudies called")
        try:
            root = self.widget.invisibleRootItem()
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
            logger.exception('Error in TreeView.returnCheckedStudies: ' + str(e))

    def returnCheckedSeries(self):
        """This function generates and returns a list of checked series."""
        logger.info("TreeView.returnCheckedSeries called")
        try:
            root = self.widget.invisibleRootItem()
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
            logger.exception('Error in TreeView.returnCheckedSeries: ' + str(e))

    def returnCheckedImages(self):
        """This function generates and returns a list of checked images."""
        logger.info("TreeView.returnCheckedImages called")
        try:
            root = self.widget.invisibleRootItem()
            subjectCount = root.childCount()
            checkedImagesList = []
            for i in range(subjectCount):
                subject = root.child(i)
                studyCount = subject.childCount()
                for j in range(studyCount):
                    study = subject.child(j)
                    seriesCount = study.childCount()
                    for n in range(seriesCount):
                        series = study.child(n)
                        imagesCount = series.childCount()
                        for k in range(imagesCount):
                            image = series.child(k)
                            if image.checkState(0) == Qt.Checked:
                                checkedImagesList.append(image)
            return checkedImagesList
        except Exception as e:
            print('Error in TreeView.returnCheckedImages: ' + str(e))
            logger.exception('Error in TreeView.returnCheckedImages: ' + str(e))
        

    def returnSeriesImageList(self, subjectName, studyName, seriesName):
        try:
            imagePathList = []
            #get subject
            root = self.widget.invisibleRootItem()
            subjectCount = root.childCount()
            for i in range(subjectCount):
                subject = root.child(i)
                subjectID = subject.text(1).replace("Subject - ", "").strip()
                if subjectID == subjectName:
                    studyCount = subject.childCount()
                    for j in range(studyCount):
                        study = subject.child(j)
                        studyID = study.text(1).replace("Study - ", "").strip()
                        if studyID == studyName:
                            seriesCount = study.childCount()
                            for k in range(seriesCount):
                                series = study.child(k)
                                seriesID = series.text(1).replace("Series - ", "").strip()
                                if seriesID == seriesName:
                                    imageCount = series.childCount()
                                    for n in range(imageCount):
                                        image = series.child(n)
                                        imagePath = image.text(4)
                                        imagePathList.append(imagePath)
                                    break
            return imagePathList
        except Exception as e:
                print('Error in TreeView.returnSeriesImageList: ' + str(e))
                logger.exception('Error in TreeView.returnSeriesImageList: ' + str(e))


    def returnImageName(self, subjectName, studyName, seriesName, imagePath):
        try:
            root = self.widget.invisibleRootItem()
            subjectCount = root.childCount()
            for i in range(subjectCount):
                subject = root.child(i)
                subjectID = subject.text(1).replace("Subject - ", "").strip()
                if subjectID == subjectName:
                    studyCount = subject.childCount()
                    for j in range(studyCount):
                        study = subject.child(j)
                        studyID = study.text(1).replace("Study - ", "").strip()
                        if studyID == studyName:
                            seriesCount = study.childCount()
                            for k in range(seriesCount):
                                series = study.child(k)
                                seriesID = series.text(1).replace("Series - ", "").strip()
                                if seriesID == seriesName:
                                    imageCount = series.childCount()
                                    for n in range(imageCount):
                                        image = series.child(n)
                                        if image.text(4) == imagePath:
                                            return image.text(1).replace("Image - ", "").strip()
                                    break
            return ''
        except Exception as e:
                print('Error in TreeView.returnImageName: ' + str(e))
                logger.exception('Error in TreeView.returnImageName: ' + str(e))


    def getPathParentNode(self, inputPath):
        """This function returns a list of subjectID, studyID an seriesID based on the given filepath."""
        logger.info("TreeView.getPathParentNode called")
        try:
            root = self.widget.invisibleRootItem()
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
                            if image.text(4) == inputPath:
                                subjectID = subject.text(1).replace('Subject -', '').strip()
                                studyID = study.text(1).replace('Study -', '').strip()
                                seriesID = series.text(1).replace('Series -', '').strip()
                                return (subjectID, studyID, seriesID)
        except Exception as e:
            print('Error in TreeView.getPathParentNode: ' + str(e))
            logger.exception('Error in TreeView.getPathParentNode: ' + str(e))


    def getSeriesNumberAfterLast(self, inputPath):
        """This function returns a list of subjectID, studyID an seriesID based on the given filepath."""
        logger.info("TreeView.getPathParentNode called")
        try:
            root = self.widget.invisibleRootItem()
            subjectCount = root.childCount()
            for i in range(subjectCount):
                subject = root.child(i)
                studyCount = subject.childCount()
                for j in range(studyCount):
                    study = subject.child(j)
                    seriesCount = study.childCount()
                    seriesList = []
                    seriesFlag = False
                    for k in range(seriesCount):
                        series = study.child(k)
                        seriesList.append(int((series.text(1).replace('Series -', '').strip()).split('_')[0]))
                        imageCount = series.childCount()
                        for n in range(imageCount):
                            image = series.child(n)
                            if image.text(4) == inputPath:
                                seriesFlag = True
                    if seriesFlag == True:
                        seriesList.sort()
                        return str(seriesList[-1] + 1)
        except Exception as e:
            print('Error in TreeView.getSeriesNumberAfterLast: ' + str(e))
            logger.exception('Error in TreeView.getSeriesNumberAfterLast: ' + str(e))


    def returnSeriesLists(self):
        """This function is not used.
            This function builds and returns:
                1. a list of names of series that do not include masks
                2. a list of names of series that only include masks.
        """
        logger.info("TreeView.returnSeriesLists called")
        try:
            listMaskSeries = []
            listNonMaskSeries = []
            root = self.widget.invisibleRootItem()
            subjectCount = root.childCount()
            #Subject loop
            for i in range(subjectCount):
                subject = root.child(i)
                if subject.checkState(0) == Qt.Checked:
                    self.checkedSubjectList.append(subject.text(1).replace("Subject - ", "").strip())
                studyCount = subject.childCount()
                #study loop
                for j in range(studyCount):
                    study = subject.child(j)
                    if study.checkState(0) == Qt.Checked:
                        checkedSubjectData = []
                        parentStudy = study.parent()
                        checkedSubjectData.append(parentStudy.text(1).replace("Subject - ", "").strip())
                        checkedSubjectData.append(study.text(1).replace("Study - ", "").strip())
                        self.checkedStudyList.append(checkedSubjectData)
                    seriesCount = study.childCount()
                    #series loop
                    for k in range(seriesCount):
                        series = study.child(k)
                        seriesName = series.text(1).replace("Series - ", "").strip()
                        if "_ROI_" in seriesName:
                            listMaskSeries.append(seriesName)
                        else:
                            listNonMaskSeries.append(seriesName)

            return listMaskSeries, listNonMaskSeries        

        except Exception as e:
            print('Error in TreeView.returnSeriesLists: ' + str(e))
            logger.exception('Error in TreeView.returnSeriesLists: ' + str(e))


    def isAnImageSelected(self, item):
            """Returns True is a single image is selected in the DICOM
            tree view, else returns False"""
            try:
                logger.info("TreeView.isAnImageSelected called.")
                #print("item.text(1).lower()={}".format(item.text(1).lower()))
                if ('image' in item.text(1).lower()) and ('images' not in item.text(1).lower()):
                    return True
                else:
                    return False
            except Exception as e:
                print('Error in isAnImageSelected: ' + str(e))
                logger.exception('Error in isAnImageSelected: ' + str(e))

    def isASeriesSelected(self, item):
            """Returns True is a series is selected in the DICOM
            tree view, else returns False"""
            try:
                logger.info("TreeView isASeriesSelected called.")
                if 'series' in item.text(1).lower():
                    return True
                else:
                    return False
            except Exception as e:
                print('Error in isASeriesSelected: ' + str(e))
                logger.exception('Error in isASeriesSelected: ' + str(e))

    def isASubjectSelected(self, item):
        """Returns True is a subject is selected in the DICOM
        tree view, else returns False"""
        try:
            logger.info("TreeView isASubjectSelected called.")
            if item:
                if 'subject' in item.text(1).lower():
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            print('Error in isASubjectSelected: ' + str(e))
            logger.exception('Error in isASubjectSelected: ' + str(e))

    def isAStudySelected(self, item):
            """Returns True is a study is selected in the DICOM
            tree view, else returns False"""
            try:
                logger.info("TreeView isAStudySelected called.")
                if 'study' in item.text(1).lower():
                    return True
                else:
                    return False   
            except Exception as e:
                print('Error in isAStudySelected: ' + str(e))
                logger.exception('Error in isAStudySelected: ' + str(e))


def createTreeBranch(branchName, branch, parent, refresh=False):
    try:
        branchID = branch.attrib['id']
        logger.info("TreeView.createTreeBranch, branch ID={}".format(branchID))
        thisBranch = QTreeWidgetItem(parent)
        thisBranch.setText(0, '')
        thisBranch.setText(1, branchName + " - {}".format(branchID))
        thisBranch.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        #put a checkbox in front of this branch
        thisBranch.setFlags(thisBranch.flags() | Qt.ItemIsUserCheckable)
        thisBranch.setCheckState(0, Qt.Unchecked)
        thisBranch.setExpanded(True)
        if refresh:
            if 'expanded' in branch.attrib:
                expand = branch.attrib['expanded']
            else:
                expand = "False"
            #print("expand={} when branch={}".format(expand, branchID))
            if expand == "False":
                thisBranch.setExpanded(False)
            
            if 'checked' in branch.attrib:
                checked = branch.attrib['checked']
            else:
                checked = "False"
            #print("checked={} when branch={}".format(checked, branchID))
            if checked == "True":
                thisBranch.setCheckState(0, Qt.Checked)

        return thisBranch# treeWidgetItemCounter
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        #filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print('Error in TreeView.createTreeBranch at line {} when branch ID={}: '.format(line_number, branchID) + str(e)) 
        logger.exception('Error in TreeView.createTreeBranch at line {}: '.format(line_number) + str(e)) 


def createImageLeaf(image, seriesBranch, refresh=False):
    try:
        #Extract filename from file path
        if image:
            if image.find('label') is None:
                imageName = os.path.basename(image.find('name').text)
            else:
                imageName = image.find('label').text
            logger.info("TreeView.createImageLeaf called with imageName={}".format(imageName))
            imageDate = image.find('date').text
            imageTime = image.find('time').text
            imagePath = image.find('name').text
            imageLeaf = QTreeWidgetItem(seriesBranch)
            imageLeaf.setToolTip(0, "At least one image must be checked to view an image(s)")
            imageLeaf.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            #put a checkbox in front of each image
            imageLeaf.setFlags(imageLeaf.flags() | Qt.ItemIsUserCheckable)
            imageLeaf.setCheckState(0, Qt.Unchecked)
            imageLeaf.setText(0, '')
            imageLeaf.setText(1, ' Image - ' + imageName)
            imageLeaf.setText(2, imageDate)
            imageLeaf.setText(3, imageTime)
            imageLeaf.setText(4, imagePath)

            if refresh:
                if 'checked' in image.attrib:
                    checked = image.attrib['checked']
                    #print("checked in image")
                else:
                    checked = "False"
                #print("checked={} when image Name={}".format(checked, imageName))
                if checked == "True":
                    imageLeaf.setCheckState(0, Qt.Checked)
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        #filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        print('Error in TreeView.createImageLeaf at line {}: '.format(line_number) + str(e)) 
        logger.exception('Error in TreeView.createImageLeaf at line {}: '.format(line_number) + str(e)) 


def toggleItemCheckedState(item, col):
    """When a tree view item is selected, it is also checked
    and when a tree view item is checked, it is also selected.
    This function also sets boolean flags that indicate if a 
    subject, study, series or image is checked.
    """
    try:
        logger.info("TreeView.toggleItemCheckedState called.")
        if col == 0:
            #Checkbox clicked
            if item.isSelected():
                item.setSelected(False)
            else:
                item.setSelected(False)
        elif col == 1:
            #item clicked
            if item.checkState(0)  == Qt.Checked:
                item.setCheckState(0, Qt.Unchecked) 
            elif item.checkState(0)  == Qt.Unchecked:
                item.setCheckState(0, Qt.Checked)     
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print('Error in toggleItemCheckedState at line number {} when {}: '.format(line_number, e))
        logger.exception('Error in toggleItemCheckedState: ' + str(e))


def checkChildItems(item):
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
                item.treeWidget().blockSignals(False)
                checkChildItems(childItem)
    except Exception as e:
        print('Error in TreeView.checkChildItems: ' + str(e))
        logger.exception('Error in TreeView.checkChildItems: ' + str(e))


def checkParentItems(item):
    """This function uses recursion to set the state of Parent checkboxes to
    match collective state of their children.
    
    Input Parameters
    ****************
    item  - A QTreeWidgetItem whose checkbox state has just changed
    """
    logger.info("TreeView.checkParentItems called")
    #print("TreeView.checkParentItems called")
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
            logger.exception('Error in TreeView.checkParentItems: ' + str(e))

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
            logger.exception('Error in TreeView.areAllChildrenChecked: ' + str(e))


def expandTreeViewBranch(item, newSeriesName = ''):
        """This function is not used."""
        try:
            logger.info("TreeView.expandTreeViewBranch called.")
            if item.childCount() > 0:
                itemCount = item.childCount()
                for n in range(itemCount):
                    childItem = item.child(n)
                    branchText = childItem.text(1).lower()
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
            logger.exception('Error in TreeView.expandTreeViewBranch: ' + str(e))


def unCheckTreeViewItems(item):
    """This function uses recursion to set the state of child checkboxes 
    of item to unchecked.
    
    Input Parameters
    ****************
    item  - A QTreeWidgetItem 
    """
    logger.info("TreeView.unCheckTreeViewItems called")
    #print("TreeView.unCheckTreeViewItems called")
    try:
        if item.childCount() > 0:
            itemCount = item.childCount()
            #print("itemCount ={}".format(itemCount))
            for n in range(itemCount):
                childItem = item.child(n)
                item.treeWidget().blockSignals(True)
                childItem.setCheckState(0, Qt.Unchecked)
                item.treeWidget().blockSignals(False)
                unCheckTreeViewItems(childItem)
    except Exception as e:
        print('Error in TreeView.unCheckTreeViewItems: ' + str(e))
        logger.exception('Error in TreeView.unCheckTreeViewItems: ' + str(e))


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
                if 'study' in childItem.text(1).lower():
                    item.treeWidget().blockSignals(True)
                    childItem.setExpanded(False)
                    item.treeWidget().blockSignals(False)
                else:
                    collapseStudiesBranches(childItem)
    except Exception as e:
            print('Error in TreeView.collapseStudiesBranches: ' + str(e))
            logger.exception('Error in TreeView.collapseStudiesBranches: ' + str(e))


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
                if 'series' in childItem.text(1).lower():
                    item.treeWidget().blockSignals(True)
                    childItem.setExpanded(False)
                    item.treeWidget().blockSignals(False)
                else:
                    collapseSeriesBranches(childItem)
    except Exception as e:
            print('Error in TreeView.collapseSeriesBranches: ' + str(e))
            logger.exception('Error in TreeView.collapseSeriesBranches: ' + str(e))





