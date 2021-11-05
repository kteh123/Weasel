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
import DICOM.ReadDICOM_Image as ReadDICOM_Image
from time import sleep
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
    sigZoomIn = QtCore.Signal()
    sigZoomOut = QtCore.Signal()

    def __init__(self, pixelArray, roi, path, linkToGraphicsView): 
        super(GraphicsItem, self).__init__()
        logger.info("GraphicsItem initialised")
        self.pixelArray = pixelArray
        if path is not None:
            minValue, maxValue = readLevels(path, self.pixelArray)
        else:
            minValue, maxValue = self.__quickMinMax(self.pixelArray)
        self.linkToGraphicsView = linkToGraphicsView
        self.contrast = maxValue - minValue
        self.intensity = minValue + (maxValue - minValue)/2
        imgData, alpha = makeARGB(data=self.pixelArray, levels=[minValue, maxValue])
        self.origQimage = makeQImage(imgData, alpha)
        self.qimage = makeQImage(imgData, alpha)
        self.mask = None
        if roi is not None:
            #add roi to pixel map
            self.addROItoImage(roi)
            self.mask = roi
        self.pixMap = QPixmap.fromImage(self.qimage)
        self.width = float(self.pixMap.width()) 
        self.height = float(self.pixMap.height())
        self.last_x, self.last_y = None, None
        self.start_x = None
        self.start_y = None
        #self.originRectX = None
        #self.originRectY = None
        self.pathCoordsList = []
        self.prevPathCoordsList = []
        self.setAcceptHoverEvents(True)
        self.listROICoords = None
        self.xMouseCoord  = None
        self.yMouseCoord  = None
        self.pixelColour = None
        self.pixelValue = None
        self.mouseMoved = False
        self.drawEnabled = False
        self.paintEnabled = False
        self.eraseEnabled = False
        self.zoomEnabled = False
        self.pixelSquareSize = 1
        #self.setToolTip("Use the mouse wheel to zoom")


    def __repr__(self):
       return '{}'.format(
           self.__class__.__name__)


    def updateImageLevels(self, intensity, contrast, roi):
        logger.info("FreeHandROI.GraphicsItem.updateImageLevels called")
        try:
            minValue = intensity - (contrast/2)
            maxValue = contrast + minValue
            imgData, alpha = makeARGB(data=self.pixelArray, levels=[minValue, maxValue])
            self.qimage = makeQImage(imgData, alpha)
            self.pixMap = QPixmap.fromImage(self.qimage)

            #Need to reapply mask
            if roi is not None and roi.any():
                self.reloadMask(roi)

            self.update()
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.updateImageLevels: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.updateImageLevels: ' + str(e))


    def paint(self, painter, option, widget):
        logger.info("FreeHandROI.GraphicsItem.paint called")
        try:
            painter.setOpacity(1)
            painter.drawPixmap(0,0, self.width, self.height, self.pixMap)
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.paint: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.paint: ' + str(e))
        

    def boundingRect(self): 
        logger.info("FreeHandROI.GraphicsItem.boundingRect called")
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
        logger.info("FreeHandROI.GraphicsItem.hoverEnterEvent called")
        try:
            if self.drawEnabled:
                pm = QPixmap(PEN_CURSOR)
                cursor = QCursor(pm, hotX=0, hotY=30)
                QApplication.setOverrideCursor(cursor)
            if self.eraseEnabled:
                pm = QPixmap(ERASER_CURSOR)
                cursor = QCursor(pm, hotX=0, hotY=30)
                QApplication.setOverrideCursor(cursor)
            if self.paintEnabled:
                pm = QPixmap(BRUSH_CURSOR)
                cursor = QCursor(pm, hotX=0, hotY=30)
                QApplication.setOverrideCursor(cursor)
            if self.zoomEnabled:
                pm = QPixmap(MAGNIFYING_GLASS_CURSOR)
                cursor = QCursor(pm, hotX=0, hotY=30)
                QApplication.setOverrideCursor(cursor)
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.hoverEnterEvent: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.hoverEnterEvent: ' + str(e))


    def hoverLeaveEvent(self, event):
        logger.info("FreeHandROI.GraphicsItem.hoverLeaveEvent called")
        try:
            QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
            self.sigMouseHovered.emit(False)
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.hoverEnterEvent: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.hoverEnterEvent: ' + str(e))


    def hoverMoveEvent(self, event):
        logger.info("FreeHandROI.GraphicsItem.hoverMoveEvent called")
        try:
            self.xMouseCoord = int(event.pos().x())
            self.yMouseCoord = int(event.pos().y())
            self.pixelColour = self.origQimage.pixelColor(self.xMouseCoord,  self.yMouseCoord ).getRgb()[:-1]
            self.pixelValue = self.pixelArray[self.xMouseCoord, self.yMouseCoord]
            self.sigMouseHovered.emit(True)
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.hoverMoveEvent: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.hoverMoveEvent: ' + str(e))
       

    def drawROIBoundary(self):
        if self.last_x is None: # First event.
            self.last_x = self.xMouseCoord
            self.last_y = self.yMouseCoord
            self.start_x = self.xMouseCoord
            self.start_y = self.yMouseCoord
            return #  Ignore the first time.
        self.drawStraightLine(self.last_x, self.last_y, 
                              self.xMouseCoord, self.yMouseCoord)
        # Update the origin for next time.
        self.last_x = self.xMouseCoord
        self.last_y = self.yMouseCoord
        #Do not add duplicates to the list
        if [self.last_x, self.last_y] not in self.pathCoordsList:
            self.pathCoordsList.append([self.last_x, self.last_y])
        self.mouseMoved = True


    def mouseMoveEvent(self, event):
        logger.info("FreeHandROI.GraphicsItem.mouseMoveEvent called")
        try:
            buttons = event.buttons()
            if (buttons == Qt.LeftButton):
                self.xMouseCoord = int(event.pos().x())
                self.yMouseCoord = int(event.pos().y())
                
                if self.drawEnabled:
                    self.drawROIBoundary()

                if self.eraseEnabled:
                    self.eraseROI()

                if self.paintEnabled:
                    self.paintROI()

        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.mouseMoveEvent: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.mouseMoveEvent: ' + str(e))

    
    def closeAndFillROI(self):
        if  (self.last_x != None and self.start_x != None 
                and self.last_y != None and self.start_y != None):
            if int(self.last_x) == self.start_x and int(self.last_y) == self.start_y:
                #free hand drawn ROI is closed, so no further action needed
                pass
            else:
                #free hand drawn ROI is not closed, so need to draw a
                #straight line from the coordinates of its start to
                #the coordinates of its last point
                self.drawStraightLine(self.last_x, self.last_y, self.start_x, self.start_y)
        
            self.prevPathCoordsList = self.pathCoordsList
            self.createMaskFromDrawnROI(self.pathCoordsList)
            #store mask
            self.sigGetDetailsROI.emit()
            self.linkToGraphicsView.dictROIs.addMask(self.mask)
            self.sigRecalculateMeanROI.emit()
            
            self.listROICoords = self.getListRoiInnerPoints(self.mask)
            self.fillFreeHandRoi()
            self.start_x = None 
            self.start_y = None
            self.last_x = None
            self.last_y = None
            self.pathCoordsList = []
            self.mouseMoved = False

    def mouseReleaseEvent(self, event):
        logger.info("FreeHandROI.GraphicsItem.mouseReleaseEvent called")
        try:
            #Get the coordinates of the cursor
            self.xMouseCoord = int(event.pos().x())
            self.yMouseCoord = int(event.pos().y())
            button = event.button()
            if (button == Qt.LeftButton):
                if self.drawEnabled:
                    if self.mouseMoved:
                        self.closeAndFillROI()
                    else:
                        #The mouse was not moved, so a pixel was clicked on
                        if self.mask is not None:
                            if self.mask[self.xMouseCoord, self.yMouseCoord] == True:
                                pass
                                #mask already exists at this pixel, 
                                #so do nothing
                            else:
                                #update mask
                                self.setPixelToRed(self.xMouseCoord, self.yMouseCoord)
                                self.mask[self.xMouseCoord, self.yMouseCoord] = True
                                #store mask
                                self.sigGetDetailsROI.emit()
                                self.linkToGraphicsView.dictROIs.addMask(self.mask)
                                self.sigRecalculateMeanROI.emit()
                        else:
                            self.createBlankMask() #create a new boolean mask with all values False
                            self.setPixelToRed(self.xMouseCoord, self.yMouseCoord)
                            self.mask[self.xMouseCoord, self.yMouseCoord] = True
                            #store mask
                            self.sigGetDetailsROI.emit()
                            self.linkToGraphicsView.dictROIs.addMask(self.mask)
                            self.sigRecalculateMeanROI.emit()

                if self.eraseEnabled:
                    self.eraseROI()
                        
                if self.paintEnabled:
                    self.paintROI()
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.mouseReleaseEvent: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.mouseReleaseEvent: ' + str(e))


    def paintROI(self):
        if self.mask is None:
            self.createBlankMask()

        if self.pixelSquareSize == 1:
            self.mask[self.xMouseCoord, self.yMouseCoord] = True
            self.setPixelToRed(self.xMouseCoord, self.yMouseCoord)
        else:
            increment = (self.pixelSquareSize - 1)/2
            lowX = int(self.xMouseCoord - increment)
            highX = int(self.xMouseCoord + increment)
            lowY = int(self.yMouseCoord - increment)
            highY = int(self.yMouseCoord + increment)
            
            for x in range(lowX, highX+1, 1):
                for y in range(lowY, highY+1, 1):
                    if x > -1 and  y > -1:
                        self.mask[x, y] = True
                        self.setPixelToRed(x, y)    
        self.update()
        self.sigGetDetailsROI.emit()
        self.linkToGraphicsView.dictROIs.addMask(self.mask)
        self.sigRecalculateMeanROI.emit()


    def eraseROI(self):
        #erase mask at this mouse pointer position
        #and set pixel back to original value
        if self.mask is not None:
            if self.pixelSquareSize == 1:
                self.resetPixel(self.xMouseCoord, self.yMouseCoord)
                self.mask[self.xMouseCoord, self.yMouseCoord] = False
            else:
                increment = (self.pixelSquareSize - 1)/2
                lowX = int(self.xMouseCoord - increment)
                highX = int(self.xMouseCoord + increment)
                lowY = int(self.yMouseCoord - increment)
                highY = int(self.yMouseCoord + increment)
            
                for x in range(lowX, highX+1, 1):
                    for y in range(lowY, highY+1, 1):
                        if x > -1 and  y > -1:
                            self.resetPixel(x, y)
                            self.mask[x, y] = False
                            
            self.sigGetDetailsROI.emit()
            #update existing mask
            self.linkToGraphicsView.dictROIs.replaceMask(self.mask)
            self.sigRecalculateMeanROI.emit()


    def resetPixel(self, x, y):
        logger.info("FreeHandROI.GraphicsItem.resetPixel called")
        try:
            pixelColour = self.origQimage.pixel(x, y) 
            pixelRGB =  QColor(pixelColour).getRgb()
            redVal = pixelRGB[0]
            greenVal = pixelRGB[1]
            blueVal = pixelRGB[2]
            value = qRgb(redVal, greenVal, blueVal)
            self.qimage.setPixel(x, y, value)
            #convert QImage to QPixmap to be able to update image
            self.pixMap = QPixmap.fromImage(self.qimage)
            self.update()
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.resetPixel: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.resetPixel: ' + str(e))
    

    def setPixelToRed(self, x, y):
        logger.info("FreeHandROI.GraphicsItem.setPixelToRed called")
        try:
            pixelColour = self.qimage.pixel(x, y) 
            pixelRGB =  QColor(pixelColour).getRgb()
            redVal = pixelRGB[0]
            greenVal = pixelRGB[1]
            blueVal = pixelRGB[2]
            if greenVal == 255 and blueVal == 255:
                #This pixel would be white if red channel set to 255
                #so set the green and blue channels to zero
                greenVal = blueVal = 0
            value = qRgb(255, greenVal, blueVal)
            self.qimage.setPixel(x, y, value)
            #convert QImage to QPixmap to be able to update image
            #with filled ROI
            self.pixMap = QPixmap.fromImage(self.qimage)
            self.update()
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.setPixelToRed: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.setPixelToRed: ' + str(e))


    def drawStraightLine(self, startX, startY, endX, endY, colour='red'):
        logger.info("FreeHandROI.GraphicsItem.drawStraightLine called")
        try:
            objPainter = QPainter(self.pixMap)
            objPen = objPainter.pen()
            objPen.setWidth(1) #1 pixel
            if colour == 'red':
                objPen.setColor(QColor("#FF0000")) #red
            else:
                objPen.setColor(QColor("#0000FF")) #blue
            objPainter.setPen(objPen)
            #self.objPainter.setRenderHint(QPainter.Antialiasing)
            objPainter.drawLine(startX, startY, endX, endY)
            objPainter.end()
            self.qimage =  self.pixMap.toImage()
            self.update()
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.drawStraightLine: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.drawStraightLine: ' + str(e))


    def reloadImage(self):
        logger.info("FreeHandROI.GraphicsItem.reloadImage called")
        try:
            self.qimage = None
            self.pixMap = None
            self.qimage = self.origQimage
            self.pixMap = QPixmap.fromImage(self.qimage)
            self.update()
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.reloadImage: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.reloadImage: ' + str(e))


    def reloadMask(self, mask):
        logger.info("FreeHandROI.GraphicsItem.reloadMask called")
        try:
            #redisplays the ROI represented by mask
            self.listROICoords = self.getListRoiInnerPoints(mask)
            self.fillFreeHandRoi()
            self.listROICoords = []
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.reloadMask: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.reloadMask: ' + str(e))


    def fillFreeHandRoi(self):
        logger.info("FreeHandROI.GraphicsItem.fillFreeHandRoi called")
        try:
            if self.listROICoords is not None:
                for coords in self.listROICoords:
                    x = coords[0]
                    y = coords[1]
                    self.setPixelToRed(x, y)
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.fillFreeHandRoi: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.fillFreeHandRoi: ' + str(e))


    def addROItoImage(self, roi):
        logger.info("FreeHandROI.GraphicsItem.addROItoImage called")
        try:
            listROICoords = self.getListRoiInnerPoints(roi)
            if listROICoords is not None:
                for coords in listROICoords:
                    x = coords[0]
                    y = coords[1]
                    pixelColour = self.qimage.pixel(x, y) 
                    pixelRGB =  QColor(pixelColour).getRgb()
                    redVal = pixelRGB[0]
                    greenVal = pixelRGB[1]
                    blueVal = pixelRGB[2]
                    if greenVal == 255 and blueVal == 255:
                        #This pixel would be white if red channel set to 255
                        #so set the green and blue channels to zero
                        greenVal = blueVal = 0
                    value = qRgb(255, greenVal, blueVal)
                    self.qimage.setPixel(x, y, value)
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.addROItoImage: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.addROItoImage: ' + str(e))


    def setROIPathColour(self, colour, listPathCoords):
        """This function is not currently used """
        logger.info("FreeHandROI.GraphicsItem.setROIPathColour called")
        try:
            if listPathCoords is not None:
                for coords in listPathCoords:
                    x = coords[0]
                    y = coords[1]

                    pixelColour = self.qimage.pixel(x, y) 
                    pixelRGB =  QColor(pixelColour).getRgb()
                    redVal = pixelRGB[0]
                    greenVal = pixelRGB[1]
                    blueVal = pixelRGB[2]
                    if greenVal == 255 and blueVal == 255:
                        #This pixel would be white if red channel set to 255
                        #so set the green and blue channels to zero
                        greenVal = blueVal = 0
                    value = qRgb(255, greenVal, blueVal)

                    self.qimage.setPixel(x, y, value)
                    #convert QImage to QPixmap to be able to update image
                    #with filled ROI
                    self.pixMap = QPixmap.fromImage(self.qimage)
                    self.update()

                    #Test if the ROI was not closed when drawn,
                    #so it was closed with a staight line.
                    lastIndex = len(listPathCoords)-1
                    startX = listPathCoords[0][0]
                    startY = listPathCoords[0][1]
                    endX = listPathCoords[lastIndex][0]
                    endY = listPathCoords[lastIndex][1]
                    if int(endX) != int(startX) and int(endY) != int(startY):
                        #free hand drawn ROI is not closed, 
                        #so draw a straight line between start and end points
                        self.drawStraightLine(startX, startY, endX, endY, colour=colour)
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.setROIPathColour: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.setROIPathColour: ' + str(e))


    def getRoiMeanAndStd(self):
        logger.info("FreeHandROI.GraphicsItem.getRoiMeanAndStd called")
        mean = round(np.mean(np.extract(self.mask, self.pixelArray)), 3)
        std = round(np.std(np.extract(self.mask, self.pixelArray)), 3)
        return mean, std


    def getMaskData(self):
        logger.info("FreeHandROI.GraphicsItem.getMaskData called")
        return self.mask


    def getListRoiInnerPoints(self, roi):
        logger.info("FreeHandROI.GraphicsItem.getListRoiInnerPoints called")
        try:
            if roi is not None:
                result = np.where(roi == True)
                return list(zip(result[1], result[0]))
            else:
                return None
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.getListRoiInnerPoints: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.getListRoiInnerPoints: ' + str(e))


    def createBlankMask(self):
        logger.info("FreeHandROI.GraphicsItem.createBlankMask called")
        ny, nx = np.shape(self.pixelArray)
        self.mask = np.full((nx, ny), False, dtype=bool)


    def createMaskFromDrawnROI(self, roiBoundaryCoords):
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
            #Setting radius=0.1 includes the drawn boundary in the ROI
            #ideally radius should = pixel size
            self.mask = roiPath.contains_points(points, radius=0.1).reshape((ny, nx))
            result = np.where(self.mask == True) 
            print("true coords ={}".format(list(zip(result[0], result[1])) ))

        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.createMaskFromDrawnROI: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.createMaskFromDrawnROI: ' + str(e))
            

    def mousePressEvent(self, event):
        logger.info("FreeHandROI.GraphicsItem.mousePressEvent called")
        try:
            button = event.button()
            if (button == Qt.LeftButton):
              self.sigZoomIn.emit()
            elif (button == Qt.RightButton): 
              self.sigZoomOut.emit()
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.mousePressEvent: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.mousePressEvent: ' + str(e))


