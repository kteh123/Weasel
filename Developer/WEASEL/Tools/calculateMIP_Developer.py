import Developer.WEASEL.Tools.developerToolsModule as tool
#**************************************************************************
#Added by third party developer to the template module. 
#The function containing the image processing algorithm must be given the 
#generic name, funcAlgorithm
#uncomment and edit the following line of code to import the function 
#containing your image processing algorithm. 
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image # Write a developer tool to deal with image sort
import numpy as np
from Developer.WEASEL.ScientificLibrary.tristanAlgorithms import TRISTAN
from Developer.WEASEL.ScientificLibrary.imagingTools import formatArrayForAnalysis
FILE_SUFFIX = '_MIP'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True


def TimeMIP(objWeasel):
    if tool.treeView.isASeriesSelected(objWeasel):
        imagePathList = tool.getImagePathList(objWeasel)

        # Pre-processing - this bit uses CoreModules directly. Will have to convert to Developer
        imagePathList, sliceList, numberSlices, _ = readDICOM_Image.sortSequenceByTag(imagePathList, "SliceLocation")
        pixelArray = tool.getPixelArrayFromDICOM(imagePathList)
        pixelArray = formatArrayForAnalysis(pixelArray, int(len(sliceList)/numberSlices), readDICOM_Image.getDicomDataset(imagePathList[0]), dimension='4D')
        
        derivedImage = TRISTAN(pixelArray).MIP(np.unique(sliceList))
        derivedImagePathList, derivedImageList = tool.prepareBulkSeriesSave(objWeasel, imagePathList, derivedImage, FILE_SUFFIX)
        tool.saveNewDICOMAndDisplayResult(objWeasel, imagePathList, derivedImagePathList, derivedImageList, FILE_SUFFIX)
