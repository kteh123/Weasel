
def main(weasel):
    
    edit = weasel.menu(label = "Edit")

    edit.item(
        label = 'Copy images',
        pipeline = 'Tutorial_CopyImages')

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

    edit.separator()

    edit.item(
        label = 'Copy and merge images',
        pipeline = 'Tutorial_MergeImagesCopy')

    edit.item(
        label = 'Copy and merge series',
        pipeline = 'Tutorial_MergeSeriesCopy')