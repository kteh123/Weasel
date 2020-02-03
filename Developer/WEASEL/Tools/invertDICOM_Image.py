import os
import numpy as np
import CoreModules.readDICOM_Image as readDICOM_Image
import CoreModules.saveDICOM_Image as saveDICOM_Image

FILE_SUFFIX = '_Inverted'

def returnPixelArray(imagePath):
    """Inverts an image. Bits that are 0 become 1, and those that are 1 become 0"""
    try:
        if os.path.exists(imagePath):
            dataset = readDICOM_Image.getDicomDataset(imagePath)
            pixelArray = readDICOM_Image.getPixelArray(dataset)
            derivedImage = invertAlgorithm(pixelArray, dataset)
            return derivedImage
        else:
            return None
    except Exception as e:
            print('Error in function invertDICOM_Image.returnPixelArray: ' + str(e))
    
def invertAlgorithm(pixelArray, dataset):
    try:
        derivedImage = np.invert(pixelArray.astype(dataset.pixel_array.dtype))
        return derivedImage
    except Exception as e:
            print('Error in function invertDICOM_Image.invertAlgorithm: ' + str(e))


def invertImage(objWeasel):
    """Creates a subwindow that displays an inverted DICOM image. Executed using the 
    'Invert Image' Menu item in the Tools menu."""
    try:
        if objWeasel.isAnImageSelected():
            imagePath = objWeasel.selectedImagePath
            pixelArray = returnPixelArray(imagePath)
            derivedImageFileName = saveDICOM_Image.returnFilePath(imagePath, FILE_SUFFIX)
            objWeasel.displayImageSubWindow(pixelArray, derivedImageFileName)
            #Record inverted image in XML file
            seriesID = objWeasel.insertNewImageInXMLFile(derivedImageFileName, 
                                                      FILE_SUFFIX)
            # Save the DICOM file in the new file path                                        
            saveDICOM_Image.save_dicom_outputResult(derivedImageFileName, imagePath, pixelArray, FILE_SUFFIX) # Still need some optional flags depending on insertNewImageInXMLFile
            #Update tree view with xml file modified above
            objWeasel.refreshDICOMStudiesTreeView(seriesID)
        elif objWeasel.isASeriesSelected():
            # Should consider the case where Series is 1 image/file only
            studyID = objWeasel.selectedStudy
            seriesID = objWeasel.selectedSeries
            imagePathList = \
                    objWeasel.getImagePathList(studyID, seriesID)
            #Iterate through list of images and invert each image
            derivedImagePathList = []
            derivedImageList = []
            numImages = len(imagePathList)
            objWeasel.displayMessageSubWindow(
              "<H4>Inverting {} DICOM files</H4>".format(numImages),
              "Inverting DICOM images")
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

            newSeriesID = objWeasel.insertNewSeriesInXMLFile(imagePathList, \
                derivedImagePathList, FILE_SUFFIX)
            # Save new DICOM series locally
            saveDICOM_Image.save_dicom_newSeries(derivedImagePathList, imagePathList, derivedImageList, FILE_SUFFIX)
            objWeasel.displayMultiImageSubWindow(
                derivedImagePathList, studyID, newSeriesID)
            objWeasel.refreshDICOMStudiesTreeView(newSeriesID)
    except Exception as e:
        print('Error in invertDICOM_Image.invertImage: ' + str(e))