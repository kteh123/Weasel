
def main(weasel):
    
    edit = weasel.menu(label = "Edit")

    edit.item(
        label = 'Copy images',
        pipeline = 'Edit__CopyImages')
    edit.item(
        label = 'Copy series',
        pipeline = 'Edit__CopySeries')

    edit.separator()

    edit.item(
        label = 'Delete images',
        pipeline = 'Edit__DeleteImages')
    edit.item(
        label = 'Delete series',
        pipeline = 'Edit__DeleteSeries')

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