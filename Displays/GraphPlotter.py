from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import logging
logger = logging.getLogger(__name__)


class NavigationToolbar(NavigationToolbar):
    """
    Removes unwanted default buttons in the Navigation Toolbar by creating
    a subclass of the NavigationToolbar class from from 
    matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    that only defines the desired buttons
    """
    toolitems = [t for t in NavigationToolbar.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]


class PlotGraph:
    """Plots an x,y graph"""
    def __init__(self, parent, xValues, yValues, xLabel, yLabel,  title=""):
        try:
            self.xValues = xValues
            self.yValues = yValues
            self.xLabel = xLabel
            self.yLabel = yLabel
            self.title = title

            self.figure = plt.figure(figsize=(3, 3), dpi=75)
            self.setUpSubPlot()
            # this is the Canvas Widget that displays the `figure`
            # it takes the `figure` instance as a parameter 
            # to its __init__ function
            self.canvas = FigureCanvas(self.figure)
            # this is the Navigation widget
            # it takes the Canvas widget as a parent
            self.toolbar = NavigationToolbar( self.canvas,  parent)

        except Exception as e:
            print('Error in class PlotGraph.__init__: ' + str(e))
            logger.error('Error in class PlotGraph.__init__: ' + str(e)) 


    def getGraphCanvas(self):
        return self.canvas


    def getGraphToolBar(self):
        return self.toolbar


    def setUpSubPlot(self):
        """
        This function draws the matplotlib plot on the GUI
        for the display of the MR signal/time curves.
        """
        try:
            logger.info('Function PlotGraph.setUpPlot called.')
        
            self.subPlot = self.figure.add_subplot(111)

            tickLabelSize = 4
            xyAxisLabelSize = 4
            titleSize = 9

            # Set size of the x,y axis tick labels
            self.subPlot.tick_params(axis='both', 
                                   which='major', 
                                   labelsize=tickLabelSize)

            self.subPlot.set_xlabel(self.xLabel, fontsize=xyAxisLabelSize)
            self.subPlot.set_ylabel(self.yLabel, fontsize=xyAxisLabelSize)
            self.subPlot.set_title(self.title, fontsize=titleSize)
            self.subPlot.grid()

            self.subPlot.plot(self.xValues, self.yValues, 'r.-', label= self.title)

        except Exception as e:
                print('Error in function PlotGraph.setUpPlot: ' + str(e))
                logger.error('Error in function PlotGraph.setUpPlot: ' + str(e))


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








