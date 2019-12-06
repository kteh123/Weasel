import os
import numpy as np
import readDICOM_Image


def save_and_returnFilename(pixelArray, dataset, imagePath, suffix):
    """This method reads the DICOM file in imagePath and returns the Image/Pixel array"""
    try:
        if os.path.exists(imagePath):
             # NEED TO FURTHER DEVELOP THIS. WILL BE A LOT MORE COMPLEX
             # Need to think about what new name to give to the file
            dataset.PixelData = pixelArray.astype(
                dataset.pixel_array.dtype).tobytes()
            oldFileName = os.path.splitext(imagePath)
            newFilePath = oldFileName[0] + suffix + '.dcm'
            newFileName = os.path.basename(newFilePath)
            dataset.save_as(newFilePath)
            #return newFileName  change made by Steve to return full file path
            return newFilePath
        else:
            return None
    except Exception as e:
        print('Error in function saveDICOM_Image.save_and_returnFilename: ' + str(e))
