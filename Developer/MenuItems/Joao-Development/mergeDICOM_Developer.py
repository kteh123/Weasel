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
    # imagePathList = ui.getListOfAllSelectedImages(objWeasel)
    imageList = ui.getCheckedImages(objWeasel)
    # mergedSeries = dicom.mergeDicomIntoOneSeries(objWeasel, imagePathList, series_name="Copied_Series", overwrite=True)
    mergedSeries = Image.merge(imageList, series_name='Overwritten_Series', overwrite=False)
    ui.refreshWeasel(objWeasel)
    # ui.displayImages(objWeasel, mergedSeries)
    mergedSeries.DisplaySeries()


def main(objWeasel):
    # imagePathList = ui.getListOfAllSelectedImages(objWeasel)
    seriesList = ui.getCheckedSeries(objWeasel)
    # mergedSeries = dicom.mergeDicomIntoOneSeries(objWeasel, imagePathList, series_name="Series", overwrite=False)
    mergedSeries = Series.merge(seriesList, series_name='NewSeries', overwrite=False)
    ui.refreshWeasel(objWeasel)
    # ui.displayImages(objWeasel, mergedSeries)
    mergedSeries.DisplaySeries()