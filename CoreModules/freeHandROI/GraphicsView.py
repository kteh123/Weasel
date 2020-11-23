from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene


from .GraphicsItem import GraphicsItem


class GraphicsView(QGraphicsView):
    def __init__(self):
        super(GraphicsView, self).__init__()
        self.scene = QGraphicsScene(self)
        self._zoom = 0
        self.graphicsItem = None
        
        #self.myScale = 2
        #self.graphicsItem.setScale(self.myScale)
        self.fitInView()

        self.setScene(self.scene)
        #self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        #self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
       # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        


    def setImage(self, pixelArray):
        try:
            if self.graphicsItem is not None:
                self.graphicsItem = None

            self.graphicsItem = GraphicsItem(pixelArray)
            self.scene.addItem(self.graphicsItem)
        except Exception as e:
            print('Error in GraphicsView.setImage: ' + str(e))

    def returnGraphicsItem(self):
        return self.graphicsItem


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
            self.fitInView()
        else:
            self._zoom = 0


    def fitInView(self, scale=True):
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
