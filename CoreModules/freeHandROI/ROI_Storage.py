import numpy as np

__version__ = '1.0'
__author__ = 'Steve Shillitoe'

class ROIs():
    def __init__(self, NumImages = 1):
        self.dictMasks = {}
        self.regionNumber = 1
        self.prevRegionName = "region1"
        self.NumOfImages = NumImages
        #self.imageMaskList = [[] for _ in range(NumImages)]


    def addRegion(self, regionName, mask, imageNumber = 1):
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
                imageMaskList = self.createBlankMask(mask)
                #Add the current mask to the correct list in the list of lists
                imageMaskList[imageNumber - 1] = mask
                self.dictMasks[regionName] = imageMaskList
        except Exception as e:
            print('Error in ROI_Storage.addRegion: ' + str(e))


    def createBlankMask(self, mask):
        ny, nx = np.shape(mask)
        blankMask = np.full((nx, ny), False, dtype=bool)
        return [blankMask for _ in range(self.NumOfImages)]


    def getNextRegionName(self):
        self.regionNumber += 1
        nextRegionName = "region" + str(self.regionNumber)
        self.prevRegionName = nextRegionName
        return nextRegionName


    def getListOfRegions(self):
        return list(self.dictMasks)


    def setPreviousRegionName(self, regionName):
        self.prevRegionName = regionName


    def getMask(self, regionName, imageNumber):
        try:
            if regionName in self.dictMasks: 
                return self.dictMasks[regionName][imageNumber - 1]
            else:
                return None
        except Exception as e:
            print('Error in ROI_Storage.getMask: ' + str(e))


    def hasRegionGotMask(self, regionName):
        if regionName in self.dictMasks: 
            return True
        else:
            return False


    def deleteMask(self, regionName):
        if regionName in self.dictMasks: 
            del self.dictMasks[regionName]


    def renameDictionaryKey(self, newName):
        try:
            print("self.prevRegionName={}".format(self.prevRegionName))
            if len(newName) > 0:
                oldName = self.prevRegionName
                if oldName in self.dictMasks:
                    pass
                else:
                    oldName = newName[0 : len(newName)-1]
                print("before POP newName={}, oldName={}".format(newName, oldName))
                if oldName in self.dictMasks:
                    if newName not in self.dictMasks:
                        print("POP newName={}, oldName={}".format(newName, oldName))
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
