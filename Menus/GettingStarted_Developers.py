""" 
Template menu illustrating the different approaches 
to building menus through the Weasel Programming Interface
"""

# Insert a menu from a local menu library
# In external applications, do not import from WEASEL/Menus
# as this can evolve. Only import your own menus library.
from Menus.Tutorial import main as menu_tutorial

def main(weasel):
   
    # Include the default Weasel menus File, View, Edit
    weasel.menu_file()
    weasel.menu_view()
    weasel.menu_edit()

    # Include a user-defined menu imported from a local Library
    menu_tutorial(weasel)
    
    # Create a new menu with Favourite Pipelines
    menu = weasel.menu("Favourites")

    # List the pipelines that should go under Favourites
    menu.item(
        label = 'Hello World!',
        pipeline = 'Tutorial__HelloWorld')
    menu.item(
        label = 'DICOM header',
        tooltip = 'View DICOM Image or series header',
        pipeline = 'View__DICOMheader')

    # Draw a line in the menu to separate different parts
    menu.separator()

    # Continue adding pipelines
    menu.item(
        label = 'Gaussian filter (copy)',
        tooltip = 'Filter images with user-defined settings',
        pipeline = 'Tutorial__GaussianPixelValuesInNewSeries')
    menu.item(
        label = 'Merge images (copy)',
        pipeline = 'Edit__MergeImagesCopy')

    # Insert the default Help menu
    weasel.menu_help()

    # Create another user defined menu WIP
    menu = weasel.menu("WIP")
    menu.item(
        label = 'Merge Series by Acquisition Time',
        pipeline = 'Test_MergeSeriesByAcquisitionTime')
    menu.item(
        label = 'Create New Series by Slice Location',
        pipeline = 'Test_CreateSeriesBySliceLocation')
    
    

  