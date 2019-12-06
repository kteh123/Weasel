import os
import numpy as np
import readDICOM_Image
import saveDICOM_Image

FILE_SUFFIX = '_Inverted'

def returnPixelArray(imagePath):
    """Inverts an image. Bits that are 0 become 1, and those that are 1 become 0"""
    try:
        if os.path.exists(imagePath):
            dataset = readDICOM_Image.getDicomDataset(imagePath)
            pixelArray = readDICOM_Image.getPixelArray(dataset)
            invertedImage = invertAlgorithm(pixelArray, dataset)
            newFileName = saveDICOM_Image.save_and_returnFilename(invertedImage, dataset, imagePath, FILE_SUFFIX)
            return invertedImage, newFileName
        else:
            return None, None
    except Exception as e:
            print('Error in function invertDICOM_Image.returnPixelArray: ' + str(e))
    
def invertAlgorithm(pixelArray, dataset):
    try:
        invertedImage = np.invert(pixelArray.astype(dataset.pixel_array.dtype))
        return invertedImage
    except Exception as e:
            print('Error in function invertDICOM_Image.invertAlgorithm: ' + str(e))