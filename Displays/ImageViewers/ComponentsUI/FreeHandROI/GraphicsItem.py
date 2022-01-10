"""
This class allows a DICOM image in the form of a pixel array to be displayed
on a GraphicsScene object.

It also provides functionality for the creation and erasing of an ROI, 
which is coloured red:

1. A boundary may be drawn around the RIO.  If the boundary is not closed, 
a straight line is drawn between the start and end points.  Then the area
enclosed by this boundary in infilled with red.

2. An ROI may be painted onto the image. 

3. Part of all of an RIO may be erased. 
"""
from PyQt5.QtCore import (QRectF, QRect, QPoint, Qt)
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import (QPainter, QPixmap, QColor, QImage, QCursor, qRgb)
from PyQt5.QtWidgets import  QGraphicsObject, QApplication, QMenu, QAction
import numpy as np
from scipy.stats import iqr
from numpy import nanmin, nanmax
from matplotlib.path import Path as MplPath
import sys
from .HelperFunctions import *
from .Resources import * 
np.set_printoptions(threshold=sys.maxsize)
import logging
logger = logging.getLogger(__name__)

__version__ = '1.0'
__author__ = 'Steve Shillitoe'
#October/November 2020


class GraphicsItem(QGraphicsObject):
    #sub classing QGraphicsObject rather than more logical QGraphicsItem
    #because QGraphicsObject can emit signals but QGraphicsItem cannot
    sigMouseHovered = QtCore.Signal(bool)
    sigGetDetailsROI = QtCore.Signal()
    sigRecalculateMeanROI = QtCore.Signal()
    sigRightMouseDrag = QtCore.Signal(float, float)
    sigZoomIn = QtCore.Signal()
    sigZoomOut = QtCore.Signal()
     

    def __init__(self, linkToGraphicsView): 
        """
        Instanciates a GraphicsItem object and initialises its properties.
        """
        super(GraphicsItem, self).__init__()
        self.linkToGraphicsView = linkToGraphicsView
        self.last_x, self.last_y = None, None
        self.start_x = None
        self.start_y = None
        self.pathCoordsList = []
        self.setAcceptHoverEvents(True)
        self.listROICoords = None
        self.xMouseCoord  = None
        self.yMouseCoord  = None
        self.pixelValue = None
        self.mouseMoved = False
        self.mask = None


    def setImage(self, pixelArray, roi, path):
        """
        Displays the image with it's ROI if it has one in the GraphicsItem object.

        The image's pixel array is transformed into a PyQt QPixmap for display 
        in the GraphicsItem object. 

        Input arguments
        ***************
        pixelArray - the image's pixel array
        roi - pixel array of the ROI on the image
        path - file path to the image file
        """
        logger.info("GraphicsItem.setImage called")
        self.origQImage = None
        self.qImage = None
        self.mask = None
        self.pixelArray = pixelArray
        if path is not None:
            minValue, maxValue = readLevels(path, self.pixelArray)
        else:
            minValue, maxValue = self.__quickMinMax(self.pixelArray)
        self.contrast = maxValue - minValue
        self.intensity = minValue + (maxValue - minValue)/2
        imgData, alpha = makeARGB(data=self.pixelArray, levels=[minValue, maxValue])
        self.origQImage = makeQImage(imgData, alpha)
        self.qImage = makeQImage(imgData, alpha)
        if roi is not None:
            #add roi to pixel map
            self.addROItoImage(roi)
            self.mask = roi
        #The contents of self.pixMap are displayed in this graphics item 
        #in the paint event
        self.pixMap = QPixmap.fromImage(self.qImage)
        self.width = float(self.pixMap.width()) 
        self.height = float(self.pixMap.height())
        #Calling update() causes the paint event to execute
        self.update()


    def __repr__(self):
        """Represents this class's objects as a string"""
        return '{}'.format(
           self.__class__.__name__)


    def updateImageLevels(self, intensity, contrast, roi):
        """
        Applies new intensity and contrast values to the image.

        A new QPixmap object is formed from the pixel array with the
        new contrast & intensity values.

        Input arguments
        ***************
        intensity - integer representing the image intensity value
        contrast - integer representing the image contrast value
        roi - pixel array of the ROI on the image
        """
        logger.info("FreeHandROI.GraphicsItem.updateImageLevels called")
        try:
            minValue = intensity - (contrast/2)
            maxValue = contrast + minValue
            imgData, alpha = makeARGB(data=self.pixelArray, levels=[minValue, maxValue])
            self.qImage = makeQImage(imgData, alpha)
            self.pixMap = QPixmap.fromImage(self.qImage)
            #Need to reapply mask
            if roi is not None and roi.any():
                self.reloadMask(roi)
            #repaint the image with the new contrast & intensity values. 
            self.update()
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.updateImageLevels: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.updateImageLevels: ' + str(e))


    def paint(self, painter, option, widget):
        """Built in PyQt function used to render the DICOM image"""
        logger.info("FreeHandROI.GraphicsItem.paint called")
        try:
            painter.setOpacity(1)
            painter.drawPixmap(0,0, self.width, self.height, self.pixMap)
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.paint: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.paint: ' + str(e))
        

    def boundingRect(self): 
        """Built in PyQt function used to render the DICOM image"""
        return QRectF(0,0,self.width, self.height)


    def __quickMinMax(self, data):
        """
        Estimate the min/max values of *data* by subsampling.
        """
        logger.info("FreeHandROI.GraphicsItem.__quickMinMax called")
        try:
            while data.size > 1e6:
                ax = np.argmax(data.shape)
                sl = [slice(None)] * data.ndim
                sl[ax] = slice(None, None, 2)
                data = data[sl]
            return nanmin(data), nanmax(data)
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.__quickMinMax: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.__quickMinMax: ' + str(e))


    def hoverEnterEvent(self, event):
        """
        Built in PyQt function that is executed when the cursor enters the 
        GraphicItem object. 
        
        Here it is used to set the cursor icon according
        to ROI drawing function selected: draw, paint, zoom or erase.
        """
        logger.info("FreeHandROI.GraphicsItem.hoverEnterEvent called")
        try:
            if self.linkToGraphicsView.drawEnabled:
                pm = QPixmap(PEN_CURSOR)
                cursor = QCursor(pm, hotX=0, hotY=30)
                QApplication.setOverrideCursor(cursor)

            if self.linkToGraphicsView.eraseEnabled:
                pm = QPixmap(ERASER_CURSOR)
                cursor = QCursor(pm, hotX=0, hotY=30)
                QApplication.setOverrideCursor(cursor)

            if self.linkToGraphicsView.paintEnabled:
                pm = QPixmap(BRUSH_CURSOR)
                cursor = QCursor(pm, hotX=0, hotY=30)
                QApplication.setOverrideCursor(cursor)

            if self.linkToGraphicsView.zoomEnabled:
                pm = QPixmap(MAGNIFYING_GLASS_CURSOR)
                cursor = QCursor(pm, hotX=0, hotY=30)
                QApplication.setOverrideCursor(cursor)
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.hoverEnterEvent: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.hoverEnterEvent: ' + str(e))


    def hoverLeaveEvent(self, event):
        """
        Built in PyQt function that is executed when the cursor leaves the 
        GraphicItem object. 

        Restores the mouse cursor from that set in hoverEnterEvent 
        to the default arrow.
        """
        logger.info("FreeHandROI.GraphicsItem.hoverLeaveEvent called")
        try:
            QApplication.restoreOverrideCursor()
            self.sigMouseHovered.emit(False)
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.hoverEnterEvent: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.hoverEnterEvent: ' + str(e))


    def hoverMoveEvent(self, event):
        """
        Built in PyQt function that is executed as the cursor hovers over the 
        GraphicItem object. 

        Determines the x,y coordinates of the mouse pointer and value of the pixel
        under it's tip.  When these values change the sigMouseHovered signal is 
        emitted to alert the module hosting the GraphicsView widget.
        """
        logger.info("FreeHandROI.GraphicsItem.hoverMoveEvent called")
        try:
            self.xMouseCoord = int(event.pos().x()) #columns
            self.yMouseCoord = int(event.pos().y()) #rows
            maxRow, maxCol = self.pixelArray.shape
            if self.yMouseCoord < maxRow and self.xMouseCoord < maxCol:
                #only get pixel value when mouse pointer is over the image
                self.pixelValue = self.pixelArray[self.yMouseCoord, self.xMouseCoord]
                self.sigMouseHovered.emit(True)
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.hoverMoveEvent when xMouseCoord={}, yMouseCoord={}: '.format(self.xMouseCoord, self.yMouseCoord) + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.hoverMoveEvent: ' + str(e))
       

    def drawROIBoundary(self):
        """
        As the mouse is moved over the image,
       
        1. The red channel of the 
        pixel under the cursor tip is set to 255, making it appear red.

        2. The coordinates of each pixel the mouse cursor moves over
        is added to a list. 
        """
        if self.last_x is None: # First draw event.
            self.last_x = self.xMouseCoord
            self.last_y = self.yMouseCoord
            self.start_x = self.xMouseCoord
            self.start_y = self.yMouseCoord
            return #  Ignore the first time.
        self.setPixelToRed(self.xMouseCoord, self.yMouseCoord)
        
        #Update the current mouse pointer position
        #These values are used to close the ROI
        self.last_x = self.xMouseCoord
        self.last_y = self.yMouseCoord
        #Do not add duplicates to the list
        if [self.last_x, self.last_y] not in self.pathCoordsList:
            self.pathCoordsList.append([self.last_x, self.last_y])
        self.mouseMoved = True


    def mouseMoveEvent(self, event):
        """
        Built in PyQt function that is executed when a mouse button is pressed 
        & the cursor is moved over the GraphicsItem object.

        If the left mouse button is pressed, if any of the following functions 
        are selected they are performed: draw a boundary around the RIO, paint the ROI 
        & erase the ROI.

        If the right mouse button is pressed, the sigRightMouseDrag signal is emitted
        with the distance moved in the x & y directions. This is used to adjust image 
        levels.
        """
        logger.info("FreeHandROI.GraphicsItem.mouseMoveEvent called")
        try:
            buttons = event.buttons()
            if buttons == Qt.LeftButton:
                self.xMouseCoord = int(event.pos().x())
                self.yMouseCoord = int(event.pos().y())
                
                if self.linkToGraphicsView.drawEnabled:
                    self.drawROIBoundary()

                if self.linkToGraphicsView.eraseEnabled:
                    self.eraseROI()

                if self.linkToGraphicsView.paintEnabled:
                    self.paintROI()

            elif buttons == Qt.RightButton:
                delta = event.screenPos() - event.lastScreenPos()
                deltaY = delta.y()
                deltaX =  delta.x()
                self.sigRightMouseDrag.emit(deltaX, deltaY)
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.mouseMoveEvent: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.mouseMoveEvent: ' + str(e))


    def addROIBoundaryToMask(self):
        """
        The ROI is represented by True values in a boolean array that has the same
        shape as it's image.  This function ensures that the boundary drawn around
        the RIO is included in the mask. 
        """
        for coords in self.pathCoordsList:
            cols = coords[0]  #x
            rows = coords[1]  #y
            self.mask[rows, cols] = True


    def closeAndFillROI(self):
        """
        Creates the mask corresponding to the RIO and sets the pixels within the RIO to red.

        If the boundary drawn around a ROI is not closed, this function closes it 
        with a straight line connecting the start and end points of the line. 
        Then a mask is created from the coordinates of the pixels on the this boundary.
        The mask is a boolean array with the same shape as the image, in which elements
        corresponding to the RIO are True and those outside the RIO are False. 

        Pixels within the RIO then have only their red channel set to 255, to 
        make them appear red but still allowing the image to be visible.
        """
        if  (self.last_x != None and self.start_x != None 
                and self.last_y != None and self.start_y != None):
            self.createMaskFromDrawnROI(self.pathCoordsList)
            self.addROIBoundaryToMask()
            #store mask
            self.sigGetDetailsROI.emit()
            self.linkToGraphicsView.dictROIs.addMask(self.mask)

            self.sigRecalculateMeanROI.emit()
            
            self.listROICoords = self.getListRoiInnerPoints(self.mask)
            self.fillFreeHandRoi()
            self.update()
            self.start_x = None 
            self.start_y = None
            self.last_x = None
            self.last_y = None
            self.pathCoordsList = []
            self.mouseMoved = False


    def mouseReleaseEvent(self, event):
        """
        Built in PyQt function that is executed when the mouse button is released.

        If the left mouse button is released, the draw RIO function was selected 
        and the mouse was moved over the image immediately prior to releasing 
        the left mouse button, then the ROI is closed if necessary and coloured
        red.


        If the left mouse button is released, the draw RIO function was selected 
        and the mouse was not moved over the image immediately prior to releasing 
        the left mouse button, then a single pixel is coloured red and added to the
        existing ROI on that image or a new ROI is created.


        If the left mouse button is released and the paint RIO function was selected
        then one or more contiguous pixels, depending on the brush size selected, are coloured red
        and added to the existing RIO on that image or a new RIO is created.


        If the left mouse button is released and the erase RIO function was selected
        then one or more contiguous pixels, depending on the eraser size selected, are returned
        to their original colour and removed from the existing RIO on that image.
        """
        logger.info("FreeHandROI.GraphicsItem.mouseReleaseEvent called")
        try:
            #Get the coordinates of the cursor
            self.xMouseCoord = int(event.pos().x())
            self.yMouseCoord = int(event.pos().y())
            button = event.button()
            if (button == Qt.LeftButton):
                if self.linkToGraphicsView.drawEnabled:
                    if self.mouseMoved:
                        self.closeAndFillROI()
                    else:
                        #The mouse was not moved, so a pixel was clicked on
                        if self.mask is not None:
                            if self.mask[self.yMouseCoord, self.xMouseCoord] == True:
                                pass
                                #mask already exists at this pixel, 
                                #so do nothing
                            else:
                                #update mask
                                self.setPixelToRed(self.xMouseCoord, self.yMouseCoord)
                                self.mask[self.yMouseCoord, self.xMouseCoord] = True
                                #store mask
                                self.sigGetDetailsROI.emit()
                                self.linkToGraphicsView.dictROIs.addMask(self.mask)
                                self.sigRecalculateMeanROI.emit()
                        else:
                            self.createBlankMask() #create a new boolean mask with all values False
                            self.setPixelToRed(self.xMouseCoord, self.yMouseCoord)
                            self.mask[self.yMouseCoord, self.xMouseCoord] = True
                            #store mask
                            self.sigGetDetailsROI.emit()
                            self.linkToGraphicsView.dictROIs.addMask(self.mask)
                            self.sigRecalculateMeanROI.emit()

                if self.linkToGraphicsView.eraseEnabled:
                    self.eraseROI()
                        
                if self.linkToGraphicsView.paintEnabled:
                    self.paintROI()
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.mouseReleaseEvent: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.mouseReleaseEvent: ' + str(e))


    def paintROI(self):
        """
        Depending on the brush size selected, this function paints 
        one or more contiguous pixels red and adds them to the 
        existing RIO on the image; i.e., in the mask it sets the
        corresponding pixel(s) to True.
        If there is no existing RIO on the image, then a blank mask is created first.  
        A blank mask is a boolean array with all its elements set to False 
        and that has the same shape as the image. 
        """
        if self.mask is None:
            self.createBlankMask()
            
        if self.linkToGraphicsView.pixelSquareSize == 1:
            #indices reversed for setting mask values to
            #fit with the numpy [rows, columns] format
            self.mask[self.yMouseCoord, self.xMouseCoord] = True
            self.setPixelToRed(self.xMouseCoord, self.yMouseCoord)
        else:
            increment = (self.linkToGraphicsView.pixelSquareSize - 1)/2
            lowX = int(self.xMouseCoord - increment)
            highX = int(self.xMouseCoord + increment)
            lowY = int(self.yMouseCoord - increment)
            highY = int(self.yMouseCoord + increment)
            
            for x in range(lowX, highX+1, 1):
                for y in range(lowY, highY+1, 1):
                    if x > -1 and  y > -1:
                        #indices reversed for setting mask values to
                        #fit with the numpy [rows, columns] format
                        self.mask[y, x] = True
                        self.setPixelToRed(x, y)    
        self.update()
        self.sigGetDetailsROI.emit()
        self.linkToGraphicsView.dictROIs.addMask(self.mask)
        self.sigRecalculateMeanROI.emit()


    def eraseROI(self):
        """
        Depending on the brush size selected, this function 
        returns one or more contiguous pixels to their original colour 
        and removes them from the RIO; i.e., in the mask it sets the
        corresponding pixel(s) to False.
        """
        #Make sure we are erasing the RIO on the latest version of the mask
        self.mask = self.linkToGraphicsView.dictROIs.getUpdatedMask()
        if self.mask is not None:
            if self.linkToGraphicsView.pixelSquareSize == 1:
                self.resetPixelToOriginalValue(self.xMouseCoord, self.yMouseCoord)
                #indices reversed for setting mask values to
                #fit with the numpy [rows, columns] format
                self.mask[self.yMouseCoord, self.xMouseCoord] = False
            else:
                increment = (self.linkToGraphicsView.pixelSquareSize - 1)/2
                lowX = int(self.xMouseCoord - increment)
                highX = int(self.xMouseCoord + increment)
                lowY = int(self.yMouseCoord - increment)
                highY = int(self.yMouseCoord + increment)
            
                for x in range(lowX, highX+1, 1):
                    for y in range(lowY, highY+1, 1):
                        if x > -1 and  y > -1:
                            self.resetPixelToOriginalValue(x, y)
                            #indices reversed for setting mask values to
                            #fit with the numpy [rows, columns] format
                            self.mask[y, x] = False
                            
            self.sigGetDetailsROI.emit()
            #update existing mask
            self.linkToGraphicsView.dictROIs.replaceMask(self.mask)
            self.sigRecalculateMeanROI.emit()


    def resetPixelToOriginalValue(self, x, y):
        """
        This function is used by the eraseRIO function to return
        a pixel in the RIO to its original colour. 

        The RGB values are obtained from a copy of the image and
        the pixel at x,y is set to these values. A new QPixmap of 
        the image is then created and the image repainted.
        """
        logger.info("FreeHandROI.GraphicsItem.resetPixelToOriginalValue called")
        try:
            pixelColour = self.origQImage.pixel(x, y) 
            pixelRGB =  QColor(pixelColour).getRgb()
            redVal = pixelRGB[0]
            greenVal = pixelRGB[1]
            blueVal = pixelRGB[2]
            value = qRgb(redVal, greenVal, blueVal)
            self.qImage.setPixel(x, y, value)
            #convert QImage to QPixmap to be able to update image
            self.pixMap = QPixmap.fromImage(self.qImage)
            #repaint image by updating it
            self.update()
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.resetPixelToOriginalValue: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.resetPixelToOriginalValue: ' + str(e))
    

    def setPixelToRed(self, x, y):
        """
        This function sets the red channel of the pixel at x,y to 255; thus,
        making it appear red. 
        """
        logger.info("FreeHandROI.GraphicsItem.setPixelToRed called")
        try:
            pixelColour = self.qImage.pixel(x, y) 
            pixelRGB =  QColor(pixelColour).getRgb()
            redVal = pixelRGB[0]
            greenVal = pixelRGB[1]
            blueVal = pixelRGB[2]
            if greenVal > 240 and blueVal > 240:
                #This pixel would be white if red channel set to 255
                #so set the green and blue channels to 240
                greenVal = blueVal = 240
            value = qRgb(255, greenVal, blueVal)
            self.qImage.setPixel(x, y, value)
            #convert QImage to QPixmap to be able to update image
            #with filled ROI
            self.pixMap = QPixmap.fromImage(self.qImage)
            #repaint image
            self.update()
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.setPixelToRed: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.setPixelToRed: ' + str(e))


    def reloadMask(self, mask):
        """
        Redisplays the ROI represented by mask on the image.

        This function makes a list of the coordinates of the elements
        in the input argument mask that have the value True and therefore correspond
        to the RIO. Then the pixels in the image, within the RIO, have 
        their Red channel set to 255, to make them appear red. 
        """
        logger.info("FreeHandROI.GraphicsItem.reloadMask called")
        try:
            self.listROICoords = self.getListRoiInnerPoints(mask)
            self.fillFreeHandRoi()
            self.listROICoords = []
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.reloadMask: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.reloadMask: ' + str(e))


    def fillFreeHandRoi(self):
        """
        Sets the Red channel to 255 of the pixels within the RIO.  
        This makes them appear red.
        """
        logger.info("FreeHandROI.GraphicsItem.fillFreeHandRoi called")
        try:
            #self.listROICoords is a list of the coordinates of the pixels
            #within the RIO
            if self.listROICoords is not None:
                for coords in self.listROICoords:
                    x = coords[0]
                    y = coords[1]
                    self.setPixelToRed(x, y)
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.fillFreeHandRoi: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.fillFreeHandRoi: ' + str(e))


    def addROItoImage(self, roi):
        """
        This function is used to add an existing ROI to an image 
        before it is displayed for the first time in the GraphicsItem object.

        rio - boolean array containing elements corresponding to the ROI; i.e.,
            their value is True. 
        """
        logger.info("FreeHandROI.GraphicsItem.addROItoImage called")
        try:
            listROICoords = self.getListRoiInnerPoints(roi)
            if listROICoords is not None:
                for coords in listROICoords:
                    x = coords[0]
                    y = coords[1]
                    pixelColour = self.qImage.pixel(x, y) 
                    pixelRGB =  QColor(pixelColour).getRgb()
                    redVal = pixelRGB[0]
                    greenVal = pixelRGB[1]
                    blueVal = pixelRGB[2]
                    if greenVal > 240 and blueVal > 240:
                        #This pixel would be white if red channel set to 255
                        #so set the green and blue channels to 240
                        greenVal = blueVal = 240
                    value = qRgb(255, greenVal, blueVal)
                    self.qImage.setPixel(x, y, value)
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.addROItoImage: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.addROItoImage: ' + str(e))


    def getMaskData(self):
        """
        This function returns the mask (boolean array) associated with 
        the GraphicsItem object. 
        """
        logger.info("FreeHandROI.GraphicsItem.getMaskData called")
        return self.mask


    def getListRoiInnerPoints(self, mask):
        """
        This function returns a list of the coordinates 
        of the elements in the mask whose values are True. 
       
        Input argument
        ***************
        mask - a boolean array the same size as the image. 
            Elements in the mask whose value is True correspond  
            to the pixels in the ROI drawn on the image.
        """
        logger.info("FreeHandROI.GraphicsItem.getListRoiInnerPoints called")
        try:
            if mask is not None:
                roi = np.where(mask == True)
                return list(zip(roi[1], roi[0]))
            else:
                return None
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.getListRoiInnerPoints: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.getListRoiInnerPoints: ' + str(e))


    def createBlankMask(self):
        """
        Creates a boolean array with the same shape as the image's
        pixel array. All its elements are set to False. This boolean array
        is assigned to the class property self.mask.

        This function is used by the paintROI function and when no ROI exists
        and an ROI is drawn on just one pixel.
        """
        logger.info("FreeHandROI.GraphicsItem.createBlankMask called")
        rows, cols = np.shape(self.pixelArray)
        self.mask = np.full((rows, cols), False, dtype=bool)


    def createMaskFromDrawnROI(self, roiBoundaryCoords):
        """
        Using the coordinates of the points on the boundary of a drawn RIO,
        this function creates a mask. 
        The mask is a boolean array with the same shape as
        the image. 
        Elements in the mask with the value True represent the ROI. 
        Elements in the mask outside the RIO have the value False. 
        """
        logger.info("FreeHandROI.GraphicsItem.createMaskFromDrawnROI called")
        try:
            self.mask = None
            #1. Create a list called points
            # of x,y coordinates for each element 
            #in self.pixelArray, the pixel array of the DICOM image
            nx, ny = np.shape(self.pixelArray)
            x, y = np.meshgrid(np.arange(nx), np.arange(ny))
            points = list(zip(x.flatten(),y.flatten()))

            #2. Convert the ROI boundary coordinates into a path object
            roiPath = MplPath(roiBoundaryCoords, closed=True)

            #3.Create a boolean array representing the original pixel array
            #with all elements set to False except those falling within the
            #ROI that are set to True.  
            #Setting radius=0.0 does not include the drawn boundary in the ROI
            self.mask = roiPath.contains_points(points, radius=0.0).reshape((ny, nx))   
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.createMaskFromDrawnROI: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.createMaskFromDrawnROI: ' + str(e))
            

    def mousePressEvent(self, event):
        """
        Built in PyQt function that is executed when the mouse button is pressed.

        When the left mouse button is pressed, the sigZoomIn signal is emitted to 
        communicate this to the host GraphicsView widget, that then zooms in on 
        the image.

        When the right mouse button is pressed, the sigZoomOut signal is emitted to 
        communicate this to the host GraphicsView widget, that then zooms out from 
        the image.
        """
        logger.info("FreeHandROI.GraphicsItem.mousePressEvent called")
        try:
            pass
            button = event.button()
            if (button == Qt.LeftButton):
              self.sigZoomIn.emit()
            elif (button == Qt.RightButton): 
              self.sigZoomOut.emit()
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.mousePressEvent: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.mousePressEvent: ' + str(e))




    