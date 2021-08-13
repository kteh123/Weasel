from CoreModules.WEASEL.PythonMenuBuilder  import PythonMenuBuilder as menuBuilder

def main(pointerToWeasel):
    #Create Tools Menu
    tools = menuBuilder(pointerToWeasel, "Tools")

    tools.addItem(itemLabel = 'View Series/Image',
               shortcut = 'Ctrl+V',
               tooltip = 'View DICOM Image or series',
               moduleName = 'ViewImage',
               context=True)

    tools.addItem(itemLabel = 'View Series/Image with multiple sliders',
               shortcut = 'Ctrl+M',
               tooltip = 'View DICOM Image or series with multiple sliders',
               moduleName = 'ViewImageMultiSlider',
               context=True)

    tools.addItem(itemLabel = 'View Series/Image with ROI',
               shortcut = 'Ctrl+R',
               tooltip = 'View DICOM Image or series with the ROI tool',
               moduleName = 'ViewROIImage',
               context=True)

    tools.addSeparator()

    tools.addItem(itemLabel = 'View Metadata',
               shortcut = 'Ctrl+M',
               tooltip = 'View DICOM Image or series metadata',
               moduleName = 'ViewMetaData',
               context=True)
    
    tools.addItem(itemLabel = 'Export to NIfTI',
               moduleName = 'ExportToNIfTI',
               shortcut = 'Ctrl+S',
               tooltip = 'Save selected series as NIfTI',
               context=True)

    #Create Tutorial menu
    tutorial = menuBuilder(pointerToWeasel, "Tutorial")

    tutorial.addItem(itemLabel = 'Display images',
               moduleName = 'Tutorial_DisplayImages')

    tutorial.addItem(itemLabel = 'Display series',
               moduleName = 'Tutorial_DisplaySeries')

    tutorial.addSeparator()

    tutorial.addItem(itemLabel = 'Copy images',
               moduleName = 'Tutorial_CopyImages')
        
    tutorial.addItem(itemLabel = 'Copy images (without a progress bar)',
               moduleName = 'Tutorial_CopyImagesDirect')

    tutorial.addItem(itemLabel = 'Copy series',
               moduleName = 'Tutorial_CopySeries')

    tutorial.addSeparator()

    tutorial.addItem(itemLabel = 'Copy studies', moduleName = 'Tutorial_CopyStudies')

    tutorial.addItem(itemLabel = 'Copy subjects', moduleName = 'Tutorial_CopySubject')	
	
    tutorial.addItem(itemLabel = 'Delete studies', moduleName = 'Tutorial_DeleteStudies')		
		    
    tutorial.addItem(itemLabel = 'Delete subjects',moduleName = 'Tutorial_DeleteSubject')    
	
    tutorial.addSeparator()

    tutorial.addItem(itemLabel = 'Delete subjects',
               moduleName = 'Tutorial_DeleteSubject') 
    
    tutorial.addItem(itemLabel = 'Delete series',
               moduleName = 'Tutorial_DeleteSeries') 

    tutorial.addItem(itemLabel = 'Delete images',
               moduleName = 'Tutorial_Delete') 
        
    tutorial.addSeparator()

    tutorial.addItem(itemLabel = 'Merge images into a new series',
               moduleName = 'Tutorial_MergeImages')

    tutorial.addItem(itemLabel = 'Copy and merge images',
               moduleName = 'Tutorial_MergeImagesCopy')

    tutorial.addItem(itemLabel = 'Copy and merge images',
               moduleName = 'Tutorial_MergeImagesCopy')

    tutorial.addItem(itemLabel = 'Merge series into a new series',
               moduleName = 'Tutorial_MergeSeries')

    tutorial.addItem(itemLabel = 'Copy and merge series',
               moduleName = 'Tutorial_MergeSeriesCopy')
    
    tutorial.addItem(itemLabel = 'Merge studies',
               moduleName = 'Tutorial_MergeStudies')

    tutorial.addItem(itemLabel = 'Merge subjects',
               moduleName = 'Tutorial_MergeSubjects')
		
    tutorial.addSeparator()

    tutorial.addItem(itemLabel = 'Invert pixel values in place (image-by-image)',
               shortcut = 'Ctrl+R',
               moduleName = 'Tutorial_InvertPixelValues')

    tutorial.addItem(itemLabel = 'Invert pixel values in place (series-by-series)',
               shortcut = 'Ctrl+P',
               moduleName = 'Tutorial_InvertPixelValuesSeries')

    tutorial.addItem(itemLabel = 'Invert pixel values in a new series (image-by-image)',
               shortcut = 'Ctrl+T',
               moduleName = 'Tutorial_InvertPixelValuesInNewSeries')
        
    tutorial.addItem(itemLabel = 'Invert pixel values in a new series (series-by-series)',
               shortcut = 'Ctrl+U',
               moduleName = 'Tutorial_InvertPixelValuesSeriesInNewSeries')
    
    tutorial.addSeparator()

    tutorial.addItem(itemLabel = 'Threshold pixel values in a new series (image-by-image)',
               shortcut = 'Ctrl+V',
               moduleName = 'Tutorial_ThresholdPixelValuesInNewSeries')
    
    tutorial.addItem(itemLabel = 'Square pixel values in a new series (image-by-image)',
                  shortcut = 'Ctrl+W',
                  moduleName = 'Tutorial_SquarePixelValuesInNewSeries') 
	
    tutorial.addItem(itemLabel = 'Apply Gaussian filter to pixel values in a new series (image-by-image)',
               shortcut = 'Ctrl+X',
               moduleName = 'Tutorial_GaussianPixelValuesInNewSeries') 
	
    tutorial.addSeparator()

    tutorial.addItem(itemLabel = 'Filter images with a local filter',
               moduleName = 'Tutorial_LocalFilterImages') 

    tutorial.addItem(itemLabel = 'User input tutorial',
               moduleName = 'Tutorial_UserInput') 
		
    tutorial.addSeparator()

    tutorial.addItem(itemLabel = 'Anonymise',
               moduleName = 'Tutorial_Anonymise') 

    tutorial.addItem(itemLabel = 'Anonymise a copy',
               moduleName = 'Tutorial_AnonymiseCopy') 

    tutorial.addItem(itemLabel = 'Anonymise Patient ID',
               moduleName = 'Tutorial_AnonymiseID')


    #Create Examples Menu
    examples = menuBuilder(pointerToWeasel, "Examples")
    examples.addItem(itemLabel = 'Binary Operations',
               moduleName = 'BinaryOperationsOnImages')
    examples.addItem(itemLabel = 'Binary Operations (Tutorials Version)',
               moduleName = 'Tutorial_BinaryOperations')
    examples.addItem(itemLabel = 'Merge Series by Acquisition Time',
               moduleName = 'Test_MergeSeriesByAcquisitionTime')
    examples.addItem(itemLabel = 'Create New Series by Slice Location',
               moduleName = 'Test_CreateSeriesBySliceLocation')

    tristan_rat = menuBuilder(pointerToWeasel, "TRISTAN Rat")      
    tristan_rat.addItem(itemLabel = 'Preprocessing',
     moduleName = 'TRISTAN_Preprocessing')
    tristan_rat.addItem(itemLabel = 'Signal/Mask to DICOM',
     moduleName = 'Tutorial_Ferret_Joao')
    tristan_rat.addItem(itemLabel = 'Launch Ferret',
     moduleName = 'Tutorial_LaunchFerret')

    help = menuBuilder(pointerToWeasel, "Help")      
    help.addItem(itemLabel = 'Help',     moduleName = 'Help')
