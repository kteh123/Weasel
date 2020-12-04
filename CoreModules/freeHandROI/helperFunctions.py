import numpy as np
from PyQt5 import QtGui, QtCore


CONFIG_OPTIONS = {
    'useOpenGL': useOpenGL, ## by default, this is platform-dependent (see widgets/GraphicsView). Set to True or False to explicitly enable/disable opengl.
    'leftButtonPan': True,  ## if false, left button drags a rubber band for zooming in viewbox
    # foreground/background take any arguments to the 'mkColor' in /pyqtgraph/functions.py
    'foreground': 'd',  ## default foreground color for axes, labels, etc.
    'background': 'k',        ## default background for GraphicsWidget
    'antialias': False,
    'editorCommand': None,  ## command used to invoke code editor from ConsoleWidgets
    'useWeave': False,       ## Use weave to speed up some operations, if it is available
    'weaveDebug': False,    ## Print full error message if weave compile fails
    'exitCleanup': True,    ## Attempt to work around some exit crash bugs in PyQt and PySide
    'enableExperimental': False, ## Enable experimental features (the curious can search for this key in the code)
    'crashWarning': False,  # If True, print warnings about situations that may result in a crash
    'imageAxisOrder': 'col-major',  # For 'row-major', image data is expected in the standard (row, col) order.
                                 # For 'col-major', image data is expected in reversed (col, row) order.
                                 # The default is 'col-major' for backward compatibility, but this may
                                 # change in the future.
} 


def setConfigOption(opt, value):
    global CONFIG_OPTIONS
    if opt not in CONFIG_OPTIONS:
        raise KeyError('Unknown configuration option "%s"' % opt)
    if opt == 'imageAxisOrder' and value not in ('row-major', 'col-major'):
        raise ValueError('imageAxisOrder must be either "row-major" or "col-major"')
    CONFIG_OPTIONS[opt] = value

def setConfigOptions(**opts):
    """Set global configuration options. 
    
    Each keyword argument sets one global option. 
    """
    for k,v in opts.items():
        setConfigOption(k, v)

def getConfigOption(opt):
    """Return the value of a single global configuration option.
    """
    return CONFIG_OPTIONS[opt]


def rescaleData(data, scale, offset, dtype=None, clip=None):
    """Return data rescaled and optionally cast to a new dtype::
    
        data => (data-offset) * scale
        
    """
    if dtype is None:
        dtype = data.dtype
    else:
        dtype = np.dtype(dtype)
    
    try:
        if not getConfigOption('useWeave'):
            raise Exception('Weave is disabled; falling back to slower version.')
        try:
            import scipy.weave
        except ImportError:
            raise Exception('scipy.weave is not importable; falling back to slower version.')
        
        ## require native dtype when using weave
        if not data.dtype.isnative:
            data = data.astype(data.dtype.newbyteorder('='))
        if not dtype.isnative:
            weaveDtype = dtype.newbyteorder('=')
        else:
            weaveDtype = dtype
        
        newData = np.empty((data.size,), dtype=weaveDtype)
        flat = np.ascontiguousarray(data).reshape(data.size)
        size = data.size
        
        code = """
        double sc = (double)scale;
        double off = (double)offset;
        for( int i=0; i<size; i++ ) {
            newData[i] = ((double)flat[i] - off) * sc;
        }
        """
        scipy.weave.inline(code, ['flat', 'newData', 'size', 'offset', 'scale'], compiler='gcc')
        if dtype != weaveDtype:
            newData = newData.astype(dtype)
        data = newData.reshape(data.shape)
    except:
        if getConfigOption('useWeave'):
            if getConfigOption('weaveDebug'):
                debug.printExc("Error; disabling weave.")
            setConfigOptions(useWeave=False)
        
        #p = np.poly1d([scale, -offset*scale])
        #d2 = p(data)
        d2 = data - float(offset)
        d2 *= scale
        
        # Clip before converting dtype to avoid overflow
        if dtype.kind in 'ui':
            lim = np.iinfo(dtype)
            if clip is None:
                # don't let rescale cause integer overflow
                d2 = np.clip(d2, lim.min, lim.max)
            else:
                d2 = np.clip(d2, max(clip[0], lim.min), min(clip[1], lim.max))
        else:
            if clip is not None:
                d2 = np.clip(d2, *clip)
        data = d2.astype(dtype)
    return data

