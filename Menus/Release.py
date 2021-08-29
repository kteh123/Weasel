
def main(weasel):
   
    view = weasel.menu(label = "View")

    view.item(
        label = 'View Series/Image',
        shortcut = 'Ctrl+V',
        tooltip = 'View DICOM Image or series',
        pipeline = 'ViewImage',
        context=True)

    view.item(
        label = 'View Series/Image with ROI',
        shortcut = 'Ctrl+R',
        tooltip = 'View DICOM Image or series with the ROI tool',
        pipeline = 'ViewROIImage',
        context=True)

    view.item(
        label = 'View Metadata',
        shortcut = 'Ctrl+M',
        tooltip = 'View DICOM Image or series metadata',
        pipeline = 'ViewMetaData',
        context=True)



    edit = weasel.menu(label = "Edit")

    edit.item(
        label = 'Copy images',
        pipeline = 'Tutorial_CopyImages')
        
    edit.item(
        label = 'Copy images (without a progress bar)',
        pipeline = 'Tutorial_CopyImagesDirect')

    edit.item(
        label = 'Copy series',
        pipeline = 'Tutorial_CopySeries')

    edit.item(
        label = 'Copy studies',
        pipeline = 'Tutorial_CopyStudies')

    edit.item(
        label = 'Copy subjects',
        pipeline = 'Tutorial_CopySubject')	 
	
    edit.separator()

    edit.item(
        label = 'Delete images',
        pipeline = 'Tutorial_Delete')
    
    edit.item(
        label = 'Delete series',
        pipeline = 'Tutorial_DeleteSeries')
    
    edit.item(
        label = 'Delete studies',
        pipeline = 'Tutorial_DeleteStudies') 
    
    edit.item(
        label = 'Delete subjects',
        pipeline = 'Tutorial_DeleteSubject') 
    
    edit.separator()

    edit.item(
        label = 'Merge images into a new series',
        pipeline = 'Tutorial_MergeImages')

    edit.item(
        label = 'Merge series into a new series',
        pipeline = 'Tutorial_MergeSeries')

    edit.item(
        label = 'Merge studies',
        pipeline = 'Tutorial_MergeStudies')

    edit.item(
        label = 'Merge subjects',
        pipeline = 'Tutorial_MergeSubjects')
    



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
    


  