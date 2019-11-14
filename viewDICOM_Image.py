import pydicom
import os

def returnPixelArray(imagePath):
    try:
        if os.path.exists(imagePath):
            dataset = pydicom.dcmread(imagePath)
            if 'PixelData' in dataset:
                return dataset.pixel_array
            else:
                return None
        else:
            return None
    except Exception as e:
            print('Error in function viewDICOM_Image.returnPixelArray: ' + str(e))
