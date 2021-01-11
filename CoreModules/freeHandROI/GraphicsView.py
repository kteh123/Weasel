from PyQt5.QtCore import QRectF, Qt,  QCoreApplication
from PyQt5 import QtCore 
from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, QMenu, QMessageBox,
                            QAction, QActionGroup, QApplication)
from PyQt5.QtGui import QPixmap, QCursor, QIcon
from .GraphicsItem import GraphicsItem
from .ROI_Storage import ROIs 
import logging
logger = logging.getLogger(__name__)

__version__ = '1.0'
__author__ = 'Steve Shillitoe'


PEN_CURSOR = 'CoreModules\\freeHandROI\\cursors\\pencil.png'
ERASOR_CURSOR = 'CoreModules\\freeHandROI\\cursors\\erasor.png'
ZOOM_IN = 1
ZOOM_OUT = -1


class GraphicsView(QGraphicsView):
    sigContextMenuDisplayed = QtCore.Signal()
    sigReloadImage =  QtCore.Signal()
    sigROIDeleted = QtCore.Signal()


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
        self.roiCombo = None
        self.dictROIs = ROIs()
        self.menu = QMenu()
        #Following commented out to display vertical and
        #horizontal scroll bars
        #self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.setDragMode(QGraphicsView.ScrollHandDrag)

    def loadROI(self, regionName):
        self.roiCombo.setCurrentText(regionName) 
        self.sigReloadImage.emit()


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


    def contextMenuEvent(self, event):
        #display pop-up context menu when the right mouse button is pressed
        #as long as zoom is not enabled
        if not self.zoomEnabled:
            self.menu.clear()
            self.sigContextMenuDisplayed.emit()
            zoomIn = QAction('Zoom In', None)
            zoomOut = QAction('Zoom Out', None)
            zoomIn.triggered.connect(lambda: self.zoomImage(ZOOM_IN))
            zoomOut.triggered.connect(lambda: self.zoomImage(ZOOM_OUT))

            drawROI = QAction(QIcon(PEN_CURSOR), 'Draw', None)
            drawROI.setToolTip("Draw an ROI")
            drawROI.triggered.connect(self.drawROI)

            eraseROI  = QAction(QIcon(ERASOR_CURSOR), 'Erasor', None)
            eraseROI.setToolTip("Erase the ROI")
            eraseROI.triggered.connect(self.eraseROI)

            newROI  = QAction('New ROI', None)
            newROI.setToolTip("Create a new ROI")
            newROI.triggered.connect(self.newROI)

            resetROI  = QAction('Reset ROI', None)
            resetROI.setToolTip("Clear drawn ROI from the image")
            resetROI.triggered.connect(self.resetROI)

            deleteROI  = QAction('Delete ROI', None)
            deleteROI.setToolTip("Delete drawn ROI from the image")
            deleteROI.triggered.connect(self.deleteROI)
            
            self.menu.addAction(zoomIn)
            self.menu.addAction(zoomOut)
            self.menu.addSeparator()
            self.menu.addAction(drawROI)
            self.menu.addAction(eraseROI)
            self.menu.addSeparator()
            self.menu.addAction(newROI)
            self.menu.addAction(resetROI)
            self.menu.addAction(deleteROI)
            #self.menu.addSeparator()
            #roiMenu = self.menu.addMenu("ROIs")
            #.addRegionsToContextMenu(roiMenu)
            self.menu.exec_(event.globalPos())  


    def addRegionsToContextMenu(self, roiMenu):
        try:
            regions = self.dictROIs.getListOfRegions()
            for region in regions:
                regionAction = QAction(str(region), None)
                function = self.loadROI(str(region))
                regionAction.triggered.connect(lambda:function)
                roiMenu.addAction(regionAction)
        except Exception as e:
            print('Error in GraphicsView.addRegionsToContextMenu: ' + str(e))


    def drawROI(self):
        if not self.graphicsItem.drawEnabled:
            self.graphicsItem.drawEnabled = True
            self.setZoomEnabled(False)
            self.graphicsItem.eraseEnabled = False
        else:
            self.graphicsItem.drawEnabled = False


    def eraseROI(self):
        if not self.graphicsItem.eraseEnabled:
            self.graphicsItem.drawEnabled = False
            self.setZoomEnabled(False)
            self.graphicsItem.eraseEnabled = True
        else:
            self.graphicsItem.eraseEnabled = False
       

    def newROI(self):
        try:
            logger.info("GraphicsView.newROI called")
            if self.dictROIs.hasRegionGotMask(self.roiCombo.currentText()):
                self.roiCombo.blockSignals(True)
                newRegion = self.dictROIs.getNextRegionName()
                self.roiCombo.addItem(newRegion)
                self.roiCombo.setCurrentIndex(self.roiCombo.count() - 1)
                self.roiCombo.blockSignals(False)
                self.graphicsItem.reloadImage()
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("Add new ROI")
                msgBox.setText(
                    "You must add ROIs to the current region before creating a new one")
                msgBox.exec()
        except Exception as e:
            print('Error in GraphicsView.newROI: ' + str(e))


    def resetROI(self):
        try:
            logger.info("GraphicsView.resetROI called")
            self.dictROIs.deleteMask(self.roiCombo.currentText())
            self.sigReloadImage.emit()
        except Exception as e:
            print('Error in GraphicsView.resetROI: ' + str(e))


    def deleteROI(self):
        try:
            logger.info("GraphicsView.deleteROI called")
            if self.roiCombo is not None:
                regionName = self.roiCombo.currentText()
                if regionName:
                    self.dictROIs.deleteMask(regionName)
                    for item in self.menu.actions():
                        if item.text() == regionName:
                            self.menu.removeAction(item)
                            break
                    self.sigROIDeleted.emit()
        except Exception as e:
            print('Error in GraphicsView.deleteROI: ' + str(e))