import numpy as np
import pydicom
from skimage.transform import resize


#INSERT A METHOD TO DEAL WITH MOSAIC PIXEL ARRAYS
#INSERT MOSAIC IMAGE CONDITION HERE / OR AT IMAGINGTOOLS.PY

def resizePixelArray(pixelArray, pixelSpacing, reconstPixel = None):
    """Resizes the given array, using reconstPixel as reference of the resizing""" 
 
    # Resample Data / Don't forget to resample the 128x128 of GE / Will have to put this in a separate file
    # This is so that data shares the same resolution and sizing. Maybe this should be a separate function and a save method
    #fraction = reconstPixel / datasetList[0].PixelSpacing[0]
    if reconstPixel is not None:
        fraction = reconstPixel / pixelSpacing
    else:
        fraction = 1
    
    if len(np.shape(pixelArray)) == 4:
        pixelArray = resize(pixelArray, (pixelArray.shape[0] // fraction, pixelArray.shape[1] // fraction, pixelArray.shape[2], pixelArray.shape[3]), anti_aliasing=True)
    elif len(np.shape(pixelArray)) == 3:
        pixelArray = resize(pixelArray, (pixelArray.shape[0] // fraction, pixelArray.shape[1] // fraction, pixelArray.shape[2]), anti_aliasing=True)

    return pixelArray