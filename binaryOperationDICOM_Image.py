import pydicom
import os
import numpy as np
import readDICOM_Image

def returnPixelArray(imagePath1, imagePath2, binaryOperation):
    """This method reads the DICOM file in imagePath and returns the Image/Pixel array"""
    try:
        if os.path.exists(imagePath1):
            dataset = readDICOM_Image.getDicomDataset(imagePath1)
            pixelArray1 = readDICOM_Image.getPixelArray(dataset)
        
        if os.path.exists(imagePath2):
            dataset = readDICOM_Image.getDicomDataset(imagePath2)
            pixelArray2 = readDICOM_Image.getPixelArray(dataset)
            
        if binaryOperation == 'Add':
            pixelArray3 = np.add(pixelArray1, pixelArray2)
            return pixelArray3
        elif binaryOperation == 'Divide':
            pixelArray3 = np.divide(pixelArray1, pixelArray2,
            out=np.zeros_like(pixelArray1), where=pixelArray2!=0)
            return pixelArray3
        elif binaryOperation == 'Multiply':
            pixelArray3 = np.multiply(pixelArray1, pixelArray2)
            return pixelArray3
        elif binaryOperation == 'Subtract':
            pixelArray3 = np.subtract(pixelArray1, pixelArray2)
            return pixelArray3
        
       
    except Exception as e:
        print('Error in function binaryOperationDICOM_Image.returnPixelArray: ' + str(e))
