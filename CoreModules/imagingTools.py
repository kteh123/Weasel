import numpy as np
import pydicom
import scipy.ndimage
from skimage.transform import resize
from skimage.restoration import unwrap_phase

#INSERT A METHOD TO DEAL WITH MOSAIC PIXEL ARRAYS

def unWrapPhase(pixelArray):
    """
    From an image wrapped to lie in the interval [-pi, pi],
    this function recovers the original, unwrapped image.
    Read references in
    https://scikit-image.org/docs/dev/auto_examples/filters/plot_phase_unwrap.html

    Parameters
    ----------
    pixelArray : np.ndarray
        A 2D/3D array containing the phase image.

    Returns
    -------
    np.ndarray with the phase of pixelArray unwrapped.
    """
    wrappedPhase = np.angle(np.exp(2j * pixelArray))
    return unwrap_phase(wrappedPhase)


def convertToPiRange(pixelArray):
    """
    Rescale the image values to the interval [-pi, pi].

    Parameters
    ----------
    pixel_array : np.ndarray

    Returns
    -------
    radians_array : np.ndarray
        An array containing with the same shape as pixel_array
        scaled to the range [-pi, pi].
    """
    if (np.amax(pixelArray) > 3.2) or (np.amin(pixelArray) < -3.2):
        # Scale the image to the interval [-pi, pi]. 
        # The value 3.2 was chosen instead of np.pi in order to give some margin 
        piArray = np.pi * np.ones(np.shape(pixelArray))
        minArray = np.amin(pixelArray) * np.ones(np.shape(pixelArray))
        maxArray = np.amax(pixelArray) * np.ones(np.shape(pixelArray))
        radiansArray = (2.0 * piArray * (pixelArray - minArray) / (maxArray - minArray)) - piArray
    else:
        # It means it's already on the interval [-pi, pi]
        radiansArray = pixelArray
    return radiansArray


def invertAlgorithm(pixelArray, dataset):
    try:
        totalBytes = dataset.BitsAllocated
        return np.invert(pixelArray.astype('int' + str(totalBytes)))
    except Exception as e:
        print('Error in function imagingTools.invertAlgorithm: ' + str(e))


def squareAlgorithm(pixelArray, dataset = None):
    try:
        return np.square(pixelArray)
    except Exception as e:
        print('Error in function imagingTools.squareAlgorithm: ' + str(e))


def gaussianFilter(pixelArray, sigma):
    try:
        return scipy.ndimage.gaussian_filter(pixelArray, sigma)
    except Exception as e:
        print('Error in function imagingTools.gaussianFilter: ' + str(e))


def thresholdPixelArray(pixelArray, lower_threshold, upper_threshold):
    if (lower_threshold < 0 or lower_threshold > 100):
        print("Raise lower t error")
    elif (upper_threshold < 0 or upper_threshold > 100):
        print("Raise lower t error")
    elif (upper_threshold < lower_threshold):
        print("Raise lower greater than upper t")
    
    maximum_value = np.amax(pixelArray)
    minimum_value = np.amin(pixelArray)
    upper_value = minimum_value + (upper_threshold / 100) * (maximum_value - minimum_value)
    lower_value = minimum_value + (lower_threshold / 100) * (maximum_value - minimum_value)

    thresholdedArray = pixelArray
    thresholdedArray[pixelArray < lower_value] = 0
    thresholdedArray[pixelArray > upper_value] = 0
    thresholdedArray[thresholdedArray != 0] = 1
    return thresholdedArray


def resizeImage(pixelArray, factor=1, targetSize=None):
    """
    Resizes the given pixelArray, using target_size as the reference
    of the resizing operation (if None, then there's no resizing).
    This method applies a resizeFactor to the first 2 axes of the input array.
    The remaining axes are left unchanged.
    Example 1: (10, 10, 2) => (5, 5, 2) with resizeFactor = 0.5
    Example 2: (10, 10, 10, 2) => (20, 20, 10, 2) with resizeFactor = 2

    Parameters
    ----------
    pixelArray : np.ndarray

    factor : boolean
        Optional input argument. This is the resize factor defined by the user
        and it is applied in the scipy.ndimage.zoom

    targetSize : boolean
        Optional input argument. By default, this script does not apply the
        scipy wrap_around in the input image.

    Returns
    -------
    resizedArray : np.ndarray where the size of the first 2 dimensions
        is np.shape(pixelArray) * factor. The remaining dimensions (or axes)
        will have a the same size as in pixelArray.
    """
    if targetSize is not None:
        factor = targetSize / np.shape(pixelArray)[0]

    resizeFactor = np.ones(len(np.shape(pixelArray)))
    resizeFactor[0] = factor
    resizeFactor[1] = factor
    resizedArray = scipy.ndimage.zoom(pixelArray, resizeFactor)

    return resizedArray


