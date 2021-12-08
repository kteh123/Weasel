import numpy as np
import logging
logger = logging.getLogger(__name__)

__version__ = '1.0'
__author__ = 'Steve Shillitoe'
#October/November 2020

class ROIs():
    """An object instanciated from this class in the GraphicsView class
   is used to store the masks on an image that form a Region of Interest, ROI.

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
   When an ROI is drawn on an image, the array elements that correspond to
   the ROI in the mask in the list corresponding to that image are set to True.
   """
    def __init__(self, numberOfImages, linkToGraphicsView):
        """Instantiates an ROIs object"""
        self.dictMasks = {}
        self.regionNumber = 1
        self.prevRegionName = "region1"
        self.NumOfImages = numberOfImages
        self.linkToGraphicsView = linkToGraphicsView
        logger.info("RIO_Storage object created")

    
    def resetRegionNumber(self):
        """Resets the regionNumber property to 1. It is incremented
        by 1, each time a new ROI is created with the default name
        region[regionNumber]"""
        self.regionNumber = 1


    def __repr__(self):
       return '{}'.format(
           self.__class__.__name__)
   

    def addMask(self, mask):
        logger.info("RIO_Storage.addMask called")
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


    def replaceMask(self, mask):
        logger.info("RIO_Storage.replaceMask called")
        try:
            if self.linkToGraphicsView.currentROIName in self.dictMasks:
                imageMaskList = self.dictMasks[self.linkToGraphicsView.currentROIName]
                imageMaskList[self.linkToGraphicsView.currentImageNumber - 1] =  mask 
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
            logger.info("RIO_Storage.createListOfBlankMasks called")
            ny, nx = np.shape(mask)
            blankMask = np.full((ny, nx), False, dtype=bool)
            return [blankMask for _ in range(self.NumOfImages)]
        except Exception as e:
            print('Error in ROI_Storage.createListOfBlankMasks: ' + str(e))


    def getNextRegionName(self):
        try:
            logger.info("RIO_Storage.getNextRegionName called")
            self.regionNumber += 1
            nextRegionName = "region" + str(self.regionNumber)
            self.prevRegionName = nextRegionName
            return nextRegionName
        except Exception as e:
                print('Error in ROI_Storage.getNextRegionName: ' + str(e))


    def getListOfRegions(self):
        try:
            logger.info("RIO_Storage.getListOfRegions called")
            return list(self.dictMasks)
        except Exception as e:
                print('Error in ROI_Storage.getListOfRegions: ' + str(e))


    def setPreviousRegionName(self, regionName):
        logger.info("RIO_Storage.setPreviousRegionName called")
        self.prevRegionName = regionName

    
    def getUpdatedMask(self):
        logger.info("RIO_Storage.getUpdatedMask called")
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
        logger.info("RIO_Storage.getMask called")
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
        try:
            logger.info("RIO_Storage.hasRegionGotMask called")
            if regionName in self.dictMasks: 
                return True
            else:
                return False
        except Exception as e:
                print('Error in ROI_Storage.hasRegionGotMask: ' + str(e))


    def hasImageGotMask(self, regionName, imageNumber):
        logger.info("RIO_Storage.hasImageGotMask called")
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
        logger.info("RIO_Storage.returnListImagesWithMasks called")
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
        try:
            logger.info("RIO_Storage.deleteMask called")
            if regionName:
                if regionName in self.dictMasks: 
                    del self.dictMasks[regionName]
        except Exception as e:
           print('Error in ROI_Storage.deleteMask: ' + str(e))
           logger.error('Error in ROI_Storage.deleteMask: ' + str(e))  


    def renameDictionaryKey(self, newName):
        logger.info("RIO_Storage.renameDictionaryKey called")
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
        print("Contents of self.dictMasks")
        for key, value in self.dictMasks.items():
            numMasks = 0
            for item in value:
                if item.any():
                    numMasks +=1
                    result = np.where(item == True)
                    numTrueValues = list(zip(result[1], result[0]))
            print(key, ' : ', numMasks, ' Number True Coords: {}'.format(numTrueValues))
