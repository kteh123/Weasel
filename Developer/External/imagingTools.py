import numpy as np
import pydicom
import scipy.ndimage
from skimage.transform import resize
from skimage.restoration import unwrap_phase

#INSERT A METHOD TO DEAL WITH MOSAIC PIXEL ARRAYS
#INSERT MOSAIC IMAGE CONDITION HERE / OR AT IMAGINGTOOLS.PY

def unWrapPhase(pixelArray):
    # Wrapping of the phase image according to https://scikit-image.org/docs/dev/auto_examples/filters/plot_phase_unwrap.html
    wrappedPhase = np.angle(np.exp(2j * pixelArray))
    return unwrap_phase(wrappedPhase)



def convertToPiRange(pixelArray):
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
    thresholdedArray[thresholdedArray > 0] = 1
    return thresholdedArray


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

# I called numAttribute because it might be others than Slices - Here's a pseudo example
#pixelArray = formatArrayForAnalysis(volumeArray, numberSlices, dataset, dimension='4D', transpose=True)
#pixelArray_2 = formatArrayForAnalysis(pixelArray, numberEchoes, dataset, dimension='5D', transpose=False)
#pixelArray_3 = formatArrayForAnalysis(pixelArray, numberBValues, dataset, dimension='6D', transpose=False, resize=3)

# MAYBE A def formatArrayForSaving? THAT WOULD MAKE SENSE AND MAKE THINGS EASIER