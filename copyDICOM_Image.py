import os
import numpy as np
import readDICOM_Image
import saveDICOM_Image

FILE_SUFFIX = '_copy'

def returnCopiedFile(imagePath):
    """Inverts an image. Bits that are 0 become 1, and those that are 1 become 0"""
    try:
        if os.path.exists(imagePath):
            dataset = readDICOM_Image.getDicomDataset(imagePath)
            pixelArray = readDICOM_Image.getPixelArray(dataset)
            newFileName = saveDICOM_Image.save_automatically_and_returnFilePath(
                 imagePath, pixelArray, FILE_SUFFIX)
            return  newFileName
        else:
            return None
    except Exception as e:
            print('Error in function invertDICOM_Image.returnPixelArray: ' + str(e))
