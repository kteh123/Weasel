from Menus.File import main as menu_file
from Menus.View import main as menu_view
from Menus.Edit import main as menu_edit
from Menus.Tutorial import main as menu_tutorial
from Menus.Help import main as menu_help

def main(weasel):
   
    menu_file(weasel)
    menu_view(weasel)
    menu_edit(weasel)
    menu_tutorial(weasel)
    
    menu = weasel.menu("Favourites")
    menu.item(
        label = 'Hello World!',
        pipeline = 'Tutorial__HelloWorld')
    menu.item(
        label = 'DICOM header',
        tooltip = 'View DICOM Image or series header',
        pipeline = 'View__DICOMheader')
    menu.separator()
    menu.item(
        label = 'Gaussian filter (copy)',
        tooltip = 'Filter images with user-defined settings',
        pipeline = 'Tutorial__GaussianPixelValuesInNewSeries')
    menu.item(
        label = 'Merge images (copy)',
        pipeline = 'Edit__MergeImagesCopy')
    menu.separator()
    menu.item(
        label = "Save selections",
        shortcut = 'Ctrl+P',
        tooltip = "Save the current selections of images",
        pipeline = 'File__SaveTreeView')

    menu_help(weasel)

    menu = weasel.menu("WIP")
    menu.item(
        label = 'Merge Series by Acquisition Time',
        pipeline = 'Test_MergeSeriesByAcquisitionTime')
    menu.item(
        label = 'Create New Series by Slice Location',
        pipeline = 'Test_CreateSeriesBySliceLocation')
    
    

  