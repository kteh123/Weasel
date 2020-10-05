import Developer.MenuItems.developerToolsModule as tool
#**************************************************************************
#Added by third party developer to the template module. 
#The function containing the image processing algorithm must be given the 
#generic name, funcAlgorithm
#uncomment and edit the following line of code to import the function 
#containing your image processing algorith. 
from Developer.SciPackages.imagingTools import thresholdPixelArray
FILE_SUFFIX = '_Thresholded'
#***************************************************************************

def main(objWeasel):
    if tool.treeView.isAnImageSelected(objWeasel):
        imagePath = tool.getImagePath(objWeasel)
        #derivedImageFileName = tool.setNewFilePath(imagePath, FILE_SUFFIX)
        pixelArray = tool.getPixelArrayFromDICOM(imagePath)
        # Lower and upper threshold from the input window. No parameter validation here
        inputDict = {"Lower Threshold":"integer", "Upper Threshold":"integer"}
        info = "Insert a value between 0 and 100. Upper threshold must be greater than lower threshold"
        paramList = tool.inputWindow(inputDict, title="Input Parameters", helpText=info)
        low_thresh = paramList[0]
        high_thresh = paramList[1]
        derivedImage = tool.applyProcessInOneImage(thresholdPixelArray, pixelArray, low_thresh, high_thresh)
        tool.overwriteDICOMAndDisplayResult(objWeasel, imagePath, derivedImage)
    elif tool.treeView.isASeriesSelected(objWeasel):
        imagePathList = tool.getImagePathList(objWeasel)
        # Progress bar set to True and threshold values hard-coded (inserted in code)
        derivedImagePathList, derivedImageList = tool.applyProcessIterativelyInSeries(objWeasel, imagePathList, FILE_SUFFIX, thresholdPixelArray, 0, 100, progress_bar=False)
        #tool.overwriteDICOMAndDisplayResult(objWeasel, imagePathList, derivedImagePathList)
        tool.saveNewDICOMAndDisplayResult(objWeasel, imagePathList, derivedImagePathList, derivedImageList, FILE_SUFFIX)