def resizePixelArray(pixelArray, pixelSpacing, reconstPixel=None):
    """Resizes the given array, using reconstPixel as reference of the resizing""" 
    # Resample Data / Don't forget to resample the 128x128 of GE
    # This is so that data shares the same resolution and sizing

    if reconstPixel is not None:
        fraction = reconstPixel / pixelSpacing
    else:
        fraction = 1
    
    # What happens to SliceSpacing?!
    if len(np.shape(pixelArray)) == 3:
        pixelArray = resize(pixelArray, (pixelArray.shape[0], pixelArray.shape[1] // fraction, pixelArray.shape[2] // fraction), anti_aliasing=True)
    elif len(np.shape(pixelArray)) == 4:
        pixelArray = resize(pixelArray, (pixelArray.shape[0], pixelArray.shape[1] , pixelArray.shape[2] // fraction, pixelArray.shape[3] // fraction), anti_aliasing=True)
    elif len(np.shape(pixelArray)) == 5:
        pixelArray = resize(pixelArray, (pixelArray.shape[0], pixelArray.shape[1], pixelArray.shape[2], pixelArray.shape[3] // fraction, pixelArray.shape[4] // fraction), anti_aliasing=True)
    elif len(np.shape(pixelArray)) == 6:
        pixelArray = resize(pixelArray, (pixelArray.shape[0], pixelArray.shape[1], pixelArray.shape[2], pixelArray.shape[3], pixelArray.shape[4] // fraction, pixelArray.shape[5] // fraction), anti_aliasing=True)

    return pixelArray


def formatArrayForAnalysis(volumeArray, numAttribute, dataset, dimension='2D', transpose=False, invert=False, resize=None):
    """Formats the given array in a structured manner according to the given flags"""

    if dimension == '2D':
        volumeArray = np.squeeze(np.reshape(volumeArray, (int(np.shape(volumeArray)[0]/numAttribute), numAttribute)))
    elif dimension == '3D':
        volumeArray = np.squeeze(np.reshape(volumeArray, (int(np.shape(volumeArray)[0]/numAttribute), numAttribute, np.shape(volumeArray)[1])))
    elif dimension == '4D':
        volumeArray = np.squeeze(np.reshape(volumeArray, (int(np.shape(volumeArray)[0]/numAttribute), numAttribute, np.shape(volumeArray)[1], np.shape(volumeArray)[2])))
    elif dimension == '5D':
        volumeArray = np.squeeze(np.reshape(volumeArray, (int(np.shape(volumeArray)[0]/numAttribute), numAttribute, np.shape(volumeArray)[1], np.shape(volumeArray)[2], np.shape(volumeArray)[3])))
    elif dimension == '6D':
        volumeArray = np.squeeze(np.reshape(volumeArray, (int(np.shape(volumeArray)[0]/numAttribute), numAttribute, np.shape(volumeArray)[1], np.shape(volumeArray)[2], np.shape(volumeArray)[3], np.shape(volumeArray)[4])))
    
    if hasattr(dataset, 'PerFrameFunctionalGroupsSequence'):
        pixelSpacing = dataset.PerFrameFunctionalGroupsSequence[0].PixelMeasuresSequence[0].PixelSpacing[0]
    else: # For normal DICOM, slicelist is a list of slice locations in mm.
        pixelSpacing = dataset.PixelSpacing[0]

    pixelArray = resizePixelArray(volumeArray, pixelSpacing, reconstPixel=resize)

    if transpose == True:
        pixelArray = np.transpose(pixelArray)

    if invert == True:
        pixelArray = invertAlgorithm(pixelArray, dataset)

    del volumeArray, pixelSpacing
    return pixelArray


def imageStats(pixelArray):
    """
    This functions takes an image and calculates its mean, std, min and max.
    It is used in the unit tests, but it can also be used for other
    image processing tasks.

    Parameters
    ----------
    pixelArray : np.ndarray

    Returns
    -------
    list() with 4 values calculated from pixel_array:
        [mean, standard deviation, minimum, maximum]
    """
    mean = np.nanmean(pixelArray)
    std = np.nanstd(pixelArray)
    minimum = np.nanmin(pixelArray)
    maximum = np.nanmax(pixelArray)
    return [mean, std, minimum, maximum]