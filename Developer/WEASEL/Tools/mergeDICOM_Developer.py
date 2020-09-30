import Developer.WEASEL.Tools.developerToolsModule as tool
#**************************************************************************
#Added by third party developer to the template module. 
#The function containing the image processing algorithm must be given the 
#generic name, funcAlgorithm
#uncomment and edit the following line of code to import the function 
#containing your image processing algorithm. 
FILE_SUFFIX = '_Merged'
#***************************************************************************

def MergeSeries(objWeasel):
    imagePathList = tool.getImagePathList(objWeasel)
    mergedSeries = tool.mergeDicomIntoOneSeries(objWeasel, imagePathList, series_description="Copied_Series", overwrite=False)
    tool.displayImage(objWeasel, mergedSeries)


def MergeSeriesNoCopy(objWeasel):
    imagePathList = tool.getImagePathList(objWeasel)
    mergedSeries = tool.mergeDicomIntoOneSeries(objWeasel, imagePathList, series_description="Series", overwrite=True)
    tool.displayImage(objWeasel, mergedSeries)