class UserSelection:
    def __init__(this, listImageLists):
        this.listImageLists = listImageLists
        this._overRideSeriesSavedColourmapAndLevels = False 
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
        this._applyUserSelectionToAnImage = False
        for image in this.listImageLists:
            image[1] = 'default'
            image[2] = -1
            image[3] = -1 

    def updateLevels(this, imageName, intensity, contrast):
        this._applyUserSelectionToAnImage = True    
        for imageNumber, image in enumerate(this.listImageLists):
            if image[0] == imageName:
                #Associate the levels with the image being viewed
                this.listImageLists[imageNumber][2] = intensity
                this.listImageLists[imageNumber][3] = contrast
                break

    def updateColourTable(this, imageNumber, colourTable):
        this.applyUserSelectionToAnImage = True
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


