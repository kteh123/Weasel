from PyQt5.QtWidgets import QVBoxLayout, QWidget, QMdiSubWindow, QPushButton
from PyQt5.QtCore import Qt
from CoreModules.WEASEL.SeriesSelector import SeriesSelector as seriesSelector
import CoreModules.WEASEL.ReadDICOM_Image as ReadDICOM_Image
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import logging
import math
import numpy as np
logger = logging.getLogger(__name__)

__author__ = "Steve Shillitoe"


def isEnabled(weasel):
    return True


class NavigationToolbar(NavigationToolbar):
    """
    Removes unwanted default buttons in the Navigation Toolbar by creating
    a subclass of the NavigationToolbar class from from 
    matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    that only defines the desired buttons
    """
    toolitems = [t for t in NavigationToolbar.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]


def main(pointerToWeasel):
    try:
        logger.info('Tutorial_Ferret.main called.')
                    
        widget = QWidget()
        widget.setLayout(QVBoxLayout()) 
        subWindow = QMdiSubWindow(pointerToWeasel)
        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.setWidget(widget)
        subWindow.setObjectName("ferret_Window")
        subWindow.setWindowTitle("Ferret")
        height, width = pointerToWeasel.getMDIAreaDimensions()
        subWindow.setGeometry(width * 0.4,0,width*0.6,height)

        signalSeriesSelector = seriesSelector(pointerToWeasel, "Signal")
        maskSeriesSelector = seriesSelector(pointerToWeasel, "Mask")
        
        widget.layout().addWidget(signalSeriesSelector.createSeriesSelector())
        widget.layout().addWidget(maskSeriesSelector.createSeriesSelector())

        btnProcessData = QPushButton("Process Data")
        figure = plt.figure(figsize=(5, 8), dpi=100)
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter 
        # to its __init__ function
        canvas = FigureCanvas(figure)

        btnProcessData.clicked.connect(lambda: getTimeCurve(
            pointerToWeasel,
            signalSeriesSelector.selectedSeriesData,
            maskSeriesSelector.selectedSeriesData,
            figure,
            canvas))
        widget.layout().addWidget(btnProcessData)

        
        # this is the Navigation widget
        # it takes the Canvas widget as a parent
        toolbar = NavigationToolbar(canvas, subWindow)
        widget.layout().addWidget(toolbar)
        widget.layout().addWidget(canvas)


        pointerToWeasel.mdiArea.addSubWindow(subWindow)
        subWindow.show()
    except Exception as e:
        print('Error in : Tutorial_Ferret.main ' + str(e))
        logger.exception('Error in : Tutorial_Ferret.main ' + str(e))


def getTimeCurve(pointerToWeasel, signalData, maskData, figure, canvas):
    try:
        #Get list of images in the signal series
        signalImageList = pointerToWeasel.objXMLReader.getImagePathList(signalData[0], 
                                                              signalData[1], 
                                                              signalData[2])

        maskImageList = pointerToWeasel.objXMLReader.getImagePathList(maskData[0], 
                                                              maskData[1], 
                                                              maskData[2])
        #print("maskImageList={} len={}".format(maskImageList, len(maskImageList)))
        ROI_signal_values = []
        ROI_time_values = []
        #loop over list of mask images
        for i, image in enumerate(maskImageList):
            #get mask pixel array
            maskPixelArray = ReadDICOM_Image.returnPixelArray(image)
            if maskPixelArray is not None:
                #get corresponding signal pixel array
                signalPixelArray = ReadDICOM_Image.returnPixelArray(signalImageList[i])
                mean_signal = round(np.mean(np.extract(maskPixelArray, signalPixelArray)), 3)
                if not math.isnan(mean_signal):
                    ROI_signal_values.append(mean_signal)
                    ROI_time_values.append(i)
                    #The following is not working, same time 
                    #returned for all images
                    #acquisitionTime = ReadDICOM_Image.getImageTagValue(
                    #    signalImageList[i], "AcquisitionTime")
                    #ROI_time_values.append(acquisitionTime)
            else:
                print("mask pixel array is none")

        #print("ROI_signal_values={}".format(ROI_signal_values))
        ROI_curve = np.array([ROI_time_values, ROI_signal_values])
        #print("ROI_curves={}".format(ROI_curve))

        timeCurvePlot = setUpPlot(figure)
        timeCurvePlot.plot(ROI_time_values, ROI_signal_values, 'r.-', label= "ROI Time Curve")
        canvas.draw()
    except Exception as e:
        print('Error in : Tutorial_Ferret.getTimeCurve ' + str(e))
        logger.exception('Error in : Tutorial_Ferret.getTimeCurve ' + str(e))
