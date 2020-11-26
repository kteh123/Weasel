from Developer.DeveloperTools import UserInterfaceTools, Series, Image
#**************************************************************************
#Uncomment and edit the following line of code to import the function 
#containing your image processing algorithm. 
FILE_SUFFIX = '_Merged'
#***************************************************************************

def MergeSeriesCopy(objWeasel):
    ui = UserInterfaceTools(objWeasel)
    imageList = ui.getCheckedImages()
    mergedSeries = Image.merge(imageList, series_name='Overwritten_Series', overwrite=True)
    ui.refreshWeasel()
    mergedSeries.DisplaySeries()


def main(objWeasel):
    ui = UserInterfaceTools(objWeasel)
    seriesList = ui.getCheckedSeries()
    mergedSeries = Series.merge(seriesList, series_name='NewSeries', overwrite=False)
    ui.refreshWeasel()
    mergedSeries.DisplaySeries()