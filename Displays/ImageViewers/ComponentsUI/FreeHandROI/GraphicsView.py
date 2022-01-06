"""
The GraphicsView class  is derived from the PyQt QGraphicsView class 
and it visualizes the contents of a QGraphicsScene in a scrollable viewport.

A QGraphicsScene object serves as a container for QGraphicsItem 
& QGraphicsObject objects.

QGraphicsObject is the base class for all graphics items that 
require signals, slots and properties.  The GraphicItem class 
is derived from the  QGraphicsObject class. 
"""

from PyQt5.QtCore import QRectF, Qt,  QCoreApplication
from PyQt5 import QtCore 
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QMenu, QMessageBox,
                            QAction, QActionGroup, QApplication )



from PyQt5.QtGui import QPixmap, QCursor, QIcon, QToolTip
from .GraphicsItem import GraphicsItem
from .ROI_Storage import ROIs 
import logging

logger = logging.getLogger(__name__)

__version__ = '1.0'
__author__ = 'Steve Shillitoe'
#October/November 2020

#Constants
ZOOM_IN = 1
ZOOM_OUT = -1


class GraphicsView(QGraphicsView):
    sigReloadImage =  QtCore.Signal()
    sigROIChanged = QtCore.Signal()
    sigNewROI = QtCore.Signal(str)
    sigUpdateZoom = QtCore.Signal(int)


    def __init__(self, numberOfImages): 
        """
        Constructs a GraphicsView object that is a viewport over 
        a QGraphicsScene object, self.scene. It also creates a data structure,
        self.dictROIs, to store ROI data.

        Input arguments
        ***************
        numberOfImages - number of images in the DICOM series. 
        Used  to set up self.dictROIs, the data structure holding ROI data
        """
        super(GraphicsView, self).__init__()
        self.scene = QGraphicsScene(self)
        self._zoom = 0 #Integer representing the zoom factor
        self.graphicsItem  = None #pointer to graphicsItem widget that displays the image
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.currentROIName = None
        self.currentImageNumber = None
        self.dictROIs = ROIs(numberOfImages, self) #data structure holding ROI data
        self.pixelSquareSizeMenu = QMenu()
        self.pixelSquareSizeMenu.hovered.connect(self._actionHovered)
        self.drawEnabled = False
        self.paintEnabled = False
        self.eraseEnabled = False
        self.zoomEnabled = False
        self.pixelSquareSize = 1
        #Following commented out to not display vertical and
        #horizontal scroll bars
        #self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.setDragMode(QGraphicsView.ScrollHandDrag)


    def __repr__(self):
        """Represents this class's objects as a string"""
        return '{}'.format(
           self.__class__.__name__)


    def setZoomEnabled(self, boolValue):
        """Sets the value of the boolean, zoomEnabled.
           When zoomEnabled is True, the user may zoom in 
           by clicking the left mouse button & zoom out by
           clicking the right mouse button. 
        """
        self.zoomEnabled = boolValue


    def setImage(self, pixelArray, mask = None, path = None):
        """
        Loads an image for display.

        A GraphicsItem object is created and added to the graphics scene
        viewed by this GraphicsView widget.  Then the image contained in
        the pixelArray is displayed in the GraphicsItem object.  The image 
        is scaled to make it fit the GraphicsView widget and the existing
        zoom level is applied to it.

        Input arguments
        ***************
        pixelArray - pixel array representing an image
        mask - pixel array represting a mask over the image
        path - file path of the image
        """
        logger.info("freeHandROI.GraphicsView.setImage called")
        try:
            if self.graphicsItem is None:
                #Create the GraphicsItem object that 
                #will be used to display all the images
                self.graphicsItem = GraphicsItem(self)
                self.scene.addItem(self.graphicsItem)
                self.graphicsItem.sigZoomIn.connect(lambda: self.zoomFromMouseClicks(ZOOM_IN))
                self.graphicsItem.sigZoomOut.connect(lambda: self.zoomFromMouseClicks(ZOOM_OUT))
            
            self.graphicsItem.setImage(pixelArray, mask, path)
            self.fitInView(self.graphicsItem, Qt.KeepAspectRatio) 
            self.reapplyZoom()
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.setImage: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.setImage: ' + str(e))


    def reapplyZoom(self):
        """
        Reapplies the zoom factor to an image. 

        When the user zooms in or out on one image,
        this function ensures that same zoom factor is applied to 
        all images in a DICOM series as the user scrolls through
        other images in the series
        """
        if self._zoom > 0:
            factor = 1.25
            totalFactor = factor**self._zoom
            self.scale(totalFactor, totalFactor)
        
          
    def zoomFromMouseClicks(self, zoomValue):
        """
        Zooms in and out on an image according to the value of zoomValue.
        
        Zoom in, when zoomValue > 0,
        zoom out, when zoomValue < 0,
        reset the image to its original size, when zoomValue = 0
        """
        if self.zoomEnabled:
           self.zoomImage(zoomValue)
    

    def zoomImage(self, zoomValue):
        """
        Scales the image according to the value of the input
        argument zoomValue.

        Zoom in, when zoomValue > 0,
        zoom out, when zoomValue < 0,
        reset the image to its original size, when zoomValue = 0
        """
        logger.info("freeHandROI.GraphicsView.zoomImage called")
        try:
            if zoomValue > 0:
                factor = 1.25
                self._zoom += 1
                #print("+self._zoom={}".format(self._zoom))
                increment = 1
            else:
                factor = 0.8
                self._zoom -= 1
                increment = -1
                #print("-self._zoom={}".format(self._zoom))
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitItemInView()
                increment = 0
            else:
                self._zoom = 0
                increment = 0
            self.sigUpdateZoom.emit(increment)
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.zoomImage: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.zoomImage: ' + str(e))


    def wheelEvent(self, event):
        """
        wheelEvent is a built-in PyQt function.  
        It is executed when the mouse wheel is rotated. 

        Input arguments
        ***************
        event - an object of the QWheelEvent class that
            contains parameters that describe a wheel event.
        """
        self.zoomImage(event.angleDelta().y())


    def fitItemInView(self):
        """
        Scales the image so that it perfectly fits the GraphicView widget.
        """
        logger.info("freeHandROI.GraphicsView.fitItemInView called")
        try:
            if self.graphicsItem is not None:
                rect = QRectF(self.graphicsItem.pixMap.rect())
                if not rect.isNull():
                    self.setSceneRect(rect)
                    unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                    self.scale(1 / unity.width(), 1 / unity.height())
                    viewrect = self.viewport().rect()
                    scenerect = self.transform().mapRect(rect)
                    factor = min(viewrect.width() / scenerect.width(),
                                    viewrect.height() / scenerect.height())
                    self.scale(factor, factor)
                    self._zoom = 0
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.fitItemInView: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.fitItemInView: ' + str(e))


    def setUpPixelSquareSizeMenu(self, event):
        """
        Creates the context menu for selecting brush/eraser size.
        """
        self.pixelSquareSizeMenu.clear()
        onePixel = QAction('One Pixel')
        onePixel.setCheckable(True)
        onePixel.setToolTip('Erase/Paint one pixel')
        threePixels = QAction('3 x 3 Pixels')
        threePixels.setCheckable(True)
        threePixels.setToolTip('Erase/Paint a 3x3 square of pixels')
        fivePixels = QAction('5 x 5 Pixels')
        fivePixels.setCheckable(True)
        fivePixels.setToolTip('Erase/Paint a 5x5 square of pixels')
        sevenPixels = QAction('7 x 7 Pixels')
        sevenPixels.setCheckable(True)
        sevenPixels.setToolTip('Erase/Paint a 7x7 square of pixels')
        ninePixels = QAction('9 x 9 Pixels')
        ninePixels.setCheckable(True)
        ninePixels.setToolTip('Erase/Paint a 9x9 square of pixels')
        elevenPixels = QAction('11 x 11 Pixels')
        elevenPixels.setCheckable(True)
        elevenPixels.setToolTip('Erase/Paint a 11x11 square of pixels')
        twentyOnePixels = QAction('21 x 21 Pixels')
        twentyOnePixels.setCheckable(True)
        twentyOnePixels.setToolTip('Erase/Paint a 21x21 square of pixels')

        #put a tick in front of a selected menu item
        if self.pixelSquareSize == 1:
            onePixel.setChecked(True)
        elif self.pixelSquareSize == 3:
            threePixels.setChecked(True)
        elif self.pixelSquareSize == 5:
            fivePixels.setChecked(True)
        elif self.pixelSquareSize == 7:
            sevenPixels.setChecked(True)
        elif self.pixelSquareSize == 9:
            ninePixels.setChecked(True)
        elif self.pixelSquareSize == 11:
            elevenPixels.setChecked(True)
        elif self.pixelSquareSize == 21:
            twentyOnePixels.setChecked(True)

        onePixel.triggered.connect(lambda: self.setPixelSquareSize(1))
        threePixels.triggered.connect(lambda:  self.setPixelSquareSize(3))
        fivePixels.triggered.connect(lambda:  self.setPixelSquareSize(5))
        sevenPixels.triggered.connect(lambda:  self.setPixelSquareSize(7))
        ninePixels.triggered.connect(lambda:  self.setPixelSquareSize(9))
        elevenPixels.triggered.connect(lambda:  self.setPixelSquareSize(11))
        twentyOnePixels.triggered.connect(lambda:  self.setPixelSquareSize(21))
        
        self.pixelSquareSizeMenu.addAction(onePixel)
        self.pixelSquareSizeMenu.addAction(threePixels)
        self.pixelSquareSizeMenu.addAction(fivePixels)
        self.pixelSquareSizeMenu.addAction(sevenPixels)
        self.pixelSquareSizeMenu.addAction(ninePixels)
        self.pixelSquareSizeMenu.addAction(elevenPixels)
        self.pixelSquareSizeMenu.addAction(twentyOnePixels)
        self.pixelSquareSizeMenu.exec_(event.globalPos())


    def setPixelSquareSize(self, pixelSquareSize):
        """
        Sets the value of the pixelSquareSize property, which
        sets the size of the side of the square of pixels that 
        represent the size of the tip of the brush or eraser. 
        E.g., if pixelSquareSize = 5, then brush/eraser size is
        a square of 25 pixels.

        Input argument
        **************
        pixelSquareSize - integer taking the values: 1, 3, 5, 7, 9, 11, 21
        """
        self.pixelSquareSize = pixelSquareSize


    def contextMenuEvent(self, event):
        """contextMenuEvent is a built in method in PyQt5 for the
        display of a context menu when the right mouse button is pressed

        Here it displays a pop-up context menu 
        allowing the user to select the brush/eraser size
        when zoom is not enabled. """
        logger.info("freeHandROI.GraphicsView.contextMenuEvent called")
        try:
            if not self.zoomEnabled:
                if self.paintEnabled or self.eraseEnabled:
                    self.setUpPixelSquareSizeMenu(event)
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.contextMenuEvent: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.contextMenuEvent: ' + str(e))
            

    def _actionHovered(self, action):
        """Allows the display of a tooltip for the menu 
        items in the brush/eraser size context menu."""
        tip = action.toolTip()
        QToolTip.showText(QCursor.pos(), tip)


    def drawROI(self, enableDraw):
        """
        Sets the values of the boolean class properties 
        in order to enable the user to draw an ROI on the image.
        """
        logger.info("freeHandROI.GraphicsView.drawROI called")
        try:
            if enableDraw:
                self.drawEnabled = True
                self.setZoomEnabled(False)
                self.eraseEnabled = False
                self.paintEnabled = False
            else:
                self.drawEnabled = False
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.drawROI: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.drawROI: ' + str(e))


    def paintROI(self, enablePaint):
        """
        Sets the values of the boolean class properties 
        in order to enable the user to paint an ROI on the image.
        """
        logger.info("freeHandROI.GraphicsView.paintROI called")
        try:
            if enablePaint:
                self.setZoomEnabled(False)
                self.eraseEnabled = False
                self.drawEnabled = False
                self.paintEnabled = True
                #default brush size to one pixel
                self.pixelSquareSize = 1
            else:
                self.paintEnabled = False
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.paintROI: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.paintROI: ' + str(e))


    def eraseROI(self, enableErase):
        """
        Sets the values of the boolean class properties 
        in order to enable the user to erase part or all 
        of an ROI on the image.
        """
        logger.info("freeHandROI.GraphicsView.eraseROI called")
        try:
            if enableErase:
                self.drawEnabled = False
                self.paintEnabled = False
                self.setZoomEnabled(False)
                self.eraseEnabled = True
                #default eraser size to one pixel
                self.pixelSquareSize = 1
            else:
                self.eraseEnabled = False
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.eraseROI: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.eraseROI: ' + str(e))
            

    def newROI(self):
        """
        Creates a new blank ROI.
        """
        logger.info("freeHandROI.GraphicsView.newROI called")
        try:
            self.sigROIChanged.emit()
            if self.dictROIs.hasRegionGotMask(self.currentROIName):
                newRegion = self.dictROIs.getNextRegionName()
                self.sigNewROI.emit(newRegion)
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("Add new ROI")
                msgBox.setText(
                    "You must add ROIs to the current region before creating a new one")
                msgBox.exec()
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.newROI: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.newROI: ' + str(e))


    def resetROI(self):
        """
        Removes the current ROI from an image.

        The ROI is removed from the data structure self.dictROIs 
        and a signal is emitted to communicate to the host subwindow
        that the image must be reloaded without the ROI that was just drawn.
        """
        logger.info("freeHandROI.GraphicsView.resetROI called")
        try:
            self.sigROIChanged.emit()
            self.dictROIs.deleteMask(self.currentROIName)
            self.sigReloadImage.emit()
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.resetROI: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.resetROI: ' + str(e))
