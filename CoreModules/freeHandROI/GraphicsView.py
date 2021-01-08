from PyQt5.QtCore import QRectF, Qt
from PyQt5 import QtCore 
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QMenu, 
                            QAction, QActionGroup, QApplication)
from PyQt5.QtGui import QPixmap, QCursor, QIcon
from .GraphicsItem import GraphicsItem

__version__ = '1.0'
__author__ = 'Steve Shillitoe'


PEN_CURSOR = 'CoreModules\\freeHandROI\\cursors\\pencil.png'
ERASOR_CURSOR = 'CoreModules\\freeHandROI\\cursors\\erasor.png'
ZOOM_IN = 1
ZOOM_OUT = -1


class GraphicsView(QGraphicsView):
    sigContextMenuDisplayed = QtCore.Signal()

    def __init__(self, zoomSlider, zoomLabel):
        super(GraphicsView, self).__init__()
        self.scene = QGraphicsScene(self)
        self._zoom = 0
        self.zoomSlider = zoomSlider
        self.zoomLabel = zoomLabel
        self.graphicsItem = None
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.zoomEnabled = False
        #Following commented out to display vertical and
        #horizontal scroll bars
        #self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.setDragMode(QGraphicsView.ScrollHandDrag)

    
    def contextMenuEvent(self, event):
        #display pop-up context menu when the right mouse button is pressed
        #as long as zoom is not enabled
        if not self.zoomEnabled:
            self.sigContextMenuDisplayed.emit()
            menu = QMenu()
            zoomIn = QAction('Zoom In', None)
            zoomOut = QAction('Zoom Out', None)
            zoomIn.triggered.connect(lambda: self.zoomImage(ZOOM_IN))
            zoomOut.triggered.connect(lambda: self.zoomImage(ZOOM_OUT))

            drawROI = QAction(QIcon(PEN_CURSOR), 'Draw', None)
            drawROI.setToolTip("Draw an ROI")
            drawROI.triggered.connect(lambda: self.drawROI())

            eraseROI  = QAction(QIcon(ERASOR_CURSOR), 'Erasor', None)
            eraseROI.setToolTip("Erase the ROI")
            eraseROI.triggered.connect(lambda: self.eraseROI())
            
            menu.addAction(zoomIn)
            menu.addAction(zoomOut)
            menu.addSeparator()
            menu.addAction(drawROI)
            menu.addAction(eraseROI)

            menu.exec_(event.globalPos())  


    def setZoomEnabled(self, boolValue):
        self.zoomEnabled = boolValue
        self.graphicsItem.zoomEnabled = boolValue


    def setImage(self, pixelArray, mask = None):
        try:
            if self.graphicsItem is not None:
                self.graphicsItem = None
                self.scene.clear()

            self.graphicsItem = GraphicsItem(pixelArray, mask)
            self.fitInView(self.graphicsItem, Qt.KeepAspectRatio) 
            self.reapplyZoom()
            self.scene.addItem(self.graphicsItem)
            self.graphicsItem.sigZoomIn.connect(lambda: self.zoomFromMouseClicks(ZOOM_IN))
            self.graphicsItem.sigZoomOut.connect(lambda: self.zoomFromMouseClicks(ZOOM_OUT))
        except Exception as e:
            print('Error in GraphicsView.setImage: ' + str(e))


    def reapplyZoom(self):
        if self._zoom > 0:
            factor = 1.25
            totalFactor = factor**self._zoom
            self.scale(totalFactor, totalFactor)


    def zoomFromMouseClicks(self, zoomValue):
        if self.zoomEnabled:
            self.zoomImage(zoomValue)
        

    def zoomImage(self, zoomValue):
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
        self.updateZoomSlider(increment)


    def updateZoomSlider(self, increment):
        #print("updateZoomSlider increment={}".format(increment))
        self.zoomSlider.blockSignals(True)
        if increment == 0:
            self.zoomSlider.setValue(0)
            self.zoomLabel.setText("<H4>100%</H4>")
        else:
            newValue = self.zoomSlider.value() + increment
            newZoomValue = 100 + (newValue * 25)
            self.zoomLabel.setText("<H4>" + str(newZoomValue) + "%</H4>")
            if self.zoomSlider.value() < self.zoomSlider.maximum() and increment > 0:
                self.zoomSlider.setValue(newValue)
            elif self.zoomSlider.value() > self.zoomSlider.minimum() and increment < 0:
                self.zoomSlider.setValue(newValue)
        self.zoomSlider.blockSignals(False)


    def wheelEvent(self, event):
        self.zoomImage(event.angleDelta().y())


    def fitItemInView(self, scale=True):
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


    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setDragMode(QGraphicsView.ScrollHandDrag)


    def drawROI(self):
        if not self.graphicsItem.drawEnabled:
            self.graphicsItem.drawEnabled = True
            self.setZoomEnabled(False)
            self.graphicsItem.eraseEnabled = False
        else:
            self.graphicsItem.drawEnabled = False
            #QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))


    def eraseROI(self):
        if not self.graphicsItem.eraseEnabled:
            self.graphicsItem.drawEnabled = False
            self.setZoomEnabled(False)
            self.graphicsItem.eraseEnabled = True
        else:
            self.graphicsItem.eraseEnabled = False
            #QApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
       
