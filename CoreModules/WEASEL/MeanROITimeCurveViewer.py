from PyQt5.QtWidgets import (QMdiSubWindow, QVBoxLayout, QFormLayout, QWidget, QLabel, QFrame)
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
#import matplotlib.pyplot as plt

from CoreModules.WEASEL.GraphPlotter import PlotGraph as plotGraph
#import CoreModules.WEASEL.StyleSheet as styleSheet
#import sys
import logging
logger = logging.getLogger(__name__)


def displayTimeCurve(pointerToWeasel, signalName, maskName,
                     ROI_time_values, ROI_signal_values, xLabel, yLabel,  title=""):
    try:
        subWindow = QMdiSubWindow(pointerToWeasel)
        subWindow.setObjectName = 'Time_Curve_viewer'
        subWindow.setWindowTitle(title)
        subWindow.setWindowFlags(Qt.CustomizeWindowHint | 
                                          Qt.WindowCloseButtonHint | 
                                          Qt.WindowMinimizeButtonHint |
                                          Qt.WindowMaximizeButtonHint)
       
        height, width = pointerToWeasel.getMDIAreaDimensions()
        subWindow.setGeometry(0, 0, width, height)
        pointerToWeasel.mdiArea.addSubWindow(subWindow)

        layout = QVBoxLayout()
        formLayout = QFormLayout()
        labMaskName = QLabel(maskName)
        labMaskName.setFrameStyle(QFrame.Panel | QFrame.Raised)
        labMaskName.setLineWidth(3)
        formLayout.addRow(QLabel("Signal Series:"), 
                          QLabel(signalName))
        formLayout.addRow(QLabel("Mask Series:"),labMaskName)
        layout.addLayout(formLayout)
            
        roiCurvePlot = plotGraph(subWindow,
                ROI_time_values, 
                ROI_signal_values,
                xLabel,
                yLabel,
                title)
        layout.addWidget(roiCurvePlot.getGraphToolBar())
        layout.addWidget(roiCurvePlot.getGraphCanvas())
        widget = QWidget()
        widget.setLayout(layout)
        subWindow.setWidget(widget)
        subWindow.show()
    except Exception as e:
        print('Error in displayTimeCurve: ' + str(e))
        logger.exception('Error in displayTimeCurve: ' + str(e)) 


#class ROITimeCurveViewer(QMdiSubWindow):
#    """description of class"""
#    def __init__(self, ROI_time_values, ROI_signal_values, xLabel, yLabel,  title=""):
#        try:
#            super().__init__()
#            self.setMinimumSize(150,200)
#            self.xValues = ROI_time_values
#            self.yValues = ROI_signal_values
#            self.xLabel = xLabel
#            self.yLabel = yLabel
#            self.title = title
#            self.setWindowTitle(self.title)
#            #self.setStyleSheet(styleSheet.TRISTAN_GREY)
#            #Hide ? help button
#            self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
#            self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, True)
#            # Consider Qt.FramelessWindowHint if it works for Mac OS
#            self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)

#            self.layout = QVBoxLayout()
            
            
#            self.roiCurvePlot = plotGraph(self,
#                    self.xValues,
#                    self.yValues,
#                    self.xLabel,
#                    self.yLabel,
#                    self.title)
#            self.layout.addWidget(self.roiCurvePlot.getGraphToolBar())
#            self.layout.addWidget(self.roiCurvePlot.getGraphCanvas())
#            #self.setLayout(self.layout)
#            self.widget = QWidget()
#            self.widget.setLayout(self.layout)
#            self.setWidget(self.widget)
#            self.show()
#            #self.exec_()  #display plot

            
#        except Exception as e:
#            print('Error in class ROITimeCurveViewer.__init__: ' + str(e))
#            logger.exception('Error in class ROITimeCurveViewer.__init__: ' + str(e)) 

    
#    def displaySubWindow(self, pointerToWeasel):
#        self.show()
#        height, width = pointerToWeasel.getMDIAreaDimensions()
#        self.setGeometry(0, 0, width, height)
#        pointerToWeasel.mdiArea.addSubWindow(self)
