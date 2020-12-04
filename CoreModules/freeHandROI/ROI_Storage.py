class ROIs():
    def __init__(self):
        self.dictMasks = {}
        self.regionNumber = 1
        self.prevRegionName = None


    def addRegion(self, regionName,  mask):
        if regionName in self.dictMasks:
            #add to an existing ROI using boolean OR (|) to get the union
            self.dictMasks[regionName] = self.dictMasks[regionName] | mask
        else:
            #a new ROI
            self.dictMasks[regionName] = mask
 

    def getNextRegionName(self):
        self.regionNumber += 1
        return "region" + str(self.regionNumber)


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
            if len(newName) > 0:
                oldName = self.prevRegionName
                if oldName in self.dictMasks:
                    pass
                else:
                    oldName = newName[0 : len(newName)-1]

                if oldName in self.dictMasks:
                    if newName not in self.dictMasks:
                        self.dictMasks[newName] = self.dictMasks.pop(oldName)
                        return True
                    else:
                        return False
        except KeyError:
            print("Key error when oldName = {} & newName ={}".format(oldName, newName))
        except Exception as e:
            print('Error in ROI_Storage.renameDictionaryKey: ' + str(e))
           