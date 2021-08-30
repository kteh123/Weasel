from Menus.File import main as menu_file
from Menus.View import main as menu_view
from Menus.Edit import main as menu_edit

def main(weasel):
   
    menu_file(weasel)
    menu_view(weasel)
    menu_edit(weasel)

    examples = weasel.menu(label = "Examples")

    examples.item(
        label = 'Invert pixel values in place (image-by-image)',
        shortcut = 'Ctrl+I',
        tooltip = 'Calculates and saves the invert of the selected images',
        pipeline = 'Tutorial_InvertPixelValues')

    examples.item(
        label = 'Square pixel values in a new series (image-by-image)',
        shortcut = 'Ctrl+S',
        tooltip = 'Calculates and saves the square of the selected series',
        pipeline = 'Tutorial_SquarePixelValuesInNewSeries')

    examples.item(
        label = 'Threshold pixel values in a new series (image-by-image)',
        shortcut = 'Ctrl+T',
        tooltip = 'Applies the selected threshold values to the selected series',
        pipeline = 'Tutorial_ThresholdPixelValuesInNewSeries')

    examples.item(
        label = 'Filter images with a local filter',
        shortcut = 'Ctrl+F',
        tooltip = 'Applies the selected filter to the selected images',
        pipeline = 'Tutorial_LocalFilterImages')

    examples.item(
        label = 'Anonymise Patient ID',
        shortcut = 'Ctrl+A',
        tooltip = 'Assigns a new Patient ID to the selected images',
        pipeline = 'Tutorial_AnonymiseID')
    


  