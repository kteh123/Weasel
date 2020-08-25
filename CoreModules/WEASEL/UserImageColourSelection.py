"""This class module provides the class variables and functions needed
to store and retrieve the data associated with changing the colour table, 
intensity and contrast levels in individual images in a DICOM series of images."""

class UserSelection:
    def __init__(this, listImageLists):
        #List of sublists, where each sublist represents an image
        #in the DICOM series.
        this.listImageLists = listImageLists
        #When this boolean is true the same colour table
        #and intensity and contrast levels are applied
        #to the whole DICOM series.
        this._overRideSeriesSavedColourmapAndLevels = False
        #When this boolean is true, colour table name
        #and intensity and contrast levels selected by the user are
        #applied to individual images in the DICOM series. 
        #These user selected values are stored in listImageLists
        this._applyUserSelectionToAnImage = False


    def getSeriesUpdateStatus(this):
        return this._overRideSeriesSavedColourmapAndLevels


    def setSeriesUpdateStatus(this, boolValue):
        this._overRideSeriesSavedColourmapAndLevels = boolValue


    def getImageUpdateStatus(this):
        return this._applyUserSelectionToAnImage


    def setImageUpdateStatus(this, boolValue):
        this._applyUserSelectionToAnImage = boolValue


    def clearUserSelection(this):
        """Resets the colour table name,  intensity and contrast 
        levels to their default values.
        Also, sets applyUserSelectionToAnImage to False to show that
        the user has not selected a new colour table etc for one or
        more images in the series
        """
        this._applyUserSelectionToAnImage = False
        for image in this.listImageLists:
            image[1] = 'default'
            image[2] = -1
            image[3] = -1 


    def updateLevels(this, imageName, intensity, contrast):
        """Saves the new intensity and contrast levels the user has
        selected for the image called imageName in the list of lists
        called listImageLists"""
        this._applyUserSelectionToAnImage = True 
        imageNumber = this.returnImageNumber(imageName)
        #Associate the levels with the image being viewed
        this.listImageLists[imageNumber][2] = intensity
        this.listImageLists[imageNumber][3] = contrast       


    def updateColourTable(this, imageName, colourTable):
        """Updates the name of the colour table belonging to an image"""
        this._applyUserSelectionToAnImage = True
        print("in updateColourTable apply={}".format(this._applyUserSelectionToAnImage))
        imageNumber = this.returnImageNumber(imageName)
        print("in updateColourTable name={}, number={}".format(imageName,imageNumber))
        this.listImageLists[imageNumber][1] =  colourTable


    def returnImageNumber(this, imageName):
        """Returns the ordinal number of the selected image in the list of lists,
        userSelectionList, that stores the user's selected colour table, contrast level
        and intensity level for each image.
        """
        try:
            imageNumber = -1
            for count, image in enumerate(this.listImageLists, 0):
                if image[0] == imageName:
                    imageNumber = count
                    break
            return imageNumber
        except Exception as e:
            print('Error in DisplayImageColour.UserSelection.returnImageNumber: ' + str(e))
            logger.error('Error in DisplayImageColour.UserSelection.returnImageNumber: ' + str(e)) 


    def returnUserSelection(this, imageNumber):
        """Returns the colour table name, intensity and contrast values 
        selected by the user for the image that has ordinal position 
        imageNumber in userSelectionList, a list of lists where 
        each sublist represents an image in the series being viewed."""
        try:
            colourTable = this.listImageLists[imageNumber][1] 
            intensity = this.listImageLists[imageNumber][2]
            contrast = this.listImageLists[imageNumber][3] 
            return colourTable, intensity, contrast
        except Exception as e:
                print('Error in DisplayImageColour.UserSelection.returnUserSelection: ' + str(e))
                logger.error('Error in DisplayImageColour.UserSelection.returnUserSelection: ' + str(e)) 


