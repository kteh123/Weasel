import os
import numpy as np
import CoreModules.readDICOM_Image as readDICOM_Image
import CoreModules.saveDICOM_Image as saveDICOM_Image
FILE_SUFFIX = '_Square'

def returnPixelArray(imagePath):
    """Applies the squareroot on an image and returns the resulting PixelArray"""
    try:
        if os.path.exists(imagePath):
            pixelArray = readDICOM_Image.returnPixelArray(imagePath)
            derivedImage = squareAlgorithm(pixelArray)
            return derivedImage
        else:
            return None
    except Exception as e:
            print('Error in function squareDICOM_Image.returnPixelArray: ' + str(e))
    

def squareAlgorithm(pixelArray):
    try:
        derivedImage = np.square(pixelArray)
        return derivedImage
    except Exception as e:
            print('Error in function squareDICOM_Image.squareAlgorithm: ' + str(e))


def squareImage(objWeasel):
    """Creates a subwindow that displays a square rooted DICOM image. Executed using the 
    'Square Image' Menu item in the Tools menu."""
    try:
        if objWeasel.isAnImageSelected():
            imagePath = objWeasel.selectedImagePath
            pixelArray = returnPixelArray(imagePath)
            derivedImageFileName = saveDICOM_Image.returnFilePath(imagePath, FILE_SUFFIX)
            objWeasel.displayImageSubWindow(pixelArray, derivedImageFileName)
            # Save the DICOM file in the new file path                                        
            saveDICOM_Image.save_dicom_outputResult(derivedImageFileName, imagePath, pixelArray, FILE_SUFFIX) # Still need some optional flags depending on insertNewImageInXMLFile
            #Record squared image in XML file
            seriesID = objWeasel.insertNewImageInXMLFile(derivedImageFileName, FILE_SUFFIX)
            #Update tree view with xml file modified above
            objWeasel.refreshDICOMStudiesTreeView(seriesID)
        elif objWeasel.isASeriesSelected():
            studyID = objWeasel.selectedStudy
            seriesID = objWeasel.selectedSeries
            imagePathList = \
                    objWeasel.getImagePathList(studyID, seriesID)
            #Iterate through list of images and square each image
            derivedImagePathList = []
            derivedImageList = []
            numImages = len(imagePathList)
            objWeasel.displayMessageSubWindow(
              "<H4>Squaring {} DICOM files</H4>".format(numImages),
              "Squaring DICOM images")
            objWeasel.setMsgWindowProgBarMaxValue(numImages)
            imageCounter = 0
            for imagePath in imagePathList:
                derivedImagePath = saveDICOM_Image.returnFilePath(imagePath, FILE_SUFFIX)
                derivedImage = returnPixelArray(imagePath)
                derivedImagePathList.append(derivedImagePath)
                derivedImageList.append(derivedImage)
                imageCounter += 1
                objWeasel.setMsgWindowProgBarValue(imageCounter)

            objWeasel.closeMessageSubWindow()
            # Save new DICOM series locally
            saveDICOM_Image.save_dicom_newSeries(derivedImagePathList, imagePathList, derivedImageList, FILE_SUFFIX)
            newSeriesID = objWeasel.insertNewSeriesInXMLFile(imagePathList, \
                derivedImagePathList, FILE_SUFFIX)
            objWeasel.displayMultiImageSubWindow(
                derivedImagePathList, studyID, newSeriesID)
            objWeasel.refreshDICOMStudiesTreeView(newSeriesID)
    except Exception as e:
        print('Error in squaredDICOM_Image.squareImage: ' + str(e))
