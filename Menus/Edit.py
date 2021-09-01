
def main(weasel):
    
    edit = weasel.menu(label = "Edit")

    edit.item(
        label = 'Copy images',
        pipeline = 'Edit__CopyImages')
    edit.item(
        label = 'Copy series',
        pipeline = 'Edit__CopySeries')
    edit.item(
        label = 'Copy studies',
        pipeline = 'Edit__CopyStudies')
    edit.item(
        label = 'Copy subjects',
        pipeline = 'Edit__CopySubject')

    edit.separator()

    edit.item(
        label = 'Delete images',
        pipeline = 'Edit__DeleteImages')
    edit.item(
        label = 'Delete series',
        pipeline = 'Edit__DeleteSeries')
    edit.item(
        label = 'Delete studies',
        pipeline = 'Edit__DeleteStudies')
    edit.item(
        label = 'Delete subjects',
        pipeline = 'Edit__DeleteSubject')

    edit.separator()

    edit.item(
        label = 'Merge images',
        pipeline = 'Edit__MergeImages')
    edit.item(
        label = 'Merge series',
        pipeline = 'Edit__MergeSeries')

    edit.separator()

    edit.item(
        label = 'Copy and merge images',
        pipeline = 'Edit__MergeImagesCopy')
    edit.item(
        label = 'Copy and merge series',
        pipeline = 'Edit__MergeSeriesCopy')