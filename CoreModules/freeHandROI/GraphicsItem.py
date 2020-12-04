from PyQt5.QtCore import (QRectF, Qt)
from PyQt5 import QtCore
from PyQt5.QtGui import (QPainter, QPixmap, QColor, QImage, qRgb)
from PyQt5.QtWidgets import  QGraphicsObject
import numpy as np
from pyqtgraph import functions as fn
from numpy import nanmin, nanmax
from matplotlib.path import Path as MplPath
import sys
np.set_printoptions(threshold=sys.maxsize)

class GraphicsItem(QGraphicsObject):
    #sub classing QGraphicsObject rather than more logical QGraphicsItem
    #because QGraphicsObject can emit signals but QGraphicsItem cannot
    sigMouseHovered = QtCore.Signal()
    sigMaskCreated = QtCore.Signal()

    def __init__(self, pixelArray): 
        super(GraphicsItem, self).__init__()
        self.pixelArray = pixelArray 
        minValue, maxValue = self.__quickMinMax(self.pixelArray)
        self.contrast = maxValue - minValue
        self.intensity = minValue + (maxValue - minValue)/2
        imgData, alpha = fn.makeARGB(data=self.pixelArray, levels=[minValue, maxValue])
        self.origQimage = fn.makeQImage(imgData, alpha)
        self.qimage = fn.makeQImage(imgData, alpha)
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
        self.mask = None
        self.xMouseCoord  = None
        self.yMouseCoord  = None
        self.pixelColour = None
        self.pixelValue = None


    def updateImageLevels(self, intensity, contrast, mask):
        try:
            minValue = intensity - (contrast/2)
            maxValue = contrast + minValue
            imgData, alpha = fn.makeARGB(data=self.pixelArray, levels=[minValue, maxValue])
            self.qimage = fn.makeQImage(imgData, alpha)
            self.pixMap = QPixmap.fromImage(self.qimage)

            #Need to reapply mask
            if mask is not None:
                self.reloadMask(mask)

            self.update()
        except Exception as e:
            print('Error in GraphicsItem.updateImageLevels: ' + str(e))


    def paint(self, painter, option, widget):
        painter.setOpacity(1)
        painter.drawPixmap(0,0, self.width, self.height, self.pixMap)
        

    def boundingRect(self):  
        return QRectF(0,0,self.width, self.height)


    def __quickMinMax(self, data):
        """
        Estimate the min/max values of *data* by subsampling.
        """
        while data.size > 1e6:
            ax = np.argmax(data.shape)
            sl = [slice(None)] * data.ndim
            sl[ax] = slice(None, None, 2)
            data = data[sl]
        return nanmin(data), nanmax(data)


    def hoverMoveEvent(self, event):
        #print("hoverMoveEvent out")
        if self.isUnderMouse():
            #print("hoverMoveEvent in")
            self.xMouseCoord = int(event.pos().x())
            self.yMouseCoord = int(event.pos().y())
            self.pixelColour = self.origQimage.pixelColor(self.xMouseCoord,  self.yMouseCoord ).getRgb()[:-1]
            self.pixelValue = self.origQimage.pixelColor(self.xMouseCoord,  self.yMouseCoord ).value()
            self.sigMouseHovered.emit()


    def mouseMoveEvent(self, event):
        if self.last_x is None: # First event.
            self.last_x = (event.pos()).x()
            self.last_y = (event.pos()).y()
            self.start_x = int(self.last_x)
            self.start_y = int(self.last_y)
            return #  Ignore the first time.
        xCoord = event.pos().x()
        yCoord = event.pos().y()
        self.drawStraightLine(self.last_x, self.last_y, xCoord, yCoord)

        # Update the origin for next time.
        self.last_x = xCoord
        self.last_y = yCoord
        self.pathCoordsList.append([self.last_x, self.last_y])
        

    def mouseReleaseEvent(self, event):
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
            self.getMask(self.pathCoordsList)
            self.listROICoords = self.getListRoiInnerPoints(self.mask)
            self.fillFreeHandRoi()
            self.start_x = None 
            self.start_y = None
            self.last_x = None
            self.last_y = None
            self.pathCoordsList = []


    def drawStraightLine(self, startX, startY, endX, endY, colour='red'):
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


    def reloadImage(self):
        self.qimage = None
        self.pixMap = None
        self.qimage = self.origQimage
        self.pixMap = QPixmap.fromImage(self.qimage)
        self.update()


    def reloadMask(self, mask):
        #redisplays the ROI represented by mask
        self.listROICoords = self.getListRoiInnerPoints(mask)
        self.fillFreeHandRoi()
        self.listROICoords = []


    def fillFreeHandRoi(self):
        if self.listROICoords is not None:
            for coords in self.listROICoords:
                #x = coords[0]
                #y = coords[1]
                x = coords[1]
                y = coords[0]
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


    def setROIPathColour(self, colour, listPathCoords):
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
                    


    def getRoiMeanAndStd(self):
        mean = round(np.mean(np.extract(self.mask, self.pixelArray)), 3)
        std = round(np.std(np.extract(self.mask, self.pixelArray)), 3)
        return mean, std


    def getMaskData(self):
        return self.mask


    def getListRoiInnerPoints(self, mask):
        #result = np.nonzero(self.mask)
        if mask is not None:
            result = np.where(mask == True)
            return list(zip(result[0], result[1]))
        else:
            return None


    def getMask(self, roiLineCoords):
            self.mask = None
            ny, nx = np.shape(self.pixelArray)
            #print("roiLineCoords ={}".format(roiLineCoords))
            # Create vertex coordinates for each grid cell...
            # (<0,0> is at the top left of the grid in this system)
            x, y = np.meshgrid(np.arange(nx), np.arange(ny))
            x, y = x.flatten(), y.flatten()
            points = np.vstack((x, y)).T #points = every [x,y] pair within the original image
        
            #print("roiLineCoords={}".format(roiLineCoords))
            roiPath = MplPath(roiLineCoords)
            #print("roiPath={}".format(roiPath))
            self.mask = roiPath.contains_points(points).reshape((ny, nx))
            self.sigMaskCreated.emit()
            

    def mousePressEvent(self, event):
        pass
