from CoreModules.WEASEL.PythonMenuBuilder  import PythonMenuBuilder as menuBuilder

def main(pointerToWeasel):
    #Create View Menu
    view = menuBuilder(pointerToWeasel, "View")

    view.addItem(itemLabel = 'View Series/Image',
                 shortcut = 'Ctrl+V',
                 tooltip = 'View DICOM Image or series',
                 moduleName = 'ViewImage',
                 context=True)

    view.addItem(itemLabel = 'View Series/Image with ROI',
                 shortcut = 'Ctrl+R',
                 tooltip = 'View DICOM Image or series with the ROI tool',
                 moduleName = 'ViewROIImage',
                 context=True)

    view.addItem(itemLabel = 'View Metadata',
                 shortcut = 'Ctrl+M',
                 tooltip = 'View DICOM Image or series metadata',
                 moduleName = 'ViewMetaData',
                 context=True)

    #Create Edit menu
    edit = menuBuilder(pointerToWeasel, "Edit")

    edit.addItem(itemLabel = 'Copy images',
                 moduleName = 'Tutorial_CopyImages')
        
    edit.addItem(itemLabel = 'Copy images (without a progress bar)',
                 moduleName = 'Tutorial_CopyImagesDirect')

    edit.addItem(itemLabel = 'Copy series',
                 moduleName = 'Tutorial_CopySeries')

    edit.addItem(itemLabel = 'Copy studies',
                 moduleName = 'Tutorial_CopyStudies')

    edit.addItem(itemLabel = 'Copy subjects',
                 moduleName = 'Tutorial_CopySubject')	 
	
    edit.addSeparator()

    edit.addItem(itemLabel = 'Delete images',
                 moduleName = 'Tutorial_Delete')
    
    edit.addItem(itemLabel = 'Delete series',
                 moduleName = 'Tutorial_DeleteSeries')
    
    edit.addItem(itemLabel = 'Delete studies',
                 moduleName = 'Tutorial_DeleteStudies') 
    
    edit.addItem(itemLabel = 'Delete subjects',
                 moduleName = 'Tutorial_DeleteSubject') 
    
    edit.addSeparator()

    edit.addItem(itemLabel = 'Merge images into a new series',
                 moduleName = 'Tutorial_MergeImages')

    edit.addItem(itemLabel = 'Merge series into a new series',
                 moduleName = 'Tutorial_MergeSeries')

    edit.addItem(itemLabel = 'Merge studies',
                 moduleName = 'Tutorial_MergeStudies')

    edit.addItem(itemLabel = 'Merge subjects',
                 moduleName = 'Tutorial_MergeSubjects')
    
    #Create Examples Menu
    examples = menuBuilder(pointerToWeasel, "Examples")

    examples.addItem(itemLabel = 'Invert pixel values in place (image-by-image)',
                     shortcut = 'Ctrl+I',
                     tooltip = 'Calculates and saves the invert of the selected images',
                     moduleName = 'Tutorial_InvertPixelValues')

    examples.addItem(itemLabel = 'Square pixel values in a new series (image-by-image)',
                     shortcut = 'Ctrl+S',
                     tooltip = 'Calculates and saves the square of the selected series',
                     moduleName = 'Tutorial_SquarePixelValuesInNewSeries')

    examples.addItem(itemLabel = 'Threshold pixel values in a new series (image-by-image)',
                     shortcut = 'Ctrl+T',
                     tooltip = 'Applies the selected threshold values to the selected series',
                     moduleName = 'Tutorial_ThresholdPixelValuesInNewSeries')

    examples.addItem(itemLabel = 'Filter images with a local filter',
                     shortcut = 'Ctrl+F',
                     tooltip = 'Applies the selected filter to the selected images',
                     moduleName = 'Tutorial_LocalFilterImages')

    examples.addItem(itemLabel = 'Anonymise Patient ID',
                     shortcut = 'Ctrl+A',
                     tooltip = 'Assigns a new Patient ID to the selected images',
                     moduleName = 'Tutorial_AnonymiseID')
    


  