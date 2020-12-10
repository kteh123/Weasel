__version__ = '1.0'
__author__ = 'Steve Shillitoe'

class ROIs():
    def __init__(self, NumImages = 1):
        self.dictMasks = {}
        self.regionNumber = 1
        self.prevRegionName = "region1"
        self.listOfLists = [[] for _ in range(NumImages)]


    def addRegion(self, regionName, mask, imageNumber = 0):
        if regionName in self.dictMasks:
            #add to an existing ROI using boolean OR (|) to get the union
            self.dictMasks[regionName] = self.dictMasks[regionName] | mask
        else:
            #a new ROI
            self.dictMasks[regionName] = mask
 

    def getNextRegionName(self):
        self.regionNumber += 1
        nextRegionName = "region" + str(self.regionNumber)
        self.prevRegionName = nextRegionName
        return nextRegionName


    def getListOfRegions(self):
        return list(self.dictMasks)


    def setPreviousRegionName(self, regionName):
        self.prevRegionName = regionName


    def getMask(self, regionName):
        if regionName in self.dictMasks: 
            return self.dictMasks[regionName]
        else:
            return None

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
        for key, value in self.dictMasks.items():
            print(key, ' : ', value)