def makeARGB(data, lut=None, levels=None, scale=None, useRGBA=False): 
    """ 
    Convert an array of values into an ARGB array suitable for building QImages,
    OpenGL textures, etc.
    
    Returns the ARGB array (unsigned byte) and a boolean indicating whether
    there is alpha channel data. This is a two stage process:
    
        1) Rescale the data based on the values in the *levels* argument (min, max).
        2) Determine the final output by passing the rescaled values through a
           lookup table.
   
    Both stages are optional.
    
    ============== ==================================================================================
    **Arguments:**
    data           numpy array of int/float types. If 
    levels         List [min, max]; optionally rescale data before converting through the
                   lookup table. The data is rescaled such that min->0 and max->*scale*::
                   
                      rescaled = (clip(data, min, max) - min) * (*scale* / (max - min))
                   
                   It is also possible to use a 2D (N,2) array of values for levels. In this case,
                   it is assumed that each pair of min,max values in the levels array should be 
                   applied to a different subset of the input data (for example, the input data may 
                   already have RGB values and the levels are used to independently scale each 
                   channel). The use of this feature requires that levels.shape[0] == data.shape[-1].
    scale          The maximum value to which data will be rescaled before being passed through the 
                   lookup table (or returned if there is no lookup table). By default this will
                   be set to the length of the lookup table, or 255 if no lookup table is provided.
    lut            Optional lookup table (array with dtype=ubyte).
                   Values in data will be converted to color by indexing directly from lut.
                   The output data shape will be input.shape + lut.shape[1:].
                   Lookup tables can be built using ColorMap or GradientWidget.
    useRGBA        If True, the data is returned in RGBA order (useful for building OpenGL textures). 
                   The default is False, which returns in ARGB order for use with QImage 
                   (Note that 'ARGB' is a term used by the Qt documentation; the *actual* order 
                   is BGRA).
    ============== ==================================================================================
    """

    if data.ndim not in (2, 3):
        raise TypeError("data must be 2D or 3D")
    if data.ndim == 3 and data.shape[2] > 4:
        raise TypeError("data.shape[2] must be <= 4")
    
    if lut is not None and not isinstance(lut, np.ndarray):
        lut = np.array(lut)
    
    if levels is None:
        # automatically decide levels based on data dtype
        if data.dtype.kind == 'u':
            levels = np.array([0, 2**(data.itemsize*8)-1])
        elif data.dtype.kind == 'i':
            s = 2**(data.itemsize*8 - 1)
            levels = np.array([-s, s-1])
        elif data.dtype.kind == 'b':
            levels = np.array([0,1])
        else:
            raise Exception('levels argument is required for float input types')
    if not isinstance(levels, np.ndarray):
        levels = np.array(levels)
    if levels.ndim == 1:
        if levels.shape[0] != 2:
            raise Exception('levels argument must have length 2')
    elif levels.ndim == 2:
        if lut is not None and lut.ndim > 1:
            raise Exception('Cannot make ARGB data when both levels and lut have ndim > 2')
        if levels.shape != (data.shape[-1], 2):
            raise Exception('levels must have shape (data.shape[-1], 2)')
    else:
        raise Exception("levels argument must be 1D or 2D (got shape=%s)." % repr(levels.shape))

    

    # Decide on maximum scaled value
    if scale is None:
        if lut is not None:
            scale = lut.shape[0] - 1
        else:
            scale = 255.

    # Decide on the dtype we want after scaling
    if lut is None:
        dtype = np.ubyte
    else:
        dtype = np.min_scalar_type(lut.shape[0]-1)
            
    # Apply levels if given
    if levels is not None:
        if isinstance(levels, np.ndarray) and levels.ndim == 2:
            # we are going to rescale each channel independently
            if levels.shape[0] != data.shape[-1]:
                raise Exception("When rescaling multi-channel data, there must be the same number of levels as channels (data.shape[-1] == levels.shape[0])")
            newData = np.empty(data.shape, dtype=int)
            for i in range(data.shape[-1]):
                minVal, maxVal = levels[i]
                if minVal == maxVal:
                    maxVal += 1e-16
                newData[...,i] = rescaleData(data[...,i], scale/(maxVal-minVal), minVal, dtype=dtype)
            data = newData
        else:
            # Apply level scaling unless it would have no effect on the data
            minVal, maxVal = levels
            if minVal != 0 or maxVal != scale:
                if minVal == maxVal:
                    maxVal += 1e-16
                data = rescaleData(data, scale/(maxVal-minVal), minVal, dtype=dtype)
            

    

    # apply LUT if given
    if lut is not None:
        data = applyLookupTable(data, lut)
    else:
        if data.dtype is not np.ubyte:
            data = np.clip(data, 0, 255).astype(np.ubyte)

    

    # this will be the final image array
    imgData = np.empty(data.shape[:2]+(4,), dtype=np.ubyte)

    

    # decide channel order
    if useRGBA:
        order = [0,1,2,3] # array comes out RGBA
    else:
        order = [2,1,0,3] # for some reason, the colors line up as BGR in the final image.
        
    # copy data into image array
    if data.ndim == 2:
        # This is tempting:
        #   imgData[..., :3] = data[..., np.newaxis]
        # ..but it turns out this is faster:
        for i in range(3):
            imgData[..., i] = data
    elif data.shape[2] == 1:
        for i in range(3):
            imgData[..., i] = data[..., 0]
    else:
        for i in range(0, data.shape[2]):
            imgData[..., i] = data[..., order[i]] 
        
    
    
    # add opaque alpha channel if needed
    if data.ndim == 2 or data.shape[2] == 3:
        alpha = False
        imgData[..., 3] = 255
    else:
        alpha = True

    return imgData, alpha


