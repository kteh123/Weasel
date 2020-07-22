import os
import numpy as np
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image
import CoreModules.WEASEL.saveDICOM_Image as saveDICOM_Image
import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.WEASEL.MessageWindow  as messageWindow
import CoreModules.WEASEL.DisplayImageColour  as displayImageColour
import CoreModules.WEASEL.InterfaceDICOMXMLFile  as interfaceDICOMXMLFile
FILE_SUFFIX = '_Inverted'

def returnPixelArray(imagePath): #Developer tool
    #return original pixel array
    """Inverts an image. Bits that are 0 become 1, and those that are 1 become 0"""
    try:
        if os.path.exists(imagePath):
            dataset = readDICOM_Image.getDicomDataset(imagePath)
            pixelArray = readDICOM_Image.getPixelArray(dataset)
            #derivedImage = invertAlgorithm(pixelArray, dataset)
            return derivedImage
        else:
            return None
    except Exception as e:
            print('Error in function invertDICOM_Image.returnPixelArray: ' + str(e))
    
#1 get a pixel array from image path
#2call algorithm
def invertAlgorithm(pixelArray, dataset): #scientific library
    try:
        derivedImage = np.invert(pixelArray.astype(dataset.pixel_array.dtype))
        return derivedImage
    except Exception as e:
            print('Error in function invertDICOM_Image.invertAlgorithm: ' + str(e))


def saveInvertImage(objWeasel): #developer tool
    """Creates a subwindow that displays an inverted DICOM image. Executed using the 
    'Invert Image' Menu item in the Tools menu."""
    try:
        if treeView.isAnImageSelected(objWeasel):
            imagePath = objWeasel.selectedImagePath
            pixelArray = returnPixelArray(imagePath)
            derivedImageFileName = saveDICOM_Image.returnFilePath(imagePath, FILE_SUFFIX)
            displayImageColour.displayImageSubWindow(objWeasel, derivedImageFileName)
            
            # Save the DICOM file in the new file path                                        
            saveDICOM_Image.saveDicomOutputResult(derivedImageFileName, imagePath, pixelArray, FILE_SUFFIX)
            #Record inverted image in XML file
            seriesID = interfaceDICOMXMLFile.insertNewImageInXMLFile(objWeasel,
                                                        derivedImageFileName, 
                                                      FILE_SUFFIX)
            #Update tree view with xml file modified above
            treeView.refreshDICOMStudiesTreeView(objWeasel, seriesID)
        elif treeView.isASeriesSelected(objWeasel):
            # Should consider the case where Series is 1 image/file only
            studyID = objWeasel.selectedStudy
            seriesID = objWeasel.selectedSeries
            imagePathList = \
                    objWeasel.objXMLReader.getImagePathList(studyID, seriesID)
            #Iterate through list of images and invert each image
            derivedImagePathList = []
            derivedImageList = []
            numImages = len(imagePathList)
            messageWindow.displayMessageSubWindow(objWeasel,
              "<H4>Inverting {} DICOM files</H4>".format(numImages),
              "Inverting DICOM images")
            messageWindow.setMsgWindowProgBarMaxValue(objWeasel, numImages)
            imageCounter = 0
            for imagePath in imagePathList:
                derivedImagePath = saveDICOM_Image.returnFilePath(imagePath, FILE_SUFFIX)
                derivedImage = returnPixelArray(imagePath)
                derivedImagePathList.append(derivedImagePath)
                derivedImageList.append(derivedImage)
                imageCounter += 1
                messageWindow.setMsgWindowProgBarValue(objWeasel, imageCounter)
            messageWindow.displayMessageSubWindow(objWeasel,
              "<H4>Saving results into a new DICOM Series</H4>",
              "Inverting DICOM images")
            messageWindow.setMsgWindowProgBarMaxValue(objWeasel, 2)
            messageWindow.setMsgWindowProgBarValue(objWeasel, 1)
            # Save new DICOM Series locally
            saveDICOM_Image.saveDicomNewSeries(derivedImagePathList, imagePathList, derivedImageList, FILE_SUFFIX)
            newSeriesID = interfaceDICOMXMLFile.insertNewSeriesInXMLFile(objWeasel,
                imagePathList, 
                derivedImagePathList, FILE_SUFFIX)
            messageWindow.setMsgWindowProgBarValue(objWeasel, 2)
            messageWindow.closeMessageSubWindow(objWeasel)
            displayImageColour.displayMultiImageSubWindow(objWeasel, derivedImagePathList, studyID, newSeriesID)
            treeView.refreshDICOMStudiesTreeView(objWeasel, newSeriesID)
    except Exception as e:
        print('Error in invertDICOM_Image.saveInvertImage: ' + str(e))