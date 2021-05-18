from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, 
                             QStyledItemDelegate, QLabel, QSpinBox, QMessageBox, QScrollBar,
                             QDoubleSpinBox, QLineEdit, QListWidget, QAbstractItemView )
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from CoreModules.WEASEL.GraphPlotter import PlotGraph as plotGraph
import CoreModules.WEASEL.StyleSheet as styleSheet
import sys
import logging
logger = logging.getLogger(__name__)


class ROITimeCurveViewer(QDialog):
    """description of class"""
    def __init__(self, ROI_time_values, ROI_signal_values, xLabel, yLabel,  title=""):
        try:
            super().__init__()
            self.setMinimumSize(150,200)
            self.xValues = ROI_time_values
            self.yValues = ROI_signal_values
            self.xLabel = xLabel
            self.yLabel = yLabel
            self.title = title
            self.setWindowTitle(self.title)
            self.setStyleSheet(styleSheet.TRISTAN_GREY)
            #Hide ? help button
            self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
            self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, True)
            # Consider Qt.FramelessWindowHint if it works for Mac OS
            self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)

            self.layout = QVBoxLayout()
            
            self.roiCurvePlot = plotGraph(self,
                    self.xValues,
                    self.yValues,
                    self.xLabel,
                    self.yLabel,
                    self.title)
            self.layout.addWidget(self.roiCurvePlot.getGraphToolBar())
            self.layout.addWidget(self.roiCurvePlot.getGraphCanvas())
            self.setLayout(self.layout)
            self.exec_()  #display plot
        except Exception as e:
            print('Error in class ROITimeCurveViewer.__init__: ' + str(e))
            logger.exception('Error in class ROITimeCurveViewer.__init__: ' + str(e)) 

