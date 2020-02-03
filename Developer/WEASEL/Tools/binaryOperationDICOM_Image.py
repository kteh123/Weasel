import pydicom
import os
import numpy as np
import CoreModules.readDICOM_Image as readDICOM_Image


listBinaryOperations =['Select binary Operation', 'Add', 'Divide', 
                         'Multiply', 'Subtract']

def returnPixelArray(imagePath1, imagePath2, binaryOperation):
    """returns the Image/Pixel array"""
    try:
        if os.path.exists(imagePath1):
            dataset1 = readDICOM_Image.getDicomDataset(imagePath1)
            pixelArray1 = readDICOM_Image.getPixelArray(dataset1)
        
        if os.path.exists(imagePath2):
            dataset2 = readDICOM_Image.getDicomDataset(imagePath2)
            pixelArray2 = readDICOM_Image.getPixelArray(dataset2)
            
        if binaryOperation == 'Add':
            pixelArray3 = np.add(pixelArray1, pixelArray2)
           
        elif binaryOperation == 'Divide':
            #If there is division by zero, then zero is returned
            pixelArray3 = np.divide(pixelArray1, pixelArray2,
            out=np.zeros_like(pixelArray1), where=pixelArray2!=0)
           
        elif binaryOperation == 'Multiply':
            pixelArray3 = np.multiply(pixelArray1, pixelArray2)
           
        elif binaryOperation == 'Subtract':
            pixelArray3 = np.subtract(pixelArray1, pixelArray2)
        
        if pixelArray3.any():
             return pixelArray3
        else:
             return np.zeros(np.array(pixelArray1).shape)
       
    except Exception as e:
        print('Error in function binaryOperationDICOM_Image.returnPixelArray: ' + str(e))

def getBinOperationFilePrefix(binaryOperation):
    if binaryOperation == 'Subtract':
        prefix = 'Sub'
    elif binaryOperation == 'Divide':
        prefix = 'Div'
    elif binaryOperation == 'Multiply':
        prefix = 'Multi'
    elif binaryOperation == 'Add':
        prefix = 'Add'

    return prefix
