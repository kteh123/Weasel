import  os
import logging
logger = logging.getLogger(__name__)
__author__ = "Steve Shillitoe"
#September 2021
"""This class module provides the class variables and functions needed
to store and retrieve the data associated with changing the colour table, 
intensity and contrast levels in individual images in a DICOM series of images."""
class UserSelection:
    def __init__(self, imageList):
        #Set up a dictionary of lists to hold user selected colour table and level data,
        #where the key is the image name and the value a list of the form.
        #    [colour table name, intensity level, contrast level]

        self.imageDict = {}
        imageDataList = ['default', -1, -1]
        for imagePath in imageList:
            imageName = os.path.basename(imagePath)
            self.imageDict[imageName] = imageDataList
        
        #When self boolean is true the same colour table
        #and intensity and contrast levels are applied
        #to the whole DICOM series.
        self._overRideSeriesSavedColourmapAndLevels = False

        #When self boolean is true, colour table name
        #and intensity and contrast levels selected by the user are
        #applied to individual images in the DICOM series. 
        #These user selected values are stored in listImageLists
        self._applyUserSelectionToAnImage = False


    def getSeriesUpdateStatus(self):
        return self._overRideSeriesSavedColourmapAndLevels


    def setSeriesUpdateStatus(self, boolValue):
        self._overRideSeriesSavedColourmapAndLevels = boolValue


    def getImageUpdateStatus(self):
        return self._applyUserSelectionToAnImage


    def setImageUpdateStatus(self, boolValue):
        self._applyUserSelectionToAnImage = boolValue


    def clearUserSelection(self):
        """Resets the colour table name,  intensity and contrast 
        levels to their default values.
        Also, sets applyUserSelectionToAnImage to False to show that
        the user has not selected a new colour table etc for one or
        more images in the series
        """
        self._applyUserSelectionToAnImage = False
        imageDataList = ['default', -1, -1]
        for key in self.imageDict:
            key = imageDataList


    def deleteOneImageInUserSelection(self, imageName):
        del self.imageDict[imageName]


    def updateUserSelection(self, imageName, colourTable, intensity, contrast):
        """Saves the new colour table name,  intensity and contrast levels the user has
        selected for the image called imageName in the list of lists
        called listImageLists"""
        try:
            self._applyUserSelectionToAnImage = True 
            tempList =[colourTable, intensity,  contrast]
            self.imageDict[imageName] = tempList
        except Exception as e:
            print('Error in UserImageColourSelection.updateUserSelection: ' + str(e))
            logger.error('Error in UserImageColourSelection.updateUserSelection: ' + str(e)) 


    def returnUserSelection(self, imageName):
        """Returns the colour table name, intensity and contrast values 
        selected by the user for the image that has ordinal position 
        imageNumber in userSelectionList, a list of lists where 
        each sublist represents an image in the series being viewed."""
        try:
            tempList = self.imageDict.get(imageName)
            colourTable = tempList[0]
            intensity = tempList[1]
            contrast = tempList[2] 
            return colourTable, intensity, contrast
        except Exception as e:
                print('Error in UserImageColourSelection.UserSelection.returnUserSelection: ' + str(e))
                logger.error('Error in UserImageColourSelection.UserSelection.returnUserSelection: ' + str(e)) 


