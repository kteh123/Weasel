import pydicom
import os
import numpy as np

FILE_SUFFIX = '_dbl.dcm'

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
                newFileName = os.path.basename(newFilePath)
                dataset.save_as(newFilePath)
                return invertedImage, newFileName
            else:
                return None, None
        else:
            return None, None
    except Exception as e:
            print('Error in function invertDICOM_Image.returnPixelArray: ' + str(e))