#    #for i, img in enumerate(children):
#    #    image_array = img.PixelArray
#    #    mask_array = mask[i].PixelArray
#    #    mean_signal = ROI_value(image_array, mask_array)
#    #    ROI_signal_values.append(mean_signal)

#    #ROI_time_values = signal["AcquisitionTime"]
#    #ROI_curve = np.array(ROI_time_values, ROI_signal_values)

#    #new_series = signal.new(suffix = 'ROI curve')
#    #new_series.write(ROI_curve)

  
#def SetUpPlotArea(self, layout):
#        """Adds widgets for the display of the graph onto the 
#        right-hand side vertical layout.
        
#        Inputs
#        ------
#        layout - holds a pointer to the right-hand side vertical layout widget
#        """
#        layout.setAlignment(QtCore.Qt.AlignTop)

#        # lblModelImage is used to display a schematic
#        # representation of the model.
#        self.lblModelImage = QLabel('') 
#        self.lblModelImage.setAlignment(QtCore.Qt.AlignCenter )
#        self.lblModelImage.setMargin(2)
                                        
#        self.lblModelName = QLabel('')
#        self.lblModelName.setAlignment(QtCore.Qt.AlignCenter)
#        self.lblModelName.setMargin(2)
#        self.lblModelName.setFrameStyle(QFrame.Panel | QFrame.Sunken)
#        self.lblModelName.setWordWrap(True)

#        self.figure = plt.figure(figsize=(5, 8), dpi=100) 
#        # this is the Canvas Widget that displays the `figure`
#        # it takes the `figure` instance as a parameter 
#        # to its __init__ function
#        self.canvas = FigureCanvas(self.figure)
#        # this is the Navigation widget
#        # it takes the Canvas widget as a parent
#        self.toolbar = NavigationToolbar(self.canvas, self)

#        # Display TRISTAN & University of Leeds Logos in labels
#        self.lblFERRET_Logo = QLabel(self)
#        self.lblTRISTAN_Logo = QLabel(self)
#        self.lblUoL_Logo = QLabel(self)
#        self.lblTRISTAN_Logo.setAlignment(QtCore.Qt.AlignHCenter)
#        self.lblUoL_Logo.setAlignment(QtCore.Qt.AlignHCenter)

#        pixmapFERRET = QPixmap(FERRET_LOGO)
#        pMapWidth = pixmapFERRET.width() 
#        pMapHeight = pixmapFERRET.height() 
#        pixmapFERRET = pixmapFERRET.scaled(pMapWidth, pMapHeight, 
#                      QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
#        self.lblFERRET_Logo.setPixmap(pixmapFERRET) 

#        pixmapTRISTAN = QPixmap(LARGE_TRISTAN_LOGO)
#        pMapWidth = pixmapTRISTAN.width() * 0.5
#        pMapHeight = pixmapTRISTAN.height() * 0.5
#        pixmapTRISTAN = pixmapTRISTAN.scaled(pMapWidth, pMapHeight, 
#                      QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
#        self.lblTRISTAN_Logo.setPixmap(pixmapTRISTAN)

