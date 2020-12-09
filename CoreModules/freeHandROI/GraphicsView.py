from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from .GraphicsItem import GraphicsItem

__version__ = '1.0'
__author__ = 'Steve Shillitoe'

class GraphicsView(QGraphicsView):
    def __init__(self):
        super(GraphicsView, self).__init__()
        self.scene = QGraphicsScene(self)
        self._zoom = 0
        self.graphicsItem = None
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        #self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
       # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.setDragMode(QGraphicsView.ScrollHandDrag)


    def setImage(self, pixelArray):
        try:
            if self.graphicsItem is not None:
                self.graphicsItem = None

            self.graphicsItem = GraphicsItem(pixelArray)
            self.fitInView(self.graphicsItem, Qt.KeepAspectRatio) 
            self.scene.addItem(self.graphicsItem)
        except Exception as e:
            print('Error in GraphicsView.setImage: ' + str(e))


    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.25
            self._zoom += 1
        else:
            factor = 0.8
            self._zoom -= 1
        if self._zoom > 0:
            self.scale(factor, factor)
        elif self._zoom == 0:
            self.fitItemInView()
        else:
            self._zoom = 0


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
