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
    menu_help(weasel)

    menu = weasel.menu(label = "In Progress")

    menu.item(
        label = 'Merge Series by Acquisition Time',
        pipeline = 'Test_MergeSeriesByAcquisitionTime')
    menu.item(
        label = 'Create New Series by Slice Location',
        pipeline = 'Test_CreateSeriesBySliceLocation')