#        pixmapUoL = QPixmap(UNI_OF_LEEDS_LOGO)
#        pMapWidth = pixmapUoL.width() * 0.75
#        pMapHeight = pixmapUoL.height() * 0.75
#        pixmapUoL = pixmapUoL.scaled(pMapWidth, pMapHeight, 
#                      QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
#        self.lblUoL_Logo.setPixmap(pixmapUoL)
       
#        layout.addWidget(self.lblModelImage)
#        layout.addWidget(self.lblModelName)
#        layout.addWidget(self.toolbar)
#        layout.addWidget(self.canvas)
#        # Create horizontal layout box to hold TRISTAN & University of Leeds Logos
#        horizontalLogoLayout = QHBoxLayout()
#        horizontalLogoLayout.setAlignment(QtCore.Qt.AlignRight)
#        # Add horizontal layout to bottom of the vertical layout
#        layout.addLayout(horizontalLogoLayout)
#        # Add labels displaying logos to the horizontal layout, 
#        # Tristan on the LHS, UoL on the RHS
#        horizontalLogoLayout.addWidget(self.lblFERRET_Logo)
#        horizontalLogoLayout.addWidget(self.lblTRISTAN_Logo)
#        horizontalLogoLayout.addWidget(self.lblUoL_Logo)

#def plotMRSignals(self, nameCallingFunction: str):
#        """If a Region of Interest has been selected, 
#        this function plots the normalised signal against time curves 
#        for the ROI, AIF, VIF.  
#        Also, plots the normalised signal/time curve predicted by the 
#        selected model.
        
#        Input Parameter
#        ----------------
#        nameCallingFunction - Name of the function or widget from whose event 
#        this function is called. This information is used in logging and error
#        handling.
#        """
#        try:
#            boolAIFSelected = False
#            boolVIFSelected = False

#            objPlot = self.setUpPlot()

#            # Get the names of the regions 
#            # selected from the drop down lists.
#            ROI = str(self.cmbROI.currentText())
#            AIF = str(self.cmbAIF.currentText())
#            VIF = 'Not Selected'
#            VIF = str(self.cmbVIF.currentText())

#            logger.info('Function plot called from ' +
#                        nameCallingFunction + 
#                        ' when ROI={}, AIF={} and VIF={}'.format(ROI, AIF, VIF))

#            arrayTimes = np.array(self.signalData['time'], dtype='float')
            
#            if AIF != 'Please Select':
#                array_AIF_MR_Signals = np.array(self.signalData[AIF], dtype='float')
#                objPlot.plot(arrayTimes, array_AIF_MR_Signals, 'r.-', label= AIF)
#                boolAIFSelected = True

#            array_VIF_MR_Signals = []
#            if VIF != 'Please Select':
#                array_VIF_MR_Signals = np.array(self.signalData[VIF], dtype='float')
#                objPlot.plot(arrayTimes, array_VIF_MR_Signals, 'k.-', label= VIF)
#                boolVIFSelected = True
                    
#            # Plot concentration curve from the model
#            modelName = str(self.cmbModels.currentText())
#            if modelName != 'Select a model':
#                inletType = self.objXMLReader.getModelInletType(modelName)
#                if (inletType == 'dual') and \
#                    (boolAIFSelected and boolVIFSelected) \
#                    or \
#                    (inletType == 'single') and boolAIFSelected:
#                    self.plotModelCurve(modelName, inletType,
#                                        arrayTimes, 
#                                        array_AIF_MR_Signals, 
#                                       array_VIF_MR_Signals, objPlot)

#            if ROI != 'Please Select':
#                array_ROI_MR_Signals = np.array(self.signalData[ROI], dtype='float')
#                objPlot.plot(arrayTimes, array_ROI_MR_Signals, 'b.-', label= ROI)
                
#                self.setUpLegendBox(objPlot)
                
