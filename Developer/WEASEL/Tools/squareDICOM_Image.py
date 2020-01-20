import os
import numpy as np
import readDICOM_Image
import saveDICOM_Image

FILE_SUFFIX = '_Square'

def returnPixelArray(imagePath):
    """Inverts an image. Bits that are 0 become 1, and those that are 1 become 0"""
    try:
        if os.path.exists(imagePath):
            dataset = readDICOM_Image.getDicomDataset(imagePath)
            pixelArray = readDICOM_Image.getPixelArray(dataset)
            derivedImage = squareAlgorithm(pixelArray, dataset)
            derivedImageFilePath = saveDICOM_Image.save_automatically_and_returnFilePath(
                imagePath, derivedImage, FILE_SUFFIX)
            return derivedImage, derivedImageFilePath
        else:
            return None, None
    except Exception as e:
            print('Error in function squareDICOM_Image.returnPixelArray: ' + str(e))
    

def squareAlgorithm(pixelArray, dataset):
    try:
        derivedImage = np.square(pixelArray.astype(dataset.pixel_array.dtype))
        return derivedImage
    except Exception as e:
            print('Error in function squareDICOM_Image.squareAlgorithm: ' + str(e))


def squareImage(objWeasel):
    """Creates a subwindow that displays an inverted DICOM image. Executed using the 
    'Invert Image' Menu item in the Tools menu."""
    try:
        if objWeasel.isAnImageSelected():
            imagePath = objWeasel.selectedImagePath
            pixelArray, derivedImageFileName = returnPixelArray(imagePath)
            objWeasel.displayImageSubWindow(pixelArray, derivedImageFileName)
            #Record inverted image in XML file
            seriesID = objWeasel.insertNewImageInXMLFile(derivedImageFileName, 
                                                      FILE_SUFFIX)
            #Update tree view with xml file modified above
            objWeasel.refreshDICOMStudiesTreeView(seriesID)
        elif objWeasel.isASeriesSelected():
            studyID = objWeasel.selectedStudy 
            seriesID = objWeasel.selectedSeries
            imageList = \
                    objWeasel.getImagePathList(studyID, seriesID)
            #Iterate through list of images and square each image
            derivedImageList = []
            numImages = len(imageList)
            objWeasel.displayMessageSubWindow(
              "<H4>Squaring {} DICOM files</H4>".format(numImages),
              "Squaring DICOM images")
            objWeasel.setMsgWindowProgBarMaxValue(numImages)
            imageCounter = 0
            for imagePath in imageList:
                _, derivedImageFileName = returnPixelArray(imagePath)
                derivedImageList.append(derivedImageFileName)
                imageCounter += 1
                objWeasel.setMsgWindowProgBarValue(imageCounter)

            objWeasel.closeMessageSubWindow()

            newSeriesID= objWeasel.insertNewSeriesInXMLFile(imageList, \
                derivedImageList, FILE_SUFFIX)
            objWeasel.displayMultiImageSubWindow(
                derivedImageList, studyID, newSeriesID)
            objWeasel.refreshDICOMStudiesTreeView(newSeriesID)
    except Exception as e:
        print('Error in squaredDICOM_Image.squareImage: ' + str(e))
