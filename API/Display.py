import CoreModules.WEASEL.TreeView as treeView
import Displays.MeanROITimeCurveViewer as curveViewer
from CoreModules.WEASEL.PythonMenuBuilder import PythonMenuBuilder as menuBuilder
from CoreModules.WEASEL.DeveloperTools import UserInterfaceTools

from PyQt5.QtGui import (QIcon)
from PyQt5.QtWidgets import QMdiSubWindow
from PyQt5.QtCore import  Qt

import logging
logger = logging.getLogger(__name__)


class Display():
    """
    Programming interfaces for modifying the Weasel GUI elements. 
    """

    def refresh(self, new_series_name=None):
        """
        Refreshes the Weasel display.
        """
        self.close_progress_bar()
        ui = UserInterfaceTools(self)
        ui.refreshWeasel(new_series_name=new_series_name)

    def reset_treeview(self):
        """
        Resets the Weasel treeview.
        """
        treeView.callUnCheckTreeViewItems(self)

    def save_treeview(self):
        """
        Saves the treeview selections.
        """
        treeView.refreshDICOMStudiesTreeView(self)

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

    def menu(self, label = "Menu"):
        """
        Interface for Python menu builder
        """
        return menuBuilder(self, label)

    def addSubWindow(self, subWindow):
        """
        Add a new subwindow to the weasel canvas
        """
        self.mdiArea.addSubWindow(subWindow)

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
