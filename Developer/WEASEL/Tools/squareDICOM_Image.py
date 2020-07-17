import os
import numpy as np
import CoreModules.readDICOM_Image as readDICOM_Image
import CoreModules.saveDICOM_Image as saveDICOM_Image
from CoreModules.imagingTools import squarePixelArray
import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.WEASEL.DisplayImageColour  as displayImageColour
FILE_SUFFIX = '_Square'

def returnPixelArray(imagePath):
    """Applies the squareroot on an image and returns the resulting PixelArray"""
    try:
        if os.path.exists(imagePath):
            pixelArray = readDICOM_Image.returnPixelArray(imagePath)
            #derivedImage = squareAlgorithm(pixelArray)
            derivedImage = squarePixelArray(pixelArray)
            return derivedImage
        else:
            return None
    except Exception as e:
            print('Error in function squareDICOM_Image.returnPixelArray: ' + str(e))
    
# The purpose is to demonstrate that the user can either apply a method already defined or can create and use a new method
# Comment/Uncomment according to what's agreed with the team.
#def squareAlgorithm(pixelArray):
    #try:
        #derivedImage = np.square(pixelArray)
        #return derivedImage
    #except Exception as e:
        #print('Error in function squareDICOM_Image.squareAlgorithm: ' + str(e))


def saveSquareImage(objWeasel):
    """Creates a subwindow that displays a square rooted DICOM image. Executed using the 
    'Square Image' Menu item in the Tools menu."""
    try:
        if treeView.isAnImageSelected(self):
            imagePath = objWeasel.selectedImagePath
            pixelArray = returnPixelArray(imagePath)
            derivedImageFileName = saveDICOM_Image.returnFilePath(imagePath, FILE_SUFFIX)
            displayImageColour.displayImageSubWindow(objWeasel, derivedImageFileName)
            # Save the DICOM file in the new file path                                        
            saveDICOM_Image.saveDicomOutputResult(derivedImageFileName, imagePath, pixelArray, FILE_SUFFIX)
            #Record squared image in XML file
            seriesID = objWeasel.insertNewImageInXMLFile(derivedImageFileName, FILE_SUFFIX)
            #Update tree view with xml file modified above
            treeView.refreshDICOMStudiesTreeView(objWeasel, seriesID)
        elif treeView.isASeriesSelected(self):
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
            objWeasel.displayMessageSubWindow(
              "<H4>Saving results into a new DICOM Series</H4>",
              "Squaring DICOM images")
            objWeasel.setMsgWindowProgBarMaxValue(2)
            objWeasel.setMsgWindowProgBarValue(1)
            # Save new DICOM series locally
            saveDICOM_Image.saveDicomNewSeries(derivedImagePathList, imagePathList, derivedImageList, FILE_SUFFIX)
            newSeriesID = objWeasel.insertNewSeriesInXMLFile(imagePathList, \
                derivedImagePathList, FILE_SUFFIX)
            objWeasel.setMsgWindowProgBarValue(2)
            objWeasel.closeMessageSubWindow()
            displayImageColour.displayMultiImageSubWindow(objWeasel,
                derivedImagePathList, studyID, newSeriesID)
            treeView.refreshDICOMStudiesTreeView(objWeasel, newSeriesID)
    except Exception as e:
        print('Error in squaredDICOM_Image.saveSquareImage: ' + str(e))
