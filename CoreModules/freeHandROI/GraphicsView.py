from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from .GraphicsItem import GraphicsItem

__version__ = '1.0'
__author__ = 'Steve Shillitoe'

class GraphicsView(QGraphicsView):
    def __init__(self, zoomSlider):
        super(GraphicsView, self).__init__()
        self.scene = QGraphicsScene(self)
        self._zoom = 0
        self.zoomSlider = zoomSlider
        self.graphicsItem = None
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        #self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
       # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.setDragMode(QGraphicsView.ScrollHandDrag)


    def setImage(self, pixelArray, mask = None):
        try:
            if self.graphicsItem is not None:
                self.graphicsItem = None
                self.scene.clear()

            self.graphicsItem = GraphicsItem(pixelArray, mask)
            self.fitInView(self.graphicsItem, Qt.KeepAspectRatio) 
            self.reapplyZoom()
            self.scene.addItem(self.graphicsItem)
        except Exception as e:
            print('Error in GraphicsView.setImage: ' + str(e))


    def reapplyZoom(self):
        if self._zoom > 0:
            factor = 1.25
            totalFactor = factor**self._zoom
            self.scale(totalFactor, totalFactor)
            

    def zoomImage(self, zoomValue):
        if zoomValue > 0:
            factor = 1.25
            self._zoom += 1
            print("+self._zoom={}".format(self._zoom))
            increment = 1
        else:
            factor = 0.8
            self._zoom -= 1
            increment = -1
            print("-self._zoom={}".format(self._zoom))
        if self._zoom > 0:
            self.scale(factor, factor)
        elif self._zoom == 0:
            self.fitItemInView()
            increment = 0
        else:
            self._zoom = 0
            increment = 0

        return increment


    def wheelEvent(self, event):
        increment = self.zoomImage(event.angleDelta().y())
        if increment == 0:
            self.zoomSlider.setValue(0)
        else:
            if self.zoomSlider.value() < self.zoomSlider.maximum() and increment > 0:
                self.zoomSlider.setValue(self.zoomSlider.value() + increment)
            elif self.zoomSlider.value() > self.zoomSlider.minimum() and increment < 0:
                self.zoomSlider.setValue(self.zoomSlider.value() + increment)


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
