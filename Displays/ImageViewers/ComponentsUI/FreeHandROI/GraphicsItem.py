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
    sigRightMouseDrag = QtCore.Signal(float, float)
    sigZoomIn = QtCore.Signal()
    sigZoomOut = QtCore.Signal()
     

    def __init__(self, linkToGraphicsView): 
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
       return '{}'.format(
           self.__class__.__name__)


    def updateImageLevels(self, intensity, contrast, roi):
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
        for coords in self.pathCoordsList:
            cols = coords[0]  #x
            rows = coords[1]  #y
            self.mask[rows, cols] = True


    def closeAndFillROI(self):
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
        #erase mask at this mouse pointer position
        #and set pixel back to original value
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
            self.update()
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.resetPixelToOriginalValue: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.resetPixelToOriginalValue: ' + str(e))
    

    def setPixelToRed(self, x, y):
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
            self.update()
        except Exception as e:
            print('Error in FreeHandROI.GraphicsItem.setPixelToRed: ' + str(e))
            logger.error('Error in FreeHandROI.GraphicsItem.setPixelToRed: ' + str(e))


    def reloadImage(self):
        logger.info("FreeHandROI.GraphicsItem.reloadImage called")
        try:
            self.qImage = None
            self.pixMap = None
            self.mask = None
            self.qImage = self.origQImage
            self.pixMap = QPixmap.fromImage(self.qImage)
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
        rows, cols = np.shape(self.pixelArray)
        self.mask = np.full((rows, cols), False, dtype=bool)


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
            #Setting radius=0.0 does not include the drawn boundary in the ROI
            self.mask = roiPath.contains_points(points, radius=0.0).reshape((ny, nx))   

            #innerROIPoints  = np.where(self.mask == True)
            #print("GraphicsItem true coords ={}".format(list(zip(innerROIPoints[1], innerROIPoints[0])) ))
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

    