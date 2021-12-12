"""A standard Weasel menu providing functions to edit images and series."""
def main(weasel):
    
    menu = weasel.menu("Edit")

    menu.item(
        label = 'Copy images',
        pipeline = 'Edit__CopyImages')
    menu.item(
        label = 'Copy series',
        pipeline = 'Edit__CopySeries')
    menu.item(
        label = 'Copy studies',
        pipeline = 'Edit__CopyStudies')
    menu.item(
        label = 'Copy subjects',
        pipeline = 'Edit__CopySubject')

    menu.separator()

    menu.item(
        label = 'Delete images',
        pipeline = 'Edit__DeleteImages')
    menu.item(
        label = 'Delete series',
        pipeline = 'Edit__DeleteSeries')
    menu.item(
        label = 'Delete studies',
        pipeline = 'Edit__DeleteStudies')
    menu.item(
        label = 'Delete subjects',
        pipeline = 'Edit__DeleteSubject')

    menu.separator()

    menu.item(
        label = 'Merge images (overwrite)',
        pipeline = 'Edit__MergeImages')
    menu.item(
        label = 'Merge images (copy)',
        pipeline = 'Edit__MergeImagesCopy')
    menu.item(
        label = 'Merge series (overwrite)',
        pipeline = 'Edit__MergeSeries')
    menu.item(
        label = 'Merge series (copy)',
        pipeline = 'Edit__MergeSeriesCopy')

    menu.separator()

    menu.item(
        label = 'Anonymise (overwrite)',
        pipeline = 'Edit__Anonymise')
    menu.item(
        label = 'Anonymise (copy)',
        pipeline = 'Edit__AnonymiseCopy')