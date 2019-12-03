import pydicom
import os
import numpy as np

FILE_SUFFIX = '_inv.dcm'

"""Inverts an image. Bits that are 0 become 1, and those that are 1 become 0"""
def returnPixelArray(imagePath):
    try:
        if os.path.exists(imagePath):
            dataset = pydicom.dcmread(imagePath)
            if 'PixelData' in dataset:
                invertedImage = np.invert(dataset.pixel_array)
                if invertedImage.dtype != np.uint16:
                    invertedImage = invertedImage.astype(np.uint16)
                dataset.PixelData = invertedImage.tobytes()
                #Save inverted image file
                newFilePath = imagePath + FILE_SUFFIX  
                dataset.save_as(newFilePath)
                return invertedImage, newFilePath
            else:
                return None, None
        else:
            return None, None
    except Exception as e:
            print('Error in function invertDICOM_Image.returnPixelArray: ' + str(e))