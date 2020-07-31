import Developer.WEASEL.Tools.developerToolsModule as tool
#**************************************************************************
#Added by third party developer to the template module. 
#The function containing the image processing algorithm must be given the 
#generic name, funcAlgorithm
#uncomment and edit the following line of code to import the function 
#containing your image processing algorith. 
from Developer.WEASEL.ScientificLibrary.imagingTools import gaussianFilter
FILE_SUFFIX = '_Gaussian'
standard_deviation_filter = 10
#***************************************************************************

def processPipeline2D(objWeasel):
    if tool.treeView.isAnImageSelected(objWeasel):
        imagePath = tool.getImagePath(objWeasel)
        derivedImageFileName = tool.setNewFilePath(imagePath, FILE_SUFFIX)
        pixelArray = tool.getPixelArrayFromDICOM(imagePath)
        derivedImage = tool.applyProcessInOneImage(gaussianFilter, pixelArray, standard_deviation_filter)
        tool.saveNewDICOMAndDisplayResult(objWeasel, imagePath, derivedImageFileName, derivedImage, FILE_SUFFIX)
    elif tool.treeView.isASeriesSelected(objWeasel):
        imagePathList = tool.getImagePathList(objWeasel)
        derivedImagePathList, derivedImageList = tool.applyProcessIterativelyInSeries(objWeasel, imagePathList, FILE_SUFFIX, gaussianFilter, standard_deviation_filter, progress_bar=True)        
        tool.saveNewDICOMAndDisplayResult(objWeasel, imagePathList, derivedImagePathList, derivedImageList, FILE_SUFFIX)


def processPipeline3D(objWeasel):
        imagePathList = tool.getImagePathList(objWeasel)
        tool.showProcessingMessageBox(objWeasel)
        pixelArray = tool.getPixelArrayFromDICOM(imagePathList)
        derivedImage = tool.applyProcessInOneImage(gaussianFilter, pixelArray, standard_deviation_filter)
        derivedImagePathList, derivedImageList = tool.prepareBulkSeriesSave(objWeasel, imagePathList, derivedImage, FILE_SUFFIX)
        imagePathList = imagePathList[:len(derivedImagePathList)]
        tool.saveNewDICOMAndDisplayResult(objWeasel, imagePathList, derivedImagePathList, derivedImageList, FILE_SUFFIX)
