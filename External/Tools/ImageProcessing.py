"""
This script contains several image processing auxiliary functions that could be used in image processing pipelines development.

At the moment, none of the functions is being used in Weasel or in any examples in Tutorial. 

However, the idea is that the list of functions in this file grows and can be used as support in developer pipelines.
"""

import numpy as np
import scipy.ndimage


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
    """
    Inverts the image values.

    Parameters
    ----------
    pixel_array : np.ndarray

    Returns
    -------
    inverted pixel_array : np.ndarray
    """
    try:
        totalBytes = dataset.BitsAllocated
        return np.invert(pixelArray.astype('int' + str(totalBytes)))
    except Exception as e:
        print('Error in function ImageProcessing.invertAlgorithm: ' + str(e))


def squareAlgorithm(pixelArray):
    """
    Squares the image values.

    Parameters
    ----------
    pixel_array : np.ndarray

    Returns
    -------
    squared pixel_array : np.ndarray
    """
    try:
        return np.square(pixelArray)
    except Exception as e:
        print('Error in function ImageProcessing.squareAlgorithm: ' + str(e))


def gaussianFilter(pixelArray, sigma):
    """
    Applies a gaussian filter with a standard deviation for gaussian kernel of `sigma` to the image.

    Parameters
    ----------
    pixel_array : np.ndarray

    Returns
    -------
    filtered pixel_array : np.ndarray
    """
    try:
        return scipy.ndimage.gaussian_filter(pixelArray, sigma)
    except Exception as e:
        print('Error in function ImageProcessing.gaussianFilter: ' + str(e))


def thresholdPixelArray(pixelArray, lower_threshold, upper_threshold):
    """
    Applies a threshold to the image based on the given `lower_threshold` and `upper_threshold` and returns a binary image.

    Parameters
    ----------
    pixel_array : np.ndarray

    Returns
    -------
    binary pixel_array : np.ndarray
    """
    if (lower_threshold < 0 or lower_threshold > 100):
        print("Raise lower threshold error")
    elif (upper_threshold < lower_threshold):
        print("Raise lower threshold greater than upper threshold error")
    
    maximum_value = np.amax(pixelArray)
    minimum_value = np.amin(pixelArray)
    upper_value = minimum_value + (upper_threshold / 100) * (maximum_value - minimum_value)
    lower_value = minimum_value + (lower_threshold / 100) * (maximum_value - minimum_value)

    thresholdedArray = pixelArray
    thresholdedArray[thresholdedArray < lower_value] = 0
    thresholdedArray[thresholdedArray > upper_value] = 0
    thresholdedArray[thresholdedArray != 0] = 1
    return thresholdedArray
    

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