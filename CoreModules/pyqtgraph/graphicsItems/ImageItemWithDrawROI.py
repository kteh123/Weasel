from __future__ import division

from ..Qt import QtGui, QtCore
from PyQt5.QtGui import qRgb
import numpy as np
import collections
from .. import functions as fn
from .. import debug as debug
from .GraphicsObject import GraphicsObject
from ..Point import Point
from matplotlib.path import Path as MplPath

__all__ = ['ImageItemWithDrawROI']


class ImageItemWithDrawROI(GraphicsObject):
    """
    **Bases:** :class:`GraphicsObject <pyqtgraph.GraphicsObject>`
    
    GraphicsObject displaying an image. Optimized for rapid update (ie video display).
    This item displays either a 2D numpy array (height, width) or
    a 3D array (height, width, RGBa). This array is optionally scaled (see 
    :func:`setLevels <pyqtgraph.ImageItemWithDrawROI.setLevels>`) and/or colored
    with a lookup table (see :func:`setLookupTable <pyqtgraph.ImageItemWithDrawROI.setLookupTable>`)
    before being displayed.
    
    ImageItemWithDrawROI is frequently used in conjunction with 
    :class:`HistogramLUTItem <pyqtgraph.HistogramLUTItem>` or 
    :class:`HistogramLUTWidget <pyqtgraph.HistogramLUTWidget>` to provide a GUI
    for controlling the levels and lookup table used to display the image.
    """
    
    # emits mean and standard deviation of image region bounded by a free hand drawn ROI
    #sigROIClosed = QtCore.Signal(object, object)   
    sigImageChanged = QtCore.Signal()
    sigRemoveRequested = QtCore.Signal(object)  # self; emitted when 'remove' is selected from context menu
    
    def __init__(self, image=None, **kargs):
        """
        See :func:`setImage <pyqtgraph.ImageItemWithDrawROI.setImage>` for all allowed initialization arguments.
        """
        GraphicsObject.__init__(self)
        self.menu = None
        self.image = None   ## original image data
        self.qimage = None  ## rendered image for display
        
        self.paintMode = None
        
        self.levels = None  ## [min, max] or [[redMin, redMax], ...]
        self.lut = None
        self.autoDownsample = False
        
        self.drawKernel = None
        self.border = None
        self.removable = False
        
        #Properties added by S Shillitoe November 2020
        #to support ROI freehand drawing
        #self.xCoord = None
        #self.yCoord = None
        #self.pixelColour = None
        #self.pixelValue = None
        #self.setAcceptHoverEvents(True)
        self.pathCoordsList = []
        self.last_x = None
        self.last_y = None
        self.start_x = None
        self.start_y = None
        self.drawRoi = False
        self.pixMap = None
        
        if image is not None:
            self.setImage(image, **kargs)
        else:
            self.setOpts(**kargs)
    

    def setAllowRoiDrawing(self, boolValue):
        self.drawRoi = boolValue


    def setCompositionMode(self, mode):
        """Change the composition mode of the item (see QPainter::CompositionMode
        in the Qt documentation). This is useful when overlaying multiple ImageItems.
        
        ============================================  ============================================================
        **Most common arguments:**
        QtGui.QPainter.CompositionMode_SourceOver     Default; image replaces the background if it
                                                      is opaque. Otherwise, it uses the alpha channel to blend
                                                      the image with the background.
        QtGui.QPainter.CompositionMode_Overlay        The image color is mixed with the background color to 
                                                      reflect the lightness or darkness of the background.
        QtGui.QPainter.CompositionMode_Plus           Both the alpha and color of the image and background pixels 
                                                      are added together.
        QtGui.QPainter.CompositionMode_Multiply       The output is the image color multiplied by the background.
        ============================================  ============================================================
        """
        self.paintMode = mode
        self.update()

    ## use setOpacity instead.
    #def setAlpha(self, alpha):
        #self.setOpacity(alpha)
        #self.updateImage()
        
    def setBorder(self, b):
        self.border = fn.mkPen(b)
        self.update()
        
    def width(self):
        if self.image is None:
            return None
        return self.image.shape[0]
        
    def height(self):
        if self.image is None:
            return None
        return self.image.shape[1]

    def boundingRect(self):
        if self.image is None:
            return QtCore.QRectF(0., 0., 0., 0.)
        return QtCore.QRectF(0., 0., float(self.width()), float(self.height()))

    #def setClipLevel(self, level=None):
        #self.clipLevel = level
        #self.updateImage()
        
    #def paint(self, p, opt, widget):
        #pass
        #if self.pixmap is not None:
            #p.drawPixmap(0, 0, self.pixmap)
            #print "paint"

    def setLevels(self, levels, update=True):
        """
        Set image scaling levels. Can be one of:
        
        * [blackLevel, whiteLevel]
        * [[minRed, maxRed], [minGreen, maxGreen], [minBlue, maxBlue]]
            
        Only the first format is compatible with lookup tables. See :func:`makeARGB <pyqtgraph.makeARGB>`
        for more details on how levels are applied.
        """
        self.levels = levels
        if update:
            self.updateImage()
        
    def getLevels(self):
        return self.levels
        #return self.whiteLevel, self.blackLevel

    def setLookupTable(self, lut, update=True):
        """
        Set the lookup table (numpy array) to use for this image. (see 
        :func:`makeARGB <pyqtgraph.makeARGB>` for more information on how this is used).
        Optionally, lut can be a callable that accepts the current image as an 
        argument and returns the lookup table to use.
        
        Ordinarily, this table is supplied by a :class:`HistogramLUTItem <pyqtgraph.HistogramLUTItem>`
        or :class:`GradientEditorItem <pyqtgraph.GradientEditorItem>`.
        """
        self.lut = lut
        if update:
            self.updateImage()

    def setAutoDownsample(self, ads):
        """
        Set the automatic downsampling mode for this ImageItemWithDrawROI.
        
        Added in version 0.9.9
        """
        self.autoDownsample = ads
        self.qimage = None
        self.update()

    def setOpts(self, update=True, **kargs):
        
        if 'lut' in kargs:
            self.setLookupTable(kargs['lut'], update=update)
        if 'levels' in kargs:
            self.setLevels(kargs['levels'], update=update)
        #if 'clipLevel' in kargs:
            #self.setClipLevel(kargs['clipLevel'])
        if 'opacity' in kargs:
            self.setOpacity(kargs['opacity'])
        if 'compositionMode' in kargs:
            self.setCompositionMode(kargs['compositionMode'])
        if 'border' in kargs:
            self.setBorder(kargs['border'])
        if 'removable' in kargs:
            self.removable = kargs['removable']
            self.menu = None
        if 'autoDownsample' in kargs:
            self.setAutoDownsample(kargs['autoDownsample'])
        if update:
            self.update()


    def setRect(self, rect):
        """Scale and translate the image to fit within rect (must be a QRect or QRectF)."""
        self.resetTransform()
        self.translate(rect.left(), rect.top())
        self.scale(rect.width() / self.width(), rect.height() / self.height())


    def clear(self):
        self.image = None
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
        self.update()


    def setImage(self, image=None, autoLevels=None, **kargs):
        """
        Update the image displayed by this item. For more information on how the image
        is processed before displaying, see :func:`makeARGB <pyqtgraph.makeARGB>`
        
        =================  =========================================================================
        **Arguments:**
        image              (numpy array) Specifies the image data. May be 2D (width, height) or 
                           3D (width, height, RGBa). The array dtype must be integer or floating
                           point of any bit depth. For 3D arrays, the third dimension must
                           be of length 3 (RGB) or 4 (RGBA).
        autoLevels         (bool) If True, this forces the image to automatically select 
                           levels based on the maximum and minimum values in the data.
                           By default, this argument is true unless the levels argument is
                           given.
        lut                (numpy array) The color lookup table to use when displaying the image.
                           See :func:`setLookupTable <pyqtgraph.ImageItemWithDrawROI.setLookupTable>`.
        levels             (min, max) The minimum and maximum values to use when rescaling the image
                           data. By default, this will be set to the minimum and maximum values 
                           in the image. If the image array has dtype uint8, no rescaling is necessary.
        opacity            (float 0.0-1.0)
        compositionMode    see :func:`setCompositionMode <pyqtgraph.ImageItemWithDrawROI.setCompositionMode>`
        border             Sets the pen used when drawing the image border. Default is None.
        autoDownsample     (bool) If True, the image is automatically downsampled to match the
                           screen resolution. This improves performance for large images and 
                           reduces aliasing.
        =================  =========================================================================
        """
        profile = debug.Profiler()

        gotNewData = False
        if image is None:
            if self.image is None:
                return
        else:
            gotNewData = True
            shapeChanged = (self.image is None or image.shape != self.image.shape)
            self.image = image.view(np.ndarray)
            if self.image.shape[0] > 2**15-1 or self.image.shape[1] > 2**15-1:
                if 'autoDownsample' not in kargs:
                    kargs['autoDownsample'] = True
            if shapeChanged:
                self.prepareGeometryChange()
                self.informViewBoundsChanged()

        profile()

        if autoLevels is None:
            if 'levels' in kargs:
                autoLevels = False
            else:
                autoLevels = True
        if autoLevels:
            img = self.image
            while img.size > 2**16:
                img = img[::2, ::2]
            mn, mx = img.min(), img.max()
            if mn == mx:
                mn = 0
                mx = 255
            kargs['levels'] = [mn,mx]

        profile()

        self.setOpts(update=False, **kargs)

        profile()

        self.qimage = None
        self.update()

        profile()

        if gotNewData:
            self.sigImageChanged.emit()


    def updateImage(self, *args, **kargs):
        ## used for re-rendering qimage from self.image.
        
        ## can we make any assumptions here that speed things up?
        ## dtype, range, size are all the same?
        defaults = {
            'autoLevels': False,
        }
        defaults.update(kargs)
        return self.setImage(*args, **defaults)

    def render(self):
        # Convert data to QImage for display.
        
        profile = debug.Profiler()
        if self.image is None or self.image.size == 0:
            return
        if isinstance(self.lut, collections.Callable):
            lut = self.lut(self.image)
        else:
            lut = self.lut

        if self.autoDownsample:
            # reduce dimensions of image based on screen resolution
            o = self.mapToDevice(QtCore.QPointF(0,0))
            x = self.mapToDevice(QtCore.QPointF(1,0))
            y = self.mapToDevice(QtCore.QPointF(0,1))
            w = Point(x-o).length()
            h = Point(y-o).length()
            xds = max(1, int(1/w))
            yds = max(1, int(1/h))
            image = fn.downsample(self.image, xds, axis=0)
            image = fn.downsample(image, yds, axis=1)
        else:
            image = self.image
        
        argb, alpha = fn.makeARGB(image.transpose((1, 0, 2)[:image.ndim]), lut=lut, levels=self.levels)
        self.qimage = fn.makeQImage(argb, alpha, transpose=False)

    def paint(self, p, *args):
        profile = debug.Profiler()
        if self.image is None:
            return
        if self.qimage is None:
            self.render()
            if self.qimage is None:
                return
            profile('render QImage')
        if self.paintMode is not None:
            p.setCompositionMode(self.paintMode)
            profile('set comp mode')

        p.drawImage(QtCore.QRectF(0,0,self.image.shape[0],self.image.shape[1]), self.qimage)
        profile('p.drawImage')
        if self.border is not None:
            p.setPen(self.border)
            p.drawRect(self.boundingRect())


    def save(self, fileName, *args):
        """Save this image to file. Note that this saves the visible image (after scale/color changes), not the original data."""
        if self.qimage is None:
            self.render()
        self.qimage.save(fileName, *args)

    def getHistogram(self, bins='auto', step='auto', targetImageSize=200, targetHistogramSize=500, **kwds):
        """Returns x and y arrays containing the histogram values for the current image.
        For an explanation of the return format, see numpy.histogram().
        
        The *step* argument causes pixels to be skipped when computing the histogram to save time.
        If *step* is 'auto', then a step is chosen such that the analyzed data has
        dimensions roughly *targetImageSize* for each axis.
        
        The *bins* argument and any extra keyword arguments are passed to 
        np.histogram(). If *bins* is 'auto', then a bin number is automatically
        chosen based on the image characteristics:
        
        * Integer images will have approximately *targetHistogramSize* bins, 
          with each bin having an integer width.
        * All other types will have *targetHistogramSize* bins.
        
        This method is also used when automatically computing levels.
        """
        if self.image is None:
            return None,None
        if step == 'auto':
            step = (np.ceil(self.image.shape[0] / targetImageSize),
                    np.ceil(self.image.shape[1] / targetImageSize))
        if np.isscalar(step):
            step = (step, step)
        stepData = self.image[::step[0], ::step[1]]
        
        if bins == 'auto':
            if stepData.dtype.kind in "ui":
                mn = stepData.min()
                mx = stepData.max()
                step = np.ceil((mx-mn) / 500.)
                bins = np.arange(mn, mx+1.01*step, step, dtype=np.int)
                if len(bins) == 0:
                    bins = [mn, mx]
            else:
                bins = 500

        kwds['bins'] = bins
        hist = np.histogram(stepData, **kwds)
        
        return hist[1][:-1], hist[0]


    def setPxMode(self, b):
        """
        Set whether the item ignores transformations and draws directly to screen pixels.
        If True, the item will not inherit any scale or rotation transformations from its
        parent items, but its position will be transformed as usual.
        (see GraphicsItem::ItemIgnoresTransformations in the Qt documentation)
        """
        self.setFlag(self.ItemIgnoresTransformations, b)
    
    def setScaledMode(self):
        self.setPxMode(False)

    def getPixmap(self):
        if self.qimage is None:
            self.render()
            if self.qimage is None:
                return None
        return QtGui.QPixmap.fromImage(self.qimage)
    
    def pixelSize(self):
        """return scene-size of a single pixel in the image"""
        br = self.sceneBoundingRect()
        if self.image is None:
            return 1,1
        return br.width()/self.width(), br.height()/self.height()
    
    def viewTransformChanged(self):
        if self.autoDownsample:
            self.qimage = None
            self.update()
    
    def hoverEvent(self, ev):
        if not ev.isExit() and self.drawKernel is not None and ev.acceptDrags(QtCore.Qt.LeftButton):
            ev.acceptClicks(QtCore.Qt.LeftButton) ## we don't use the click, but we also don't want anyone else to use it.
            ev.acceptClicks(QtCore.Qt.RightButton)
            print("Hover event if")
            #self.box.setBrush(fn.mkBrush('w'))
        elif not ev.isExit() and self.removable:
            print("Hover event elif")
            ev.acceptClicks(QtCore.Qt.RightButton)  ## accept context menu clicks
        #else:
            #self.box.setBrush(self.brush)
        #self.update()

    #def hoverMoveEvent(self, event):
    #    if self.isUnderMouse():
    #        self.xCoord = int(event.pos().x())
    #        self.yCoord = int(event.pos().y())
    #    else:
    #        self.xCoord = None
    #        self.yCoord = None
    #        #qimage = self.getPixmap().toImage()
    #       # self.pixelColour = qimage.pixelColor(self.xCoord,  self.yCoord ).getRgb()  #[:-1]
    #       # self.pixelValue = qimage.pixelColor(self.xCoord,  self.yCoord ).value()
    #    #    #print(("Pixel value {}, pixel colour {} @ X:{}, Y:{}".format(pixelValue, 
    #         #                                                                         pixelColour,
    #          #                                                                        xCoord, 
    #           #                                                                       yCoord)))
    #             #                                                         yCoord))
    
        
    def mouseMoveEvent(self, event):
        if self.drawRoi:
            if self.last_x is None: # First event.
                self.last_x = (event.pos()).x()
                self.last_y = (event.pos()).y()
                self.start_x = int(self.last_x)
                self.start_y = int(self.last_y)
                return #  Ignore the first time.
            self.pixMap = self.getPixmap()
            self.myPainter = QtGui.QPainter(self.pixMap)
            p = self.myPainter.pen()
            p.setWidth(1) #1 pixel
            p.setColor(QtGui.QColor("#FF0000")) #red
            self.myPainter.setPen(p)
            #Draws a line from (x1 , y1 ) to (x2 , y2 ).
            xCoord = event.pos().x()
            yCoord = event.pos().y()
            self.myPainter.drawLine(self.last_x, self.last_y, xCoord, yCoord)
            self.myPainter.end() 
            #The pixmap has changed (it was drawn on), so update it
            #back to the original image
            self.qimage =  self.getPixmap().toImage()
            self.update()

            # Update the origin for next time.
            self.last_x = xCoord
            self.last_y = yCoord
            self.pathCoordsList.append([self.last_x, self.last_y])
    

   # def mouseDragEvent(self, ev):
    #    pass


    def mousePressEvent(self, event): 
        #This function is necessary to activate mouse move events
        pass


    def mouseReleaseEvent(self, ev):
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
                    self.pixMap = self.getPixmap()
                    self.myPainter = QtGui.QPainter(self.pixMap)
                    p = self.myPainter.pen()
                    p.setWidth(1) #1 pixel
                    p.setColor(QtGui.QColor("#FF0000")) #red
                    self.myPainter.setPen(p)
                    #self.myPainter.setRenderHint(QtGui.QPainter.Antialiasing)
                    self.myPainter.drawLine(self.last_x, self.last_y, self.start_x, self.start_y)
                    self.myPainter.end()
                    self.qimage =  self.getPixmap().toImage()
                    #self.update()
                mask = self.getMask(self.pathCoordsList)
                listCoords = self.getListRoiInnerPoints(mask)
                self.fillFreeHandRoi(listCoords)
                self.update()
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
            #print("pixelColour ={}".format(pixelColour))
            pixelRGB =  QtGui.QColor(pixelColour).getRgb()
            redVal = pixelRGB[0]
            greenVal = pixelRGB[1]
            blueVal = pixelRGB[2]
            if greenVal == 255 and blueVal == 255:
                #This pixel would be white if red channel set to 255
                #so set the green and blue channels to zero
                greenVal = blueVal = 0
            value = qRgb(255, greenVal, blueVal)
            #print("greenVal ={}, blueVal={}".format(greenVal, blueVal))
            self.qimage.setPixel(x, y, value)


    #def getRoiMeanAndStd(self, mask):
    #    localImage = np.copy(self.image)
    #    mean = round(np.mean(np.extract(mask, localImage)), 3)
    #    std = round(np.std(np.extract(mask, localImage)), 3)
    #    return mean, std


    def getListRoiInnerPoints(self, mask):
        #result = np.nonzero(mask)
        result = np.where(mask == True)
        return list(zip(result[0], result[1]))


    def getMask(self, roiLineCoords):
            ny, nx = np.shape(self.image)
            #print("roiLineCoords ={}".format(roiLineCoords))
            # Create vertex coordinates for each grid cell...
            # (<0,0> is at the top left of the grid in this system)
            x, y = np.meshgrid(np.arange(nx), np.arange(ny))
            x, y = x.flatten(), y.flatten()
            points = np.vstack((x, y)).T #points = every [x,y] pair within the original image
        
            #print("roiLineCoords={}".format(roiLineCoords))
            roiPath = MplPath(roiLineCoords)
            #print("roiPath={}".format(roiPath))
            mask = roiPath.contains_points(points).reshape((ny, nx))
            return mask


    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            if self.raiseContextMenu(ev):
                ev.accept()
        if self.drawKernel is not None and ev.button() == QtCore.Qt.LeftButton:
            self.drawAt(ev.pos(), ev)


    def raiseContextMenu(self, ev):
        menu = self.getMenu()
        if menu is None:
            return False
        menu = self.scene().addParentContextMenus(self, menu, ev)
        pos = ev.screenPos()
        menu.popup(QtCore.QPoint(pos.x(), pos.y()))
        return True


    def getMenu(self):
        if self.menu is None:
            if not self.removable:
                return None
            self.menu = QtGui.QMenu()
            self.menu.setTitle("Image")
            remAct = QtGui.QAction("Remove image", self.menu)
            remAct.triggered.connect(self.removeClicked)
            self.menu.addAction(remAct)
            self.menu.remAct = remAct
        return self.menu
        
        
    def tabletEvent(self, ev):
        print(ev.device())
        print(ev.pointerType())
        print(ev.pressure())
    

    def drawAt(self, pos, ev=None):
        pos = [int(pos.x()), int(pos.y())]
        #print ("drawAt {}".format(pos))
        dk = self.drawKernel
        kc = self.drawKernelCenter
        sx = [0,dk.shape[0]]
        sy = [0,dk.shape[1]]
        tx = [pos[0] - kc[0], pos[0] - kc[0]+ dk.shape[0]]
        ty = [pos[1] - kc[1], pos[1] - kc[1]+ dk.shape[1]]
        #print("sx{}, sy{}, tx{}, ty{}".format(sx, sy, tx, ty))
        for i in [0,1]:
            dx1 = -min(0, tx[i])
            dx2 = min(0, self.image.shape[0]-tx[i])
            tx[i] += dx1+dx2
            sx[i] += dx1+dx2

            dy1 = -min(0, ty[i])
            dy2 = min(0, self.image.shape[1]-ty[i])
            ty[i] += dy1+dy2
            sy[i] += dy1+dy2

        ts = (slice(tx[0],tx[1]), slice(ty[0],ty[1]))
        ss = (slice(sx[0],sx[1]), slice(sy[0],sy[1]))

        mask = self.drawMask
        src = dk
        
        if isinstance(self.drawMode, collections.Callable):
            self.drawMode(dk, self.image, mask, ss, ts, ev)
        else:
            src = src[ss]
            if self.drawMode == 'set':
                if mask is not None:
                    mask = mask[ss]
                    print("Before self.image[ts]={}".format(self.image[ts]))
                    self.image[ts] = self.image[ts] * (1-mask) + src * mask
                    print("After self.image[ts]={}".format(self.image[ts]))
                else:
                    self.image[ts] = src
            elif self.drawMode == 'add':
                self.image[ts] += src
            else:
                raise Exception("Unknown draw mode '%s'" % self.drawMode)
            self.updateImage()
        

    def setDrawKernel(self, kernel=None, mask=None, center=(0,0), mode='set'):
        self.drawKernel = kernel
        self.drawKernelCenter = center
        self.drawMode = mode
        self.drawMask = mask

    def removeClicked(self):
        ## Send remove event only after we have exited the menu event handler
        self.removeTimer = QtCore.QTimer()
        self.removeTimer.timeout.connect(self.emitRemoveRequested)
        self.removeTimer.start(0)

    def emitRemoveRequested(self):
        self.removeTimer.timeout.disconnect(self.emitRemoveRequested)
        self.sigRemoveRequested.emit(self)
