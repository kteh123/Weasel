from PyQt5.QtCore import (QRectF, Qt)
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import (QPainter, QPixmap, QColor, QImage, QCursor, qRgb)
from PyQt5.QtWidgets import  QGraphicsObject, QApplication, QMenu, QAction
import numpy as np
import CoreModules.freeHandROI.helperFunctions as fn
from numpy import nanmin, nanmax
from matplotlib.path import Path as MplPath
import sys
import CoreModules.freeHandROI.Resources as icons
np.set_printoptions(threshold=sys.maxsize)
import logging
logger = logging.getLogger(__name__)

__version__ = '1.0'
__author__ = 'Steve Shillitoe'


class GraphicsItem(QGraphicsObject):
    #sub classing QGraphicsObject rather than more logical QGraphicsItem
    #because QGraphicsObject can emit signals but QGraphicsItem cannot
    sigMouseHovered = QtCore.Signal(bool)
    sigMaskCreated = QtCore.Signal()
    sigMaskEdited = QtCore.Signal()
    sigZoomIn = QtCore.Signal()
    sigZoomOut = QtCore.Signal()

    def __init__(self, pixelArray, roi): 
        super(GraphicsItem, self).__init__()
        logger.info("GraphicsItem initialised")
        self.pixelArray = pixelArray 
        minValue, maxValue = self.__quickMinMax(self.pixelArray)
        self.contrast = maxValue - minValue
        self.intensity = minValue + (maxValue - minValue)/2
        imgData, alpha = fn.makeARGB(data=self.pixelArray, levels=[minValue, maxValue])
        self.origQimage = fn.makeQImage(imgData, alpha)
        self.qimage = fn.makeQImage(imgData, alpha)
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
        self.eraseEnabled = False
        self.zoomEnabled = False
        self.setToolTip("Use the mouse wheel to zoom")


    def updateImageLevels(self, intensity, contrast, roi):
        logger.info("freeHandROI.GraphicsItem.updateImageLevels called")
        try:
            minValue = intensity - (contrast/2)
            maxValue = contrast + minValue
            imgData, alpha = fn.makeARGB(data=self.pixelArray, levels=[minValue, maxValue])
            self.qimage = fn.makeQImage(imgData, alpha)
            self.pixMap = QPixmap.fromImage(self.qimage)

            #Need to reapply mask
            if roi is not None and roi.any():
                self.reloadMask(roi)

            self.update()
        except Exception as e:
            print('Error in freeHandROI.GraphicsItem.updateImageLevels: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.updateImageLevels: ' + str(e))


    def paint(self, painter, option, widget):
        logger.info("freeHandROI.GraphicsItem.paint called")
        try:
            painter.setOpacity(1)
            painter.drawPixmap(0,0, self.width, self.height, self.pixMap)
        except Exception as e:
            print('Error in freeHandROI.GraphicsItem.paint: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.paint: ' + str(e))
        

    def boundingRect(self): 
        logger.info("freeHandROI.GraphicsItem.boundingRect called")
        return QRectF(0,0,self.width, self.height)


    def __quickMinMax(self, data):
        """
        Estimate the min/max values of *data* by subsampling.
        """
        logger.info("freeHandROI.GraphicsItem.__quickMinMax called")
        try:
            while data.size > 1e6:
                ax = np.argmax(data.shape)
                sl = [slice(None)] * data.ndim
                sl[ax] = slice(None, None, 2)
                data = data[sl]
            return nanmin(data), nanmax(data)
        except Exception as e:
            print('Error in freeHandROI.GraphicsItem.__quickMinMax: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.__quickMinMax: ' + str(e))


    def hoverEnterEvent(self, event):
        logger.info("freeHandROI.GraphicsItem.hoverEnterEvent called")
        try:
            if self.drawEnabled:
                pm = QPixmap(icons.PEN_CURSOR)
                cursor = QCursor(pm, hotX=0, hotY=30)
                QApplication.setOverrideCursor(cursor)
            if self.eraseEnabled:
                pm = QPixmap(icons.ERASOR_CURSOR)
                cursor = QCursor(pm, hotX=0, hotY=30)
                QApplication.setOverrideCursor(cursor)
            if self.zoomEnabled:
                pm = QPixmap(icons.MAGNIFYING_GLASS_CURSOR)
                cursor = QCursor(pm, hotX=0, hotY=30)
                QApplication.setOverrideCursor(cursor)
        except Exception as e:
            print('Error in freeHandROI.GraphicsItem.hoverEnterEvent: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.hoverEnterEvent: ' + str(e))


    def hoverLeaveEvent(self, event):
        logger.info("freeHandROI.GraphicsItem.hoverLeaveEvent called")
        try:
            QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
            self.sigMouseHovered.emit(False)
        except Exception as e:
            print('Error in freeHandROI.GraphicsItem.hoverEnterEvent: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.hoverEnterEvent: ' + str(e))


    def hoverMoveEvent(self, event):
        logger.info("freeHandROI.GraphicsItem.hoverMoveEvent called")
        try:
            self.xMouseCoord = int(event.pos().x())
            self.yMouseCoord = int(event.pos().y())
            self.pixelColour = self.origQimage.pixelColor(self.xMouseCoord,  self.yMouseCoord ).getRgb()[:-1]
            self.pixelValue = round(self.pixelArray[self.xMouseCoord, self.yMouseCoord], 3)
            self.sigMouseHovered.emit(True)
        except Exception as e:
            print('Error in freeHandROI.GraphicsItem.hoverMoveEvent: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.hoverMoveEvent: ' + str(e))
       

    def mouseMoveEvent(self, event):
        logger.info("freeHandROI.GraphicsItem.mouseMoveEvent called")
        try:
            buttons = event.buttons()
            if (buttons == Qt.LeftButton):
                xCoord = int(event.pos().x())
                yCoord = int(event.pos().y())
                if self.drawEnabled:
                    #Only draw if left button pressed
                    if self.last_x is None: # First event.
                        self.last_x = (event.pos()).x()
                        self.last_y = (event.pos()).y()
                        self.start_x = int(self.last_x)
                        self.start_y = int(self.last_y)
                        return #  Ignore the first time.
                    self.drawStraightLine(self.last_x, self.last_y, xCoord, yCoord)
                    # Update the origin for next time.
                    self.last_x = xCoord
                    self.last_y = yCoord
                    #Do not add duplicates to the list
                    if [self.last_x, self.last_y] not in self.pathCoordsList:
                        self.pathCoordsList.append([self.last_x, self.last_y])
                    self.mouseMoved = True

                if self.eraseEnabled:
                    #erase mask at this pixel 
                    #and set pixel back to original value
                    if self.mask is not None:
                        self.resetPixel(xCoord, yCoord)
                        #self.mask[xCoord, yCoord] = False
                        self.mask[yCoord, xCoord] = False
                        self.sigMaskEdited.emit()

            #elif (buttons == Qt.RightButton):
        except Exception as e:
            print('Error in freeHandROI.GraphicsItem.mouseMoveEvent: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.mouseMoveEvent: ' + str(e))


    def mouseReleaseEvent(self, event):
        logger.info("freeHandROI.GraphicsItem.mouseReleaseEvent called")
        try:
            button = event.button()
            if (button == Qt.LeftButton):
                if self.drawEnabled:
                    if self.mouseMoved:
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
                            self.createMask(self.pathCoordsList)
                            self.listROICoords = self.getListRoiInnerPoints(self.mask)
                            #print("ROI Inner coords={}".format(self.listROICoords))
                            self.fillFreeHandRoi()
                            self.start_x = None 
                            self.start_y = None
                            self.last_x = None
                            self.last_y = None
                            self.pathCoordsList = []
                            self.mouseMoved = False
                    else:
                        #The mouse was not moved, so a pixel was clicked on
                        xCoord = int(event.pos().x())
                        yCoord = int(event.pos().y())
                        if self.mask is not None:
                            if self.mask[yCoord, xCoord]:
                                pass
                                #mask already exists at this pixel, 
                                #so do nothing
                            else:
                                #added to the mask
                                self.setPixelToRed(xCoord, yCoord)
                                #self.mask[xCoord, yCoord] = True
                                self.mask[yCoord, xCoord] = True
                                self.sigMaskCreated.emit()
                        else:
                            #first create a boolean mask with all values False
                            self.createBlankMask()
                            self.setPixelToRed(xCoord, yCoord)
                            self.mask[yCoord, xCoord] = True
                            self.sigMaskCreated.emit()

                if self.eraseEnabled:
                    if self.mask is not None:
                        if not self.mouseMoved:
                            #The mouse was not moved, so a pixel was clicked on
                            xCoord = int(event.pos().x())
                            yCoord = int(event.pos().y())
                            #erase mask at this pixel 
                            #and set pixel back to original value
                            self.resetPixel(xCoord, yCoord)
                            #self.mask[xCoord, yCoord] = False
                            self.mask[yCoord, xCoord] = False
                            self.sigMaskEdited.emit()
        except Exception as e:
            print('Error in freeHandROI.GraphicsItem.mouseReleaseEvent: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.mouseReleaseEvent: ' + str(e))


    def resetPixel(self, x, y):
        logger.info("freeHandROI.GraphicsItem.resetPixel called")
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
            print('Error in freeHandROI.GraphicsItem.resetPixel: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.resetPixel: ' + str(e))
    

    def setPixelToRed(self, x, y):
        logger.info("freeHandROI.GraphicsItem.setPixelToRed called")
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
            print('Error in freeHandROI.GraphicsItem.setPixelToRed: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.setPixelToRed: ' + str(e))


    def drawStraightLine(self, startX, startY, endX, endY, colour='red'):
        logger.info("freeHandROI.GraphicsItem.drawStraightLine called")
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
            print('Error in freeHandROI.GraphicsItem.drawStraightLine: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.drawStraightLine: ' + str(e))

    def reloadImage(self):
        logger.info("freeHandROI.GraphicsItem.reloadImage called")
        try:
            self.qimage = None
            self.pixMap = None
            self.qimage = self.origQimage
            self.pixMap = QPixmap.fromImage(self.qimage)
            self.update()
        except Exception as e:
            print('Error in freeHandROI.GraphicsItem.reloadImage: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.reloadImage: ' + str(e))


    def reloadMask(self, mask):
        logger.info("freeHandROI.GraphicsItem.reloadMask called")
        try:
            #redisplays the ROI represented by mask
            self.listROICoords = self.getListRoiInnerPoints(mask)
            self.fillFreeHandRoi()
            self.listROICoords = []
        except Exception as e:
            print('Error in freeHandROI.GraphicsItem.reloadMask: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.reloadMask: ' + str(e))


    def fillFreeHandRoi(self):
        logger.info("freeHandROI.GraphicsItem.fillFreeHandRoi called")
        try:
            if self.listROICoords is not None:
                for coords in self.listROICoords:
                    x = coords[0]
                    y = coords[1]
                    self.setPixelToRed(x, y)
        except Exception as e:
            print('Error in freeHandROI.GraphicsItem.fillFreeHandRoi: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.fillFreeHandRoi: ' + str(e))


    def addROItoImage(self, roi):
        logger.info("freeHandROI.GraphicsItem.addROItoImage called")
        try:
            listROICoords = self.getListRoiInnerPoints(roi)
            if listROICoords is not None:
                for coords in listROICoords:
                    x = coords[0]
                    y = coords[1]
                    #x = coords[1]
                    #y = coords[0]
                    #print("({}, {})".format(x, y))
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
            print('Error in freeHandROI.GraphicsItem.addROItoImage: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.addROItoImage: ' + str(e))


    def setROIPathColour(self, colour, listPathCoords):
        logger.info("freeHandROI.GraphicsItem.setROIPathColour called")
        try:
            if listPathCoords is not None:
                for coords in listPathCoords:
                    x = coords[0]
                    y = coords[1]
                    pixelColour = self.qimage.pixel(x, y) 
                    pixelRGB =  QColor(pixelColour).getRgb()

                    if colour == "red":
                        value = qRgb(255, 0, 0)
                    elif colour == "blue":
                        value = qRgb(0, 0, 255) 

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
            print('Error in freeHandROI.GraphicsItem.setROIPathColour: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.setROIPathColour: ' + str(e))

    def getRoiMeanAndStd(self):
        logger.info("freeHandROI.GraphicsItem.getRoiMeanAndStd called")
        mean = round(np.mean(np.extract(self.mask, self.pixelArray)), 3)
        std = round(np.std(np.extract(self.mask, self.pixelArray)), 3)
        return mean, std


    def getMaskData(self):
        logger.info("freeHandROI.GraphicsItem.getMaskData called")
        return self.mask


    def getListRoiInnerPoints(self, roi):
        logger.info("freeHandROI.GraphicsItem.getListRoiInnerPoints called")
        try:
            if roi is not None:
                result = np.where(roi == True)
                return list(zip(result[1], result[0]))
            else:
                return None
        except Exception as e:
            print('Error in freeHandROI.GraphicsItem.getListRoiInnerPoints: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.getListRoiInnerPoints: ' + str(e))

    def createBlankMask(self):
        logger.info("freeHandROI.GraphicsItem.createBlankMask called")
        ny, nx = np.shape(self.pixelArray)
        self.mask = np.full((nx, ny), False, dtype=bool)


    def createMask(self, roiBoundaryCoords):
        logger.info("freeHandROI.GraphicsItem.createMask called")
        try:
            self.mask = None
            nx, ny = np.shape(self.pixelArray)
            #print("roiBoundaryCoords ={}".format(roiBoundaryCoords))
            # Create vertex coordinates for each grid cell...
            # (<0,0> is at the top left of the grid in this system)
            x, y = np.meshgrid(np.arange(nx), np.arange(ny))
            points = list(zip(x.flatten(),y.flatten()))
            #print("Points={}".format(points))
            #print("roiBoundaryCoords={}".format(roiBoundaryCoords))
            roiPath = MplPath(roiBoundaryCoords)
             # print("roiPath={}".format(roiPath))
            #setting radius=0.1 includes the drawn boundary in the ROI
            #ideally radius should = pixel size
            self.mask = roiPath.contains_points(points, radius=0.1).reshape((nx, ny))
            self.sigMaskCreated.emit()
        except Exception as e:
            print('Error in freeHandROI.GraphicsItem.createMask: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.createMask: ' + str(e))
            

    def mousePressEvent(self, event):
        logger.info("freeHandROI.GraphicsItem.mousePressEven called")
        try:
            button = event.button()
            if (button == Qt.LeftButton):
              self.sigZoomIn.emit()
            elif (button == Qt.RightButton): 
              self.sigZoomOut.emit()
        except Exception as e:
            print('Error in freeHandROI.GraphicsItem.createMask: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsItem.createMask: ' + str(e))



    #      def get_mask(img_frame, drawn_roi, row, col):
    #for i in np.arange(row):
    #    for j in np.arange(col):
    #         if np.logical_and(drawn_roi.path.contains_points([(j,i)]) == [True], img_frame[i][j] > 0):
    #             mask[i][j] = 1
    #mask_bool = mask.astype(bool)
    #mask_bool = ~mask_bool
    #return mask_bool