
def main(weasel):

    tools = weasel.menu(label = "Tools")

    tools.item(
        label = 'View Series/Image',
        shortcut = 'Ctrl+V',
        tooltip = 'View DICOM Image or series',
        pipeline = 'ViewImage',
        context = True)

    tools.item(
        label = 'View Series/Image with multiple sliders',
        shortcut = 'Ctrl+M',
        tooltip = 'View DICOM Image or series with multiple sliders',
        pipeline = 'ViewImageMultiSlider',
        context = True)

    tools.item(
        label = 'View Series/Image with ROI',
        shortcut = 'Ctrl+R',
        tooltip = 'View DICOM Image or series with the ROI tool',
        pipeline = 'ViewROIImage',
        context = True)

    tools.separator()

    tools.item(
        label = 'View Metadata',
        shortcut = 'Ctrl+M',
        tooltip = 'View DICOM Image or series metadata',
        pipeline = 'ViewMetaData',
        context = True)

    tools.item(
        label = 'Export to NIfTI',
        pipeline = 'ExportToNIfTI',
        shortcut = 'Ctrl+S',
        tooltip = 'Save selected series as NIfTI',
        context = True)



    tutorial = weasel.menu(label = "Tutorial")

    tutorial.item(
        label = 'Display images',
        pipeline = 'Tutorial_DisplayImages')

    tutorial.item(
        label = 'Display series',
        pipeline = 'Tutorial_DisplaySeries')

    tutorial.separator()

    tutorial.item(
        label = 'Copy images',
        pipeline = 'Tutorial_CopyImages')
        
    tutorial.item(
        label = 'Copy images (without a progress bar)',
        pipeline = 'Tutorial_CopyImagesDirect')

    tutorial.item(
        label = 'Copy series',
        pipeline = 'Tutorial_CopySeries')

    tutorial.separator()

    tutorial.item(
        label = 'Copy studies', 
        pipeline = 'Tutorial_CopyStudies')

    tutorial.item(
        label = 'Copy subjects', 
        pipeline = 'Tutorial_CopySubject')	
	
    tutorial.item(
        label = 'Delete studies', 
        pipeline = 'Tutorial_DeleteStudies')		
		    
    tutorial.item(
        label = 'Delete subjects',
        pipeline = 'Tutorial_DeleteSubject')    
	
    tutorial.separator()

    tutorial.item(
        label = 'Delete subjects',
        pipeline = 'Tutorial_DeleteSubject') 
    
    tutorial.item(
        label = 'Delete series',
        pipeline = 'Tutorial_DeleteSeries') 

    tutorial.item(
        label = 'Delete images',
        pipeline = 'Tutorial_Delete') 
        
    tutorial.separator()

    tutorial.item(
        label = 'Merge images into a new series',
        pipeline = 'Tutorial_MergeImages')

    tutorial.item(
        label = 'Copy and merge images',
        pipeline = 'Tutorial_MergeImagesCopy')

    tutorial.item(
        label = 'Copy and merge images',
        pipeline = 'Tutorial_MergeImagesCopy')

    tutorial.item(
        label = 'Merge series into a new series',
        pipeline = 'Tutorial_MergeSeries')

    tutorial.item(
        label = 'Copy and merge series',
        pipeline = 'Tutorial_MergeSeriesCopy')
    
    tutorial.item(
        label = 'Merge studies',
        pipeline = 'Tutorial_MergeStudies')

    tutorial.item(
        label = 'Merge subjects',
        pipeline = 'Tutorial_MergeSubjects')
		
    tutorial.separator()

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
