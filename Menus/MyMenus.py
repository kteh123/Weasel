from Menus.View import main as menu_view
from Menus.Edit import main as menu_edit

def main(weasel):

    menu_view(weasel)
    menu_edit(weasel)

    tutorial = weasel.menu(label = "Tutorial")

    tutorial.item(
        label = 'Invert pixel values in place (image-by-image)',
        shortcut = 'Ctrl+R',
        pipeline = 'Tutorial_InvertPixelValues')

    tutorial.item(
        label = 'Invert pixel values in place (series-by-series)',
        shortcut = 'Ctrl+P',
        pipeline = 'Tutorial_InvertPixelValuesSeries')

    tutorial.item(
        label = 'Invert pixel values in a new series (image-by-image)',
        shortcut = 'Ctrl+T',
        pipeline = 'Tutorial_InvertPixelValuesInNewSeries')
        
    tutorial.item(
        label = 'Invert pixel values in a new series (series-by-series)',
        shortcut = 'Ctrl+U',
        pipeline = 'Tutorial_InvertPixelValuesSeriesInNewSeries')
    
    tutorial.separator()

    tutorial.item(
        label = 'Threshold pixel values in a new series (image-by-image)',
        shortcut = 'Ctrl+V',
        pipeline = 'Tutorial_ThresholdPixelValuesInNewSeries')
    
    tutorial.item(
        label = 'Square pixel values in a new series (image-by-image)',
        shortcut = 'Ctrl+W',
        pipeline = 'Tutorial_SquarePixelValuesInNewSeries') 
	
    tutorial.item(
        label = 'Apply Gaussian filter to pixel values in a new series (image-by-image)',
        shortcut = 'Ctrl+X',
        pipeline = 'Tutorial_GaussianPixelValuesInNewSeries') 
	
    tutorial.separator()

    tutorial.item(
        label = 'Filter images with a local filter',
        pipeline = 'Tutorial_LocalFilterImages') 

    tutorial.item(
        label = 'User input tutorial',
        pipeline = 'Tutorial_UserInput') 
		
    tutorial.separator()

    tutorial.item(
        label = 'Anonymise',
        pipeline = 'Tutorial_Anonymise') 

    tutorial.item(
        label = 'Anonymise a copy',
        pipeline = 'Tutorial_AnonymiseCopy') 

    tutorial.item(
        label = 'Anonymise Patient ID',
        pipeline = 'Tutorial_AnonymiseID')



    examples = weasel.menu("Examples")

    examples.item(
        label = 'Binary Operations',
        pipeline = 'BinaryOperationsOnImages')
    examples.item(
        label = 'Binary Operations (Tutorials Version)',
        pipeline = 'Tutorial_BinaryOperations')
    examples.item(
        label = 'Merge Series by Acquisition Time',
        pipeline = 'Test_MergeSeriesByAcquisitionTime')
    examples.item(
        label = 'Create New Series by Slice Location',
        pipeline = 'Test_CreateSeriesBySliceLocation')



    help = weasel.menu(label = "Help")  
        
    help.item(
        label = 'Help', 
        icon = 'Documents/images/question-mark.png', 
        pipeline = 'Help')