#                # Refresh canvas
#                self.canvas.draw()
#            else:
#                # Draw a blank graph on the canvas
#                self.canvas.draw

#        except Exception as e:
#                print('Error in function plotMRSignals when an event associated with ' + str(nameCallingFunction) + ' is fired : ROI=' + ROI + ' AIF = ' + AIF + ' : ' + str(e) )
#                logger.error('Error in function plotMRSignals when an event associated with ' + str(nameCallingFunction) + ' is fired : ROI=' + ROI + ' AIF = ' + AIF + ' : ' + str(e) )
            
        
def setUpPlot(figure):
        """
        This function draws the matplotlib plot on the GUI
        for the display of the MR signal/time curves.
        """
        try:
            logger.info('Function setUpPlot called.')
            figure.clear()
            figure.set_visible(True)
        
            objSubPlot = figure.add_subplot(111)

            # Get the optimum label size for the screen resolution.
            #tickLabelSize, xyAxisLabelSize, titleSize = \
            #    self.DetermineTextSize()

            tickLabelSize = 16
            xyAxisLabelSize = 18
            titleSize = 24

            # Set size of the x,y axis tick labels
            objSubPlot.tick_params(axis='both', 
                                   which='major', 
                                   labelsize=tickLabelSize)

            objSubPlot.set_xlabel('Time (mins)',   fontsize=xyAxisLabelSize)
            objSubPlot.set_ylabel('signal', fontsize=xyAxisLabelSize)
            objSubPlot.set_title('Time Curves', fontsize=titleSize, pad=25)
            objSubPlot.grid()

            return objSubPlot

        except Exception as e:
                print('Error in function setUpPlot: ' + str(e))
                logger.error('Error in function setUpPlot: ' + str(e))


    #def setUpLegendBox(self, objPlot):
    #    """
    #    This function draws the legend box holding the key
    #    to the MR signal/time curves on the plot.
    #    """
    #    logger.info('Function setUpLegendBox called.')
    #    chartBox = objPlot.get_position()
    #    objPlot.set_position([chartBox.x0*1.1, chartBox.y0, 
    #                          chartBox.width*0.9, chartBox.height])
    #    objPlot.legend(loc='upper center', 
    #                   bbox_to_anchor=(0.9, 1.0), 
    #                   shadow=True, ncol=1, fontsize='x-large')    

    #def GetScreenResolution(self):
    #    """Determines the screen resolution of the device 
    #    running this software.
        
    #    Returns
    #    -------
    #        Returns the width & height of the device screen in pixels.
    #    """
    #    try:
    #        width, height = pyautogui.size()
    #        logger.info('Function GetScreenResolution called. Screen width = {}, height = {}.'.format(width, height))
    #        return width, height
    #    except Exception as e:
    #        print('Error in function GetScreenResolution: ' + str(e) )
    #        logger.error('Error in function GetScreenResolution: ' + str(e) )
        

    #def DetermineTextSize(self):
    #    """Determines the optimum size for the title & labels on the 
    #       matplotlib graph from the screen resolution.
           
    #       Returns
    #       -------
    #          tick label size, xy axis label size & title size
    #       """
    #    try:
    #        logger.info('Function DetermineTextSize called.')
    #        width, _ = self.GetScreenResolution()
            
    #        if width == 1920: #Desktop
    #            tickLabelSize = 12
    #            xyAxisLabelSize = 14
    #            titleSize = 20
    #        elif width == 2560: #Laptop
    #            tickLabelSize = 16
    #            xyAxisLabelSize = 18
    #            titleSize = 24
    #        else:
    #            tickLabelSize = 12
    #            xyAxisLabelSize = 14
    #            titleSize = 20

    #        return tickLabelSize, xyAxisLabelSize, titleSize
    #    except Exception as e:
    #        print('Error in function DetermineTextSize: ' + str(e) )
    #        logger.error('Error in function DetermineTextSize: ' + str(e) )