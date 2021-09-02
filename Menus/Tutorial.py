def main(weasel):
   
    menu = weasel.menu("Tutorial")

    menu.item(
        label = 'Hello World!',
        pipeline = 'Tutorial__HelloWorld')

    menu.separator()

    menu.item(
        label = 'Invert images (overwrite)',
        tooltip = 'Replace pixel data of selected images by their inverse',
        pipeline = 'Tutorial__InvertPixelValues')
    menu.item(
        label = 'Invert images (copy)',
        tooltip = 'Replace pixel data of selected images by their inverse, saving the result in a new series',
        pipeline = 'Tutorial__InvertPixelValuesInNewSeries')
    menu.item(
        label = 'Invert series (overwrite)',
        tooltip = 'Replace pixel data in selected series by their inverse',
        pipeline = 'Tutorial__InvertPixelValuesSeries')
    menu.item(
        label = 'Invert series (copy)',
        tooltip = 'Replace pixel data in selected series by their inverse, saving the result in a new series',
        pipeline = 'Tutorial__InvertPixelValuesSeriesInNewSeries')

    menu.separator()

    menu.item(
        label = 'Demo user input display',
        pipeline = 'Tutorial__UserInput')
    menu.item(
        label = 'Gaussian filter (copy)',
        tooltip = 'Filter images with user-defined settings',
        pipeline = 'Tutorial__GaussianPixelValuesInNewSeries')
    menu.item(
        label = 'Filter (overwrite)',
        tooltip = 'Filter images with user-defined settings',
        pipeline = 'Tutorial__LocalFilterImages')
    menu.item(
        label = 'Threshold (overwrite)',
        tooltip = 'Threshold images with user-defined settings',
        pipeline = 'Tutorial__ThresholdPixelValuesInNewSeries')
    menu.item(
        label = 'Binary operations on images',
        tooltip = 'Multiply, divide, add or subtract two images',
        pipeline = 'Tutorial__BinaryOperations')