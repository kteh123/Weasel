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
            squaredImage = squareAlgorithm(pixelArray, dataset)
            newFilePath = saveDICOM_Image.save_automatically_and_returnFilePath(
                imagePath, squaredImage, FILE_SUFFIX)
            return squaredImage, newFilePath
        else:
            return None, None
    except Exception as e:
            print('Error in function squareDICOM_Image.returnPixelArray: ' + str(e))
    

def squareAlgorithm(pixelArray, dataset):
    try:
        squaredImage = np.square(pixelArray.astype(dataset.pixel_array.dtype))
        return squaredImage
    except Exception as e:
            print('Error in function squareDICOM_Image.squareAlgorithm: ' + str(e))


def squareImage(objWeasel):
    """Creates a subwindow that displays an inverted DICOM image. Executed using the 
    'Invert Image' Menu item in the Tools menu."""
    try:
        if objWeasel.isAnImageSelected():
            imagePath = objWeasel.selectedImagePath
            pixelArray, squaredImageFileName = returnPixelArray(imagePath)
            objWeasel.displayImageSubWindow(pixelArray, squaredImageFileName)
            #Record inverted image in XML file
            seriesID = objWeasel.insertNewImageInXMLFile(squaredImageFileName, 
                                                      FILE_SUFFIX)
            #Update tree view with xml file modified above
            objWeasel.refreshDICOMStudiesTreeView(seriesID)
        elif objWeasel.isASeriesSelected():
            studyID = objWeasel.selectedStudy 
            seriesID = objWeasel.selectedSeries
            imageList = \
                    objWeasel.getImagePathList(studyID, seriesID)
            #Iterate through list of images and square each image
            squaredImageList = []
            numImages = len(imageList)
            objWeasel.displayMessageSubWindow(
              "<H4>Squaring {} DICOM files</H4>".format(numImages),
              "Squaring DICOM images")
            objWeasel.setMsgWindowProgBarMaxValue(numImages)
            imageCounter = 0
            for imagePath in imageList:
                _, squaredImageFileName = returnPixelArray(imagePath)
                squaredImageList.append(squaredImageFileName)
                imageCounter += 1
                objWeasel.setMsgWindowProgBarValue(imageCounter)

            objWeasel.closeMessageSubWindow()

            newSeriesID= objWeasel.insertNewSeriesInXMLFile(imageList, \
                squaredImageList, FILE_SUFFIX)
            objWeasel.displayMultiImageSubWindow(
                squaredImageList, studyID, newSeriesID)
            objWeasel.refreshDICOMStudiesTreeView(newSeriesID)
    except Exception as e:
        print('Error in squaredDICOM_Image.squareImage: ' + str(e))
