from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import PixelArrayDICOMTools as pixel
from Developer.DeveloperTools import GenericDICOMTools as dicom
#**************************************************************************
#Uncomment and edit the following line of code to import the function 
#containing your image processing algorithm. 
FILE_SUFFIX = '_Merged'
#***************************************************************************

def MergeSeriesCopy(objWeasel):
    # imagePathList = ui.getListOfAllSelectedImages(objWeasel)
    imagePathList = ui.getListOfAllCheckedImages(objWeasel)
    mergedSeries = dicom.mergeDicomIntoOneSeries(objWeasel, imagePathList, series_name="Copied_Series", overwrite=True)
    ui.refreshWeasel(objWeasel)
    ui.displayImage(objWeasel, mergedSeries)


def main(objWeasel):
    # imagePathList = ui.getListOfAllSelectedImages(objWeasel)
    imagePathList = ui.getListOfAllCheckedImages(objWeasel)
    mergedSeries = dicom.mergeDicomIntoOneSeries(objWeasel, imagePathList, series_name="Series", overwrite=False)
    ui.refreshWeasel(objWeasel)
    ui.displayImage(objWeasel, mergedSeries)