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
            newFilePath = saveDICOM_Image.save_automatically_and_returnFilePath(
                imagePath, invertedImage, FILE_SUFFIX)
            return invertedImage, newFilePath
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


def invertImage(objWeasel):
    """Creates a subwindow that displays an inverted DICOM image. Executed using the 
    'Invert Image' Menu item in the Tools menu."""
    try:
        if objWeasel.isAnImageSelected():
            imagePath = objWeasel.selectedImagePath
            pixelArray, invertedImageFileName = returnPixelArray(imagePath)
            objWeasel.displayImageSubWindow(pixelArray, invertedImageFileName)
            #Record inverted image in XML file
            seriesID = objWeasel.insertNewImageInXMLFile(invertedImageFileName, 
                                                      FILE_SUFFIX)
            #Update tree view with xml file modified above
            objWeasel.refreshDICOMStudiesTreeView(seriesID)
        elif objWeasel.isASeriesSelected():
            studyID = objWeasel.selectedStudy 
            seriesID = objWeasel.selectedSeries
            imageList = \
                    objWeasel.getImagePathList(studyID, seriesID)
            #Iterate through list of images and invert each image
            invertedImageList = []
            for imagePath in imageList:
                _, invertedImageFileName = returnPixelArray(imagePath)
                invertedImageList.append(invertedImageFileName)

            newSeriesID= objWeasel.insertNewSeriesInXMLFile(imageList, \
                invertedImageList, FILE_SUFFIX)
            objWeasel.displayMultiImageSubWindow(
                invertedImageList, studyID, newSeriesID)
            objWeasel.refreshDICOMStudiesTreeView(newSeriesID)
    except Exception as e:
        print('Error in invertDICOM_Image.invertImage: ' + str(e))