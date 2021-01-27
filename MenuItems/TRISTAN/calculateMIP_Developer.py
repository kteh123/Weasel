import CoreModules.DeveloperTools as tools
from CoreModules.DeveloperTools import UserInterfaceTools as ui
from CoreModules.DeveloperTools import PixelArrayDICOMTools as pixel
from CoreModules.DeveloperTools import GenericDICOMTools as dicom
#**************************************************************************
import CoreModules.WEASEL.readDICOM_Image as readDICOM_Image # Write a developer tool to deal with image sort
import numpy as np
from External.tristanAlgorithms import TRISTAN
from CoreModules.imagingTools import formatArrayForAnalysis
FILE_SUFFIX = '_MIP'
#***************************************************************************

def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True


def main(objWeasel):
    if tools.treeView.isASeriesSelected(objWeasel):
        imagePathList = ui.getImagesFromSeries(objWeasel)
        # Pre-processing - this bit uses CoreModules directly. Will have to convert to Developer
        imagePathList, sliceList, numberSlices, _ = readDICOM_Image.sortSequenceByTag(imagePathList, "SliceLocation")
        pixelArray = pixel.getPixelArrayFromDICOM(imagePathList)
        pixelArray = formatArrayForAnalysis(pixelArray, int(len(sliceList)/numberSlices), readDICOM_Image.getDicomDataset(imagePathList[0]), dimension='4D')
        # Run MIP
        pixelArray = TRISTAN(pixelArray).MIP(np.unique(sliceList))
        # Save resulting image to DICOM (and update XML)
        outputhPath = pixel.writeNewPixelArray(objWeasel, pixelArray, imagePathList, FILE_SUFFIX)
        # Refresh the UI screen
        ui.refreshWeasel(objWeasel)
        # Display resulting image
        ui.displayImage(objWeasel, outputhPath)