def readLevels(path, pixelArray): 
        """Reads levels directly from the DICOM image"""
        try:
            logger.info("GraphicsItem.readLevels called")
            #set default values
            centre = -1 
            width = -1 
            maximumValue = -1  
            minimumValue = -1 
            dataset = ReadDICOM_Image.getDicomDataset(path)
            if dataset and hasattr(dataset, 'WindowCenter') and hasattr(dataset, 'WindowWidth'):
                slope = float(getattr(dataset, 'RescaleSlope', 1))
                intercept = float(getattr(dataset, 'RescaleIntercept', 0))
                centre = dataset.WindowCenter # * slope + intercept
                width = dataset.WindowWidth # * slope
                if [0x2005, 0x100E] in dataset: # 'Philips Rescale Slope'
                    centre = centre / dataset[(0x2005, 0x100E)].value
                    width = width / dataset[(0x2005, 0x100E)].value
                maximumValue = centre + width/2
                minimumValue = centre - width/2
            elif dataset and hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
                # In Enhanced MRIs, this display will retrieve the centre and width values of the first slice
                slope = dataset.PerFrameFunctionalGroupsSequence[0].PixelValueTransformationSequence[0].RescaleSlope
                intercept = dataset.PerFrameFunctionalGroupsSequence[0].PixelValueTransformationSequence[0].RescaleIntercept
                centre = dataset.PerFrameFunctionalGroupsSequence[0].FrameVOILUTSequence[0].WindowCenter # * slope + intercept
                width = dataset.PerFrameFunctionalGroupsSequence[0].FrameVOILUTSequence[0].WindowWidth # * slope
                if [0x2005, 0x100E] in dataset: # 'Philips Rescale Slope'
                    centre = centre / dataset[(0x2005, 0x100E)].value
                    width = width / dataset[(0x2005, 0x100E)].value
                maximumValue = centre + width/2
                minimumValue = centre - width/2 
            else:
                minimumValue = np.amin(pixelArray) if (np.median(pixelArray) - iqr(pixelArray, rng=(
                1, 99))/2) < np.amin(pixelArray) else np.median(pixelArray) - iqr(pixelArray, rng=(1, 99))/2
                maximumValue = np.amax(pixelArray) if (np.median(pixelArray) + iqr(pixelArray, rng=(
                1, 99))/2) > np.amax(pixelArray) else np.median(pixelArray) + iqr(pixelArray, rng=(1, 99))/2
                centre = minimumValue + (abs(maximumValue) - abs(minimumValue))/2
                width = maximumValue - abs(minimumValue)

            return minimumValue, maximumValue
        except Exception as e:
            print('Error in GraphicsItem.readLevels: ' + str(e))
            logger.error('Error in GraphicsItem.readLevels: ' + str(e))

       