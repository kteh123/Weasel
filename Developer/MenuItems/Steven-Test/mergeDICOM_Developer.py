from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import PixelArrayDICOMTools as pixel
from Developer.DeveloperTools import GenericDICOMTools as dicom
from Developer.DeveloperTools import Series, Image
#**************************************************************************
#Uncomment and edit the following line of code to import the function 
#containing your image processing algorithm. 
FILE_SUFFIX = '_Merged'
#***************************************************************************

def MergeSeriesCopy(objWeasel):
    imageList = ui.getCheckedImages(objWeasel)
    mergedSeries = Image.merge(imageList, series_name='Overwritten_Series', overwrite=True)
    ui.refreshWeasel(objWeasel)
    mergedSeries.DisplaySeries()


def main(objWeasel):
    seriesList = ui.getCheckedSeries(objWeasel)
    mergedSeries = Series.merge(seriesList, series_name='NewSeries', overwrite=False)
    ui.refreshWeasel(objWeasel)
    mergedSeries.DisplaySeries()