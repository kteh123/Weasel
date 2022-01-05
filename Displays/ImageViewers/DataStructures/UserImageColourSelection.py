"""
This class module provides the class variables and functions needed
to store and retrieve the data associated with changing the colour table, 
intensity and contrast levels in individual images in a DICOM series of images.
"""
import  os
import logging
logger = logging.getLogger(__name__)
__author__ = "Steve Shillitoe"
#September 2021

class UserSelection:
    def __init__(self, imageList):
        """
        Creates a dictionary of lists to hold user selected colour table and level data,
        where the key is the image name and the value is a list, called imageDataList,
        of the form.
            [colour table name, intensity level, contrast level]

        Image name is extracted from the image file path in the list imageList

        Inputs
        ******
        imageList - list of the file paths of the images in a DICOM series
        """

        self.imageDict = {}
        #create imageDataList with default values
        imageDataList = ['default', -1, -1]
        for imagePath in imageList:
            imageName = os.path.basename(imagePath)
            self.imageDict[imageName] = imageDataList
        
        #When this boolean is true the same colour table
        #and intensity and contrast levels are applied
        #to the whole DICOM series.
        self._overRideSeriesSavedColourmapAndLevels = False

        #When this boolean is true, colour table name
        #and intensity and contrast levels selected by the user are
        #applied to individual images in the DICOM series. 
        #These user selected values are stored in listImageLists
        self._applyUserSelectionToAnImage = False


    def getSeriesUpdateStatus(self):
        """
        Returns the value of the boolean _overRideSeriesSavedColourmapAndLevels

        When _overRideSeriesSavedColourmapAndLevels is true the same colour table,
        intensity and contrast levels are applied to the whole DICOM series.

        Returns
        *******
            The value of the boolean _overRideSeriesSavedColourmapAndLevels
        """
        return self._overRideSeriesSavedColourmapAndLevels


    def setSeriesUpdateStatus(self, boolValue):
        """
        Sets the value of the boolean _overRideSeriesSavedColourmapAndLevels 
        to the value of the argument boolValue.
        """
        self._overRideSeriesSavedColourmapAndLevels = boolValue


    def getImageUpdateStatus(self):
        """
        Returns the value of the boolean _applyUserSelectionToAnImage.

        When _applyUserSelectionToAnImage is true, colour table name,
        intensity level and contrast level selected by the user are
        applied to individual images in the DICOM series.
        
        These user selected values are stored in the
        dictionary value, which is a list, corresponding to the image
        in the self.imageDict dictionary

        Returns
        *******
            The value of the boolean _applyUserSelectionToAnImage
        """
        return self._applyUserSelectionToAnImage


    def setImageUpdateStatus(self, boolValue):
        """
        Sets the value of the boolean _applyUserSelectionToAnImage
        to the value of the argument boolValue.
        """
        self._applyUserSelectionToAnImage = boolValue


    def clearUserSelection(self):
        """
        Resets the colour table name,  intensity and contrast 
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
        """
        Deletes a key-value pair in the dictionary self.imageDict
        where the key = imageName.
        """
        del self.imageDict[imageName]


    def updateUserSelection(self, imageName, colourTable, intensity, contrast):
        """Saves the new colour table name,  intensity and contrast levels the user has
        selected for the image called imageName in the dictionary self.imageDict.
        
        Input arguments
        ***************
            imageName - name of the image
            colourTable - name of the colour table 
            intensity - integer representing image intensity 
            contrast - integer representing image contrast 
        """
        try:
            self._applyUserSelectionToAnImage = True 
            tempList =[colourTable, intensity,  contrast]
            self.imageDict[imageName] = tempList
        except Exception as e:
            print('Error in UserImageColourSelection.updateUserSelection: ' + str(e))
            logger.error('Error in UserImageColourSelection.updateUserSelection: ' + str(e)) 


    def returnUserSelection(self, imageName):
        """Returns the colour table name, intensity and contrast values 
        selected by the user for the image called imageName
        from the dictionary self.imageDict ."""
        try:
            tempList = self.imageDict.get(imageName)
            colourTable = tempList[0]
            intensity = tempList[1]
            contrast = tempList[2] 
            return colourTable, intensity, contrast
        except Exception as e:
                print('Error in UserImageColourSelection.UserSelection.returnUserSelection: ' + str(e))
                logger.error('Error in UserImageColourSelection.UserSelection.returnUserSelection: ' + str(e)) 


