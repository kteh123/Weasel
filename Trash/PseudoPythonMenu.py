from TRISTANmenus import ModelFittingMenu

def MyPseudoCodeMenu(weasel):

    # Create 3 menus, one imported

    tools = weasel.menu(label = 'Tools')
    display = weasel.menu(label = 'Display')
    tristan = ModelFittingMenu(weasel)

    # Create 2 submenus

    tools_copy = tools.menu(label = 'Copy')
    display_images = display.menu(label = 'Images')

    #Create menu items under the various menus above

    tools.item(
        label = 'View Series/Image',
        shortcut = 'Ctrl + V',
        tooltip = 'View DICOM',
        module = 'ViewImage')

    tools.item(
        label = 'View Metadata',
        shortcut = 'Ctrl + M',
        tooltip = 'View DICOM header',
        module = 'ViewMetaData')

    tools_copy.item(
        label = 'Copy Series',
        module = 'CopyDICOM_Image')

    tools_copy.item(
        label = 'Copy Series',
        module = 'CopyDICOM_Image')
 
    display.item(
        label = 'Copy Series',
        module = 'CopyDICOM_Image')

    display_images.item(
        label = 'Copy Series 2',
        module = 'CopyDICOM_Series2')

    #Extend the imported Tristan menu with one item

    tristan.item(
        label = 'Copy Series 3',
        module = 'CopyDICOM_Series3')
    
