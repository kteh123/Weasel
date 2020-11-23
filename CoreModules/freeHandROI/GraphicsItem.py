from PyQt5.QtCore import (QRectF, Qt)
from PyQt5 import QtCore
from PyQt5.QtGui import (QPainter, QPixmap, QColor, QImage, qRgb)
from PyQt5.QtWidgets import  QGraphicsObject
import numpy as np
from pyqtgraph import functions as fn
from numpy import nanmin, nanmax
from matplotlib.path import Path as MplPath


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
        self.setAcceptHoverEvents(True)
        self.mask = None
        self.drawRoi = False
        self.xMouseCoord  = None
        self.yMouseCoord  = None
        self.pixelColour = None
        self.pixelValue = None


    def updateImageLevels(self, intensity, contrast):
        try:
            minValue = intensity - (contrast/2)
            maxValue = contrast + minValue
            imgData, alpha = fn.makeARGB(data=self.pixelArray, levels=[minValue, maxValue])
            self.qimage = fn.makeQImage(imgData, alpha)
            self.pixMap = QPixmap.fromImage(self.qimage)
            #Need to reapply mask
            if self.mask is not None:
                listCoords = self.getListRoiInnerPoints(self.mask)
                self.fillFreeHandRoi(listCoords)
                #This does not work
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
        if self.drawRoi:
            if self.last_x is None: # First event.
                self.last_x = (event.pos()).x()
                self.last_y = (event.pos()).y()
                self.start_x = int(self.last_x)
                self.start_y = int(self.last_y)
                return #  Ignore the first time.
            self.myPainter = QPainter(self.pixMap)
            myPen = self.myPainter.pen()
            myPen.setWidth(1) # 1 pixel
            myPen.setColor(QColor("#FF0000")) #red
            self.myPainter.setPen(myPen)
            #Draws a line from (x1 , y1 ) to (x2 , y2 ).
            xCoord = event.pos().x()
            yCoord = event.pos().y()
            self.myPainter.drawLine(self.last_x, self.last_y, xCoord, yCoord)
            self.myPainter.end() 
            #The pixmap has changed (it was drawn on), so update it
            #back to the original image
            self.qimage =  self.pixMap.toImage()
            self.update()

            # Update the origin for next time.
            self.last_x = xCoord
            self.last_y = yCoord
            self.pathCoordsList.append([self.last_x, self.last_y])
        

    def mouseReleaseEvent(self, event):
        if self.drawRoi:
            if  (self.last_x != None and self.start_x != None 
                 and self.last_y != None and self.start_y != None):
                if int(self.last_x) == self.start_x and int(self.last_y) == self.start_y:
                    #free hand drawn ROI is closed, so no further action needed
                    pass
                else:
                    #free hand drawn ROI is not closed, so need to draw a
                    #straight line from the coordinates of its start to
                    #the coordinates of its last point
                    self.myPainter = QPainter(self.pixMap)
                    p = self.myPainter.pen()
                    p.setWidth(1) #1 pixel
                    p.setColor(QColor("#FF0000")) #red
                    self.myPainter.setPen(p)
                    #self.myPainter.setRenderHint(QPainter.Antialiasing)
                    self.myPainter.drawLine(self.last_x, self.last_y, self.start_x, self.start_y)
                    self.myPainter.end()
                    self.qimage =  self.pixMap.toImage()
                    self.update()
                self.getMask(self.pathCoordsList)
                listCoords = self.getListRoiInnerPoints(self.mask)
                self.fillFreeHandRoi(listCoords)
                self.start_x = None 
                self.start_y = None
                self.last_x = None
                self.last_y = None
                self.pathCoordsList = []


    def fillFreeHandRoi(self, listCoords):
        for coords in listCoords:
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


    def getRoiMeanAndStd(self):
        mean = round(np.mean(np.extract(self.mask, self.pixelArray)), 3)
        std = round(np.std(np.extract(self.mask, self.pixelArray)), 3)
        return mean, std


    def getListRoiInnerPoints(self, mask):
        #result = np.nonzero(self.mask)
        result = np.where(mask == True)
        return list(zip(result[0], result[1]))


    def getMask(self, roiLineCoords):
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
