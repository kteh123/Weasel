import Displays.MeanROITimeCurveViewer as curveViewer

from PyQt5.QtGui import (QIcon)
from PyQt5.QtWidgets import QMdiSubWindow
from PyQt5.QtCore import  Qt

import logging
logger = logging.getLogger(__name__)


class Display():
    """
    Programming interfaces for modifying the Weasel GUI elements. 
    """

    def refresh(self):
        """
        Refreshes the Weasel display.
        """
        self.close_progress_bar()
        self.treeView.refreshDICOMStudiesTreeView()

    def reset_treeview(self):
        """
        Resets the Weasel treeview.
        """
        self.treeView.callUnCheckTreeViewItems()

    def save_treeview(self):
        """
        Saves the treeview selections.
        """
        self.treeView.refreshDICOMStudiesTreeView()

    def close_subwindows(self):
        """
        Closes all open windows.
        """
        if self.cmd == False:
            self.mdiArea.closeAllSubWindows()

    def tile_subwindows(self):
        """
        Tiles all open windows.
        """
        if self.cmd == False:
            self.mdiArea.tileSubWindows()

    def plot(self, signalName, maskName, x, y, x_axis_label, y_axis_label, title="Time/Curve Plot"):
        curveViewer.displayTimeCurve(self, signalName, maskName, x, y, x_axis_label, y_axis_label, title=title)

    def getMDIAreaDimensions(self):
        """
        Dimensions of the weasel canvas
        """
        return self.mdiArea.height(), self.mdiArea.width() 

    def addSubWindow(self, subWindow):
        """
        Add a new subwindow to the weasel canvas
        """
        self.mdiArea.addSubWindow(subWindow)

    def closeSubWindow(self, objectName):
        """
        Closes all subwindows with a given name

        objectName (string): the value set by setObjectName(objectName)
            when the SubWindow was created
        """   
        for subWin in self.mdiArea.subWindowList():
            if subWin.objectName() == objectName:
                subWin.close()   

    # replace by lower case notation "launch_external_app"
    def launchExternalApp(self, appWidget, title=None, icon=None):
        """This method takes a composite widget created by an external 
        application, makes it the central widget of an MDI subwindow
        and displays that subwindow in the Weasel MDI"""
        try:
            logger.info("OriginalPipelines.launchExternalApp called")
            subWindow = QMdiSubWindow()
            subWindow.setWindowFlags(Qt.CustomizeWindowHint | 
                                      Qt.WindowCloseButtonHint | 
                                      Qt.WindowMinimizeButtonHint |
                                      Qt.WindowMaximizeButtonHint)
            height, width = self.getMDIAreaDimensions()
            subWindow.setGeometry(0, 0, width, height)
            self.mdiArea.addSubWindow(subWindow)
            
            subWindow.setWidget(appWidget)

            if title is not None:
                subWindow.setWindowTitle(title)
            if icon is not None:
                subWindow.setWindowIcon(QIcon(icon))
            
            subWindow.show()
        except Exception as e:
            print('Error in OriginalPipelines.launchExternalApp: ' + str(e))
            logger.error('OriginalPipelines.launchExternalApp: ' + str(e)) 
