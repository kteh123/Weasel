import numpy as np
import logging
logger = logging.getLogger(__name__)

__version__ = '1.0'
__author__ = 'Steve Shillitoe'

class ROIs():
    def __init__(self, NumImages = 1):
        logger.info("ROI_Storage object initialised")
        self.dictMasks = {}
        self.regionNumber = 1
        self.prevRegionName = "region1"
        self.NumOfImages = NumImages
        logger.info("RIO_Storage object created")


    def addRegion(self, regionName, mask, imageNumber = 1):
        logger.info("RIO_Storage.addRegion called")
        try:
            if regionName in self.dictMasks:
                imageMaskList = self.dictMasks[regionName]
                if imageMaskList[imageNumber - 1] is None:
                    #empty list
                    imageMaskList[imageNumber - 1] = mask
                else:
                    #already contains a mask, so add to an existing ROI 
                    #using boolean OR (|) to get the union 
                    imageMaskList[imageNumber - 1] = imageMaskList[imageNumber - 1]  | mask
                self.dictMasks[regionName] = imageMaskList
                #self.dictMasks[regionName] = self.dictMasks[regionName] | mask
            else:
                #a new ROI
                #Make a copy of the list of image mask lists
                imageMaskList = self.createListOfBlankMasks(mask)
                #Add the current mask to the correct list in the list of lists
                imageMaskList[imageNumber - 1] = mask
                self.dictMasks[regionName] = imageMaskList
        except Exception as e:
            print('Error in ROI_Storage.addRegion: ' + str(e))


    def replaceMask(self, regionName, mask, imageNumber = 1):
        logger.info("RIO_Storage.replaceMask called")
        try:
            if regionName in self.dictMasks:
                imageMaskList = self.dictMasks[regionName]
                #imageMaskList[imageNumber - 1] = mask
                imageMaskList[imageNumber - 1] =  mask & imageMaskList[imageNumber - 1]
                self.dictMasks[regionName] = imageMaskList

        except Exception as e:
            print('Error in ROI_Storage.replaceMask: ' + str(e))


    def createListOfBlankMasks(self, mask):
        try:
            logger.info("RIO_Storage.createListOfBlankMasks called")
            ny, nx = np.shape(mask)
            blankMask = np.full((nx, ny), False, dtype=bool)
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
            print('Error in ROI_Storage.getMask: ' + str(e))


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
        numMasks = 0
        for key, value in self.dictMasks.items():
            for item in value:
                if item.any():
                    numMasks +=1

            print(key, ' : ', numMasks)
