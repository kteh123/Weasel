from Developer.MenuItems.DeveloperTools import UserInterfaceTools as ui
from Developer.MenuItems.DeveloperTools import PixelArrayDICOMTools as pixel
from Developer.MenuItems.DeveloperTools import GenericDICOMTools as dicom
#**************************************************************************
#Uncomment and edit the following line of code to import the function 
#containing your image processing algorithm. 
FILE_SUFFIX = '_Merged'
#***************************************************************************

def MergeSeriesCopy(objWeasel):
    imagePathList = ui.getAllSelectedImages(objWeasel)
    mergedSeries = dicom.mergeDicomIntoOneSeries(objWeasel, imagePathList, series_description="Copied_Series", overwrite=False)
    ui.displayImage(objWeasel, mergedSeries)


def main(objWeasel):
    imagePathList = ui.getAllSelectedImages(objWeasel)
    mergedSeries = dicom.mergeDicomIntoOneSeries(objWeasel, imagePathList, series_description="Series", overwrite=True)
    ui.displayImage(objWeasel, mergedSeries)