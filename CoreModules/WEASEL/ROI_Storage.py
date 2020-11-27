class ROIs():
    def __init__(self):
        self.dictPathCoords = {}
        self.dictMasks = {}
        self.regionNumber = 0


    def addRegion(self, pathCoords, mask):
        #get next ROI name
        self.regionNumber += 1
        regionName = "region" + str(self.regionNumber)
        print(regionName)
        self.dictPathCoords[regionName] = pathCoords
        self.dictMasks[regionName] = mask


    def getListOfRegions(self):
        return list(self.dictMasks)


    def getMask(self, regionName):
        return self.dictMasks[regionName]

    def getPathCoords(self, regionName):
        return self.dictPathCoords[regionName]

    def renameDictionaryKey(self, oldName, newName):
        self.dictPathCoords[newName] = self.dictPathCoords.pop(oldName)
        self.dictMasks[newName] = self.dictMasks.pop(oldName)


