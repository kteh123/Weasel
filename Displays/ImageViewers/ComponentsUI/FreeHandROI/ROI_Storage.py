import numpy as np
import logging
logger = logging.getLogger(__name__)

__version__ = '1.0'
__author__ = 'Steve Shillitoe'
#October/November 2020

class ROIs():
    """
    This class provides a data structure and associated input and 
    output functions for the storage of the ROI's drawn/painted 
    on a DICOM image.
    
    An object is instanciated from this class in the GraphicsView class.

    Weasel gives an ROI a default name but it can be renamed by the user.
    An ROI may extend over 1 or more images and on each image it may have 
    a different shape and position.

    A mask is a boolean array that is the same size as the DICOM images. 
    A blank mask contains only False values.  When an ROI is drawn on an
    image, the array elements in the mask corresponding to the ROI are
    set to True.

    Mask data is stored in a Python dictionary, where the key is the 
    ROI's name and the value a list of masks, one mask for each image
    in the DICOM series. Initially all the masks in this list are blank.
   """
    def __init__(self, numberOfImages, linkToGraphicsView):
        """Instantiates an ROIs object
        
        arguments:
            numberOfImages - number of images in the DICOM series
            linkToGraphicsView - an object reference to the GraphicView
                                object hosting the ROIs object
        """
        self.dictMasks = {}
        self.regionNumber = 1
        self.prevRegionName = "region1"
        self.NumOfImages = numberOfImages
        self.linkToGraphicsView = linkToGraphicsView
        logger.info("ROI_Storage object created")

    
    def resetRegionNumber(self):
        """Resets the regionNumber property to 1. It is incremented
        by 1, each time a new ROI is created with the default name
        region[regionNumber]"""
        self.regionNumber = 1


    def __repr__(self):
        """Represents this class's objects as a string"""
        return '{}'.format(
           self.__class__.__name__)
   

    def addMask(self, mask):
        """Overwrites the blank mask corresponding linked to a given image in the list of 
        initially blank masks with the updated mask containing the ROI."""
        logger.info("ROI_Storage.addMask called")
        try:
            if self.linkToGraphicsView.currentROIName in self.dictMasks:
                imageMaskList = self.dictMasks[self.linkToGraphicsView.currentROIName]
                if imageMaskList[self.linkToGraphicsView.currentImageNumber - 1] is None:
                    #empty list
                    imageMaskList[self.linkToGraphicsView.currentImageNumber - 1] = mask
                else:
                    #already contains a mask, so add to an existing ROI 
                    #using boolean OR (|) to get the union 
                    imageMaskList[self.linkToGraphicsView.currentImageNumber - 1] = imageMaskList[self.linkToGraphicsView.currentImageNumber - 1] | mask
                self.dictMasks[self.linkToGraphicsView.currentROIName] = imageMaskList
            else:
                #a new ROI
                #Make a copy of the list of image mask lists
                imageMaskList = self.createListOfBlankMasks(mask)
                #Add the current mask to the correct list in the list of lists
                imageMaskList[self.linkToGraphicsView.currentImageNumber - 1] = mask
                self.dictMasks[self.linkToGraphicsView.currentROIName] = imageMaskList
        except Exception as e:
            print('Error in ROI_Storage.addMask: ' + str(e))
            logger.exception('Error in ROI_Storage.addMask: ' + str(e))


    def replaceMask(self, newMask):
        """
        For a given ROI and image, the existing mask is replaced by the new
        mask in the input argument, newMask.
        """
        logger.info("ROI_Storage.replaceMask called")
        try:
            if self.linkToGraphicsView.currentROIName in self.dictMasks:
                imageMaskList = self.dictMasks[self.linkToGraphicsView.currentROIName]
                imageMaskList[self.linkToGraphicsView.currentImageNumber - 1] =  newMask 
                self.dictMasks[self.linkToGraphicsView.currentROIName] = imageMaskList
        except Exception as e:
            print('Error in ROI_Storage.replaceMask: ' + str(e))
            logger.exception('Error in ROI_Storage.replaceMask: ' + str(e))


    def createListOfBlankMasks(self, mask):
        """
        Creates a list of blank masks. 
        
        Each mask is a boolean array with all
        elements set to False. It is the same size as
        the DICOM images in the series. There is one mask for
        each image in the series.
        """
        try:
            logger.info("ROI_Storage.createListOfBlankMasks called")
            ny, nx = np.shape(mask)
            blankMask = np.full((ny, nx), False, dtype=bool)
            return [blankMask for _ in range(self.NumOfImages)]
        except Exception as e:
            print('Error in ROI_Storage.createListOfBlankMasks: ' + str(e))


    def getNextRegionName(self):
        """
        This function generates & returns a new ROI name.

        A new ROI name is generated by incrementing the regionNumber class property by 1
        and concatenating with the string 'region'.

        This new ROI name is also stored in the prevRegionName class property
        for use if the user renames this new ROI name. See the function
        renameDictionaryKey for further details.
        """
        try:
            logger.info("ROI_Storage.getNextRegionName called")
            self.regionNumber += 1
            nextRegionName = "region" + str(self.regionNumber)
            self.prevRegionName = nextRegionName
            return nextRegionName
        except Exception as e:
                print('Error in ROI_Storage.getNextRegionName: ' + str(e))


    def getListOfRegions(self):
        """
        Returns a list of region names.
        """
        try:
            logger.info("ROI_Storage.getListOfRegions called")
            return list(self.dictMasks)
        except Exception as e:
                print('Error in ROI_Storage.getListOfRegions: ' + str(e))


    def setPreviousRegionName(self, regionName):
        """
        Sets the value of the property prevRegionName to the input argument, regionName.
        """
        logger.info("ROI_Storage.setPreviousRegionName called")
        self.prevRegionName = regionName

    
    def getUpdatedMask(self):
        """
        This function returns the  mask for a given 
        ROI & image from the dictMasks dictionary.
        """
        logger.info("ROI_Storage.getUpdatedMask called")
        try:
            regionName = self.linkToGraphicsView.currentROIName
            imageNumber = self.linkToGraphicsView.currentImageNumber
            if regionName in self.dictMasks: 
                mask = self.dictMasks[regionName][imageNumber - 1]
                if mask.any():
                    return mask
                else:
                    return None
            else:
                return None
        except Exception as e:
            print('Error in ROI_Storage.getUpdatedMask when imageNumber={}: '.format(imageNumber) + str(e))
            logger.exception('Error in ROI_Storage.getUpdatedMask when imageNumber={}: '.format(imageNumber) + str(e))



    def getMask(self, regionName, imageNumber):
        """
        This function returns the mask for a given 
        ROI & image from the dictMasks dictionary.

        Input Arguments
        ***************
        regionName - Name of the ROI
        imageNumber - Ordinal position of the image in the DICOM series.

        Returns
        *******
        True or False
        """
        logger.info("ROI_Storage.getMask called")
        try:
            if regionName in self.dictMasks: 
                mask = self.dictMasks[regionName][imageNumber - 1]
                if mask.any():
                    return mask
                else:
                    return None
            else:
                return None
        except Exception as e:
            print('Error in ROI_Storage.getMask when imageNumber={}: '.format(imageNumber) + str(e))
            logger.exception('Error in ROI_Storage.getMask when imageNumber={}: '.format(imageNumber) + str(e))


    def hasRegionGotMask(self, regionName):
        """
        This function returns True if a ROI has masks stored in the 
        dictMasks dictionary. Otherwise it returns False.

        Input Argument
        **************
        regionName - Name of the ROI.

        Returns
        *******
        True or False
        """
        try:
            logger.info("ROI_Storage.hasRegionGotMask called")
            if regionName in self.dictMasks: 
                return True
            else:
                return False
        except Exception as e:
                print('Error in ROI_Storage.hasRegionGotMask: ' + str(e))


    def hasImageGotMask(self, regionName, imageNumber):
        """
        This function returns True if a particular ROI exists 
        on a particular image. Otherwise it returns False.

        Input Argument
        **************
        regionName - Name of the ROI.
        imageNumber - Ordinal position of the image in the DICOM series.

        Returns
        *******
        True or False
        """
        logger.info("ROI_Storage.hasImageGotMask called")
        try:
            if regionName in self.dictMasks: 
                mask = self.dictMasks[regionName][imageNumber - 1]
                if mask.any():
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            print('Error in ROI_Storage.hasImageGotMask: ' + str(e))
            logger.error('Error in ROI_Storage.hasImageGotMask: ' + str(e))


    def returnListImagesWithMasks(self, regionName):
        """
        Returns a list of the image numbers where the ROI, regionName
        has been drawn/painted on the image.
        """
        logger.info("ROI_Storage.returnListImagesWithMasks called")
        try:
            listImagesWithMasks = []
            if regionName in self.dictMasks: 
                maskList = self.dictMasks[regionName]
                for i in range(self.NumOfImages):
                   mask = self.dictMasks[regionName][i]
                   if mask.any():
                        listImagesWithMasks.append(i)
           
            return listImagesWithMasks

        except Exception as e:
            print('Error in ROI_Storage.returnListImagesWithMasks: ' + str(e))
            logger.error('Error in ROI_Storage.returnListImagesWithMasks: ' + str(e))


    def deleteMask(self, regionName=None):
        """
        Deletes the masks associated with the ROI called regionName 
        in the dictMask dictionary.
        """
        try:
            logger.info("ROI_Storage.deleteMask called")
            if regionName:
                if regionName in self.dictMasks: 
                    del self.dictMasks[regionName]
        except Exception as e:
           print('Error in ROI_Storage.deleteMask: ' + str(e))
           logger.error('Error in ROI_Storage.deleteMask: ' + str(e))  


    def renameDictionaryKey(self, newName):
        """
        Replaces the name of an existing ROI with the new name in the
        input argument newName.

        If this operation is successful, this function returns True
        otherwise it returns False if newName is already used as a 
        key in the dictMasks dictionary.
        """
        logger.info("ROI_Storage.renameDictionaryKey called")
        try:
            #print("self.prevRegionName={}".format(self.prevRegionName))
            if len(newName) > 0:
                oldName = self.prevRegionName
                if oldName in self.dictMasks:
                    pass
                else:
                    oldName = newName[0 : len(newName)-1]
                #print("before POP newName={}, oldName={}".format(newName, oldName))
                if oldName in self.dictMasks:
                    if newName not in self.dictMasks:
                        #print("POP newName={}, oldName={}".format(newName, oldName))
                        self.dictMasks[newName] = self.dictMasks.pop(oldName)
                        return True
                    else:
                        return False
        except KeyError:
            print("Key error when oldName = {} & newName ={}".format(oldName, newName))
        except Exception as e:
            print('Error in ROI_Storage.renameDictionaryKey: ' + str(e))
       

    def printContentsDictMasks(self):
        """
        This function prints the name of each ROI, the number of 
        images they are drawn/painted on and the number of pixels in each ROI.

        This function was used during testing.
        """
        print("Contents of self.dictMasks")
        for key, value in self.dictMasks.items():
            numMasks = 0
            for item in value:
                if item.any():
                    numMasks +=1
                    result = np.where(item == True)
                    numTrueValues = list(zip(result[1], result[0]))
            print(key, ' : ', numMasks, ' Number True Coords: {}'.format(numTrueValues))
