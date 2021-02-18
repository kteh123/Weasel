from CoreModules.DeveloperTools import UserInterfaceTools, Series, Image
#**************************************************************************
#Uncomment and edit the following line of code to import the function
#containing your image processing algorithm.
FILE_SUFFIX = '_Merged'
#***************************************************************************

def MergeSeriesCopy(objWeasel):
    ui = UserInterfaceTools(objWeasel)
    imageList = ui.getCheckedImages()
    if imageList is None: return # Exit function if no images are checked
    mergedSeries = Image.merge(imageList, series_name='Overwritten_Series', overwrite=True)
    ui.refreshWeasel()
    mergedSeries.Display()


def main(objWeasel):
    ui = UserInterfaceTools(objWeasel)
    seriesList = ui.getCheckedSeries()
    if seriesList is None: return # Exit function if no series are checked
    mergedSeries = Series.merge(seriesList, series_name='NewSeries', overwrite=False)
    ui.refreshWeasel()
    mergedSeries.Display()