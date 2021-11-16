from PyQt5.QtCore import QRectF, Qt,  QCoreApplication
from PyQt5 import QtCore 
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QMenu, QMessageBox,
                            QAction, QActionGroup, QApplication )
from PyQt5.QtGui import QPixmap, QCursor, QIcon, QToolTip
from .GraphicsItem import GraphicsItem
from .ROI_Storage import ROIs 
from .Resources import * 
import logging
#import numpy as np
logger = logging.getLogger(__name__)

__version__ = '1.0'
__author__ = 'Steve Shillitoe'
#October/November 2020

ZOOM_IN = 1
ZOOM_OUT = -1


class GraphicsView(QGraphicsView):
    sigContextMenuDisplayed = QtCore.Signal()
    sigReloadImage =  QtCore.Signal()
    sigROIDeleted = QtCore.Signal()
    sigSetDrawButtonRed = QtCore.Signal(bool)
    sigSetPaintButtonRed = QtCore.Signal(bool)
    sigSetEraseButtonRed = QtCore.Signal(bool)
    sigROIChanged = QtCore.Signal()
    sigNewROI = QtCore.Signal(str)
    sigUpdateZoom = QtCore.Signal(int)


    def __init__(self, numberOfImages): 
        super(GraphicsView, self).__init__()
        self.scene = QGraphicsScene(self)
        self._zoom = 0
        self.graphicsItem = None
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.currentROIName = None
        self.currentImageNumber = None
        self.dictROIs = ROIs(numberOfImages, self)
        self.mainContextMenu = QMenu()
        self.mainContextMenu.hovered.connect(self._actionHovered)
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
       return '{}'.format(
           self.__class__.__name__)


    def setZoomEnabled(self, boolValue):
        self.zoomEnabled = boolValue


    def setImage(self, pixelArray, mask = None, path = None):
        logger.info("freeHandROI.GraphicsView.setImage called")
        try:
            if self.graphicsItem is not None:
                self.graphicsItem = None
                self.scene.clear()

            self.graphicsItem = GraphicsItem(pixelArray, mask, path, self)
       
            #Give graphicsItem some time to adjust itself
            QApplication.processEvents()
            self.scene.addItem(self.graphicsItem)
            self.fitInView(self.graphicsItem, Qt.KeepAspectRatio) 
            self.reapplyZoom()

            ##Centre the image on the area where the ROI was drawn
            #if mask is not None:
            #    result = np.where(mask == True)
            #    print("Mask True coords ={}".format(list(zip(result[1], result[0]))))
            #    #print("Mask True coords ={}".format(list(zip(np.where(mask == True)))))
            #    print("self.centerOn({},{})".format(float(result[1][0]),float(result[0][0])))
            #    self.centerOn(float(result[1][0]),float(result[0][0]))

            self.graphicsItem.sigZoomIn.connect(lambda: self.zoomFromMouseClicks(ZOOM_IN))
            self.graphicsItem.sigZoomOut.connect(lambda: self.zoomFromMouseClicks(ZOOM_OUT))
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.setImage: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.setImage: ' + str(e))


    def reapplyZoom(self):
        if self._zoom > 0:
            factor = 1.25
            totalFactor = factor**self._zoom
            self.scale(totalFactor, totalFactor)
        

    def zoomFromMouseClicks(self, zoomValue):
        if self.zoomEnabled:
            self.zoomImage(zoomValue)
    

    def fitImageToViewPort(self):
        self.zoomImage(ZOOM_IN)
        self.zoomImage(ZOOM_OUT)


    def zoomImage(self, zoomValue):
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
        self.zoomImage(event.angleDelta().y())


    def fitItemInView(self):#, scale=True
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


    def toggleDragMode(self):
        logger.info("freeHandROI.GraphicsView.toggleDragMode called")
        try:
            if self.dragMode() == QGraphicsView.ScrollHandDrag:
                self.setDragMode(QGraphicsView.NoDrag)
            else:
                self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.setDragMode(QGraphicsView.ScrollHandDrag)
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.toggleDragMode: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.toggleDragMode: ' + str(e))


    def setUpPixelSquareSizeMenu(self, event):
        self.pixelSquareSizeMenu.clear()
        onePixel = QAction('One Pixel', None)
        onePixel.setCheckable(True)
        onePixel.setToolTip('Erase/Paint one pixel')
        threePixels = QAction('3 x 3 Pixels', None)
        threePixels.setCheckable(True)
        threePixels.setToolTip('Erase/Paint a 3x3 square of pixels')
        fivePixels = QAction('5 x 5 Pixels', None)
        fivePixels.setCheckable(True)
        fivePixels.setToolTip('Erase/Paint a 5x5 square of pixels')
        sevenPixels = QAction('7 x 7 Pixels', None)
        sevenPixels.setCheckable(True)
        sevenPixels.setToolTip('Erase/Paint a 7x7 square of pixels')
        ninePixels = QAction('9 x 9 Pixels', None)
        ninePixels.setCheckable(True)
        ninePixels.setToolTip('Erase/Paint a 9x9 square of pixels')
        elevenPixels = QAction('11 x 11 Pixels', None)
        elevenPixels.setCheckable(True)
        elevenPixels.setToolTip('Erase/Paint a 11x11 square of pixels')
        twentyOnePixels = QAction('21 x 21 Pixels', None)
        twentyOnePixels.setCheckable(True)
        twentyOnePixels.setToolTip('Erase/Paint a 21x21 square of pixels')

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

        onePixel.triggered.connect(lambda:self.setPixelSquareSize(1, onePixel ))
        threePixels.triggered.connect(lambda:  self.setPixelSquareSize(3,threePixels ))
        fivePixels.triggered.connect(lambda:  self.setPixelSquareSize(5,fivePixels))
        sevenPixels.triggered.connect(lambda:  self.setPixelSquareSize(7, sevenPixels))
        ninePixels.triggered.connect(lambda:  self.setPixelSquareSize(9, ninePixels))
        elevenPixels.triggered.connect(lambda:  self.setPixelSquareSize(11,elevenPixels))
        twentyOnePixels.triggered.connect(lambda:  self.setPixelSquareSize(21,twentyOnePixels ))
        
        self.pixelSquareSizeMenu.addAction(onePixel)
        self.pixelSquareSizeMenu.addAction(threePixels)
        self.pixelSquareSizeMenu.addAction(fivePixels)
        self.pixelSquareSizeMenu.addAction(sevenPixels)
        self.pixelSquareSizeMenu.addAction(ninePixels)
        self.pixelSquareSizeMenu.addAction(elevenPixels)
        self.pixelSquareSizeMenu.addAction(twentyOnePixels)
        self.pixelSquareSizeMenu.exec_(event.globalPos())


    def setPixelSquareSize(self, pixelSquareSize, action):
        self.pixelSquareSize = pixelSquareSize


    def setUpMainContextMenu(self, event):
        self.mainContextMenu.clear()
        self.sigContextMenuDisplayed.emit()
        zoomIn = QAction('Zoom In', None)
        zoomIn.setToolTip('Click to zoom in')
        zoomOut = QAction('Zoom Out', None)
        zoomOut.setToolTip('Click to zoom out')
        zoomIn.triggered.connect(lambda: self.zoomImage(ZOOM_IN))
        zoomOut.triggered.connect(lambda: self.zoomImage(ZOOM_OUT))
        
        drawROI = QAction(QIcon(PEN_CURSOR), 'Draw', None)
        drawROI.setToolTip("Draw an ROI")
        drawROI.triggered.connect(lambda: self.drawROI(True))

        paintROI = QAction(QIcon(BRUSH_CURSOR), 'Paint', None)
        paintROI.setToolTip("Paint an ROI")
        paintROI.triggered.connect(lambda: self.paintROI(True))
        
        eraseROI  = QAction(QIcon(ERASER_CURSOR), 'Eraser', None)
        eraseROI.setToolTip("Erase the ROI")
        eraseROI.triggered.connect(lambda: self.eraseROI(True))
        
        newROI  = QAction(QIcon(NEW_ICON),'New ROI', None)
        newROI.setToolTip("Create a new ROI")
        newROI.triggered.connect(self.newROI)
        
        resetROI  = QAction(QIcon(RESET_ICON),'Reset ROI', None)
        resetROI.setToolTip("Clear drawn ROI from the image")
        resetROI.triggered.connect(self.resetROI)
        
        deleteROI  = QAction(QIcon(DELETE_ICON), 'Delete ROI', None)
        deleteROI.setToolTip("Delete drawn ROI from the image")
        deleteROI.triggered.connect(self.deleteROI)
        
        self.mainContextMenu.addAction(zoomIn)
        self.mainContextMenu.addAction(zoomOut)
        self.mainContextMenu.addSeparator()
        self.mainContextMenu.addAction(drawROI)
        self.mainContextMenu.addAction(paintROI)
        self.mainContextMenu.addAction(eraseROI)
        self.mainContextMenu.addSeparator()
        self.mainContextMenu.addAction(newROI)
        self.mainContextMenu.addAction(resetROI)
        self.mainContextMenu.addAction(deleteROI)
        self.mainContextMenu.exec_(event.globalPos())


    def contextMenuEvent(self, event):
        #display pop-up context menu when the right mouse button is pressed
        #as long as zoom is not enabled
        logger.info("freeHandROI.GraphicsView.contextMenuEvent called")
        try:
            if not self.zoomEnabled:
                if self.eraseEnabled or self.paintEnabled:
                    self.setUpPixelSquareSizeMenu(event)
                else:
                    self.setUpMainContextMenu(event)  
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.contextMenuEvent: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.contextMenuEvent: ' + str(e))
            

    def _actionHovered(self, action):
        tip = action.toolTip()
        QToolTip.showText(QCursor.pos(), tip)


    def drawROI(self, fromContextMenu = False):
        logger.info("freeHandROI.GraphicsView.drawROI called")
        try:
            if not self.drawEnabled:
                if fromContextMenu:
                    self.sigSetDrawButtonRed.emit(True)
                self.drawEnabled = True
                self.setZoomEnabled(False)
                self.eraseEnabled = False
                self.graphicsItem.paintEnabled = False
            else:
                self.drawEnabled = False
                if fromContextMenu:
                    self.sigSetDrawButtonRed.emit(False)
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.drawROI: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.drawROI: ' + str(e))


    def paintROI(self, fromContextMenu = False):
        logger.info("freeHandROI.GraphicsView.paintROI called")
        try:
            if not self.paintEnabled:
                if fromContextMenu:
                    self.sigSetPaintButtonRed.emit(True)
                self.setZoomEnabled(False)
                self.eraseEnabled = False
                self.drawEnabled = False
                self.paintEnabled = True
                self.pixelSquareSize = 1
            else:
                self.paintEnabled = False
                if fromContextMenu:
                    self.sigSetPaintButtonRed.emit(False)
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.paintROI: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.paintROI: ' + str(e))


    def eraseROI(self, fromContextMenu = False):
        logger.info("freeHandROI.GraphicsView.eraseROI called")
        try:
            if not self.eraseEnabled:
                if fromContextMenu:
                    self.sigSetEraseButtonRed.emit(True)
                self.drawEnabled = False
                self.paintEnabled = False
                self.setZoomEnabled(False)
                self.eraseEnabled = True
                self.pixelSquareSize = 1
            else:
                self.eraseEnabled = False
                if fromContextMenu:
                    self.sigSetEraseButtonRed.emit(False)
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.eraseROI: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.eraseROI: ' + str(e))
            

    def newROI(self):
        logger.info("freeHandROI.GraphicsView.newROI called")
        try:
            self.sigROIChanged.emit()
            if self.dictROIs.hasRegionGotMask(self.currentROIName):
                newRegion = self.dictROIs.getNextRegionName()
                self.sigNewROI.emit(newRegion)
                self.graphicsItem.reloadImage()
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
        logger.info("freeHandROI.GraphicsView.resetROI called")
        try:
            self.sigROIChanged.emit()
            self.dictROIs.deleteMask(self.currentROIName)
            self.sigReloadImage.emit()
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.resetROI: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.resetROI: ' + str(e))


    def deleteROI(self):
        logger.info("freeHandROI.GraphicsView.deleteROI called")
        try:
            self.sigROIChanged.emit()
            self.dictROIs.deleteMask(self.currentROIName)
            self.sigROIDeleted.emit()
        except Exception as e:
            print('Error in freeHandROI.GraphicsView.deleteROI: ' + str(e))
            logger.error('Error in freeHandROI.GraphicsView.deleteROI: ' + str(e))