def makeQImage(imgData, alpha=None, copy=True, transpose=True):
    """
    Turn an ARGB array into QImage.
    By default, the data is copied; changes to the array will not
    be reflected in the image. The image will be given a 'data' attribute
    pointing to the array which shares its data to prevent python
    freeing that memory while the image is in use.
    
    ============== ===================================================================
    **Arguments:**
    imgData        Array of data to convert. Must have shape (width, height, 3 or 4) 
                   and dtype=ubyte. The order of values in the 3rd axis must be 
                   (b, g, r, a).
    alpha          If True, the QImage returned will have format ARGB32. If False,
                   the format will be RGB32. By default, _alpha_ is True if
                   array.shape[2] == 4.
    copy           If True, the data is copied before converting to QImage.
                   If False, the new QImage points directly to the data in the array.
                   Note that the array must be contiguous for this to work
                   (see numpy.ascontiguousarray).
    transpose      If True (the default), the array x/y axes are transposed before 
                   creating the image. Note that Qt expects the axes to be in 
                   (height, width) order whereas pyqtgraph usually prefers the 
                   opposite.
    ============== ===================================================================    
    """
    ## create QImage from buffer
    
    ## If we didn't explicitly specify alpha, check the array shape.
    if alpha is None:
        alpha = (imgData.shape[2] == 4)
        
    copied = False
    if imgData.shape[2] == 3:  ## need to make alpha channel (even if alpha==False; QImage requires 32 bpp)
        if copy is True:
            d2 = np.empty(imgData.shape[:2] + (4,), dtype=imgData.dtype)
            d2[:,:,:3] = imgData
            d2[:,:,3] = 255
            imgData = d2
            copied = True
        else:
            raise Exception('Array has only 3 channels; cannot make QImage without copying.')
    
    if alpha:
        imgFormat = QtGui.QImage.Format_ARGB32
    else:
        imgFormat = QtGui.QImage.Format_RGB32
        
    if transpose:
        imgData = imgData.transpose((1, 0, 2))  ## QImage expects the row/column order to be opposite

    

    if not imgData.flags['C_CONTIGUOUS']:
        if copy is False:
            extra = ' (try setting transpose=False)' if transpose else ''
            raise Exception('Array is not contiguous; cannot make QImage without copying.'+extra)
        imgData = np.ascontiguousarray(imgData)
        copied = True
        
    if copy is True and copied is False:
        imgData = imgData.copy()
        
    if USE_PYSIDE:
        ch = ctypes.c_char.from_buffer(imgData, 0)
        img = QtGui.QImage(ch, imgData.shape[1], imgData.shape[0], imgFormat)
    else:
        #addr = ctypes.addressof(ctypes.c_char.from_buffer(imgData, 0))
        ## PyQt API for QImage changed between 4.9.3 and 4.9.6 (I don't know exactly which version it was)
        ## So we first attempt the 4.9.6 API, then fall back to 4.9.3
        #addr = ctypes.c_char.from_buffer(imgData, 0)
        #try:
            #img = QtGui.QImage(addr, imgData.shape[1], imgData.shape[0], imgFormat)
        #except TypeError:  
            #addr = ctypes.addressof(addr)
            #img = QtGui.QImage(addr, imgData.shape[1], imgData.shape[0], imgFormat)
        try:
            img = QtGui.QImage(imgData.ctypes.data, imgData.shape[1], imgData.shape[0], imgFormat)
        except:
            if copy:
                # does not leak memory, is not mutable
                img = QtGui.QImage(buffer(imgData), imgData.shape[1], imgData.shape[0], imgFormat)
            else:
                # mutable, but leaks memory
                img = QtGui.QImage(memoryview(imgData), imgData.shape[1], imgData.shape[0], imgFormat)
                
    img.data = imgData
    return img
