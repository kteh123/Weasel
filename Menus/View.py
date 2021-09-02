def main(weasel):
   
    view = weasel.menu(label = "View")

    view.item(
        label = 'Series/Image',
        shortcut = 'Ctrl+V',
        tooltip = 'View DICOM Image or series',
        pipeline = 'View__DisplayImages',
        context = True)

    view.item(
        label = 'Series/Image with multiple sliders',
        shortcut = 'Ctrl+M',
        tooltip = 'View DICOM Image or series with multiple sliders',
        pipeline = 'ViewImageMultiSlider',
        context = True)

    view.item(
        label = 'Series/Image with ROI',
        shortcut = 'Ctrl+R',
        tooltip = 'View DICOM Image or series with the ROI tool',
        pipeline = 'ViewROIImage',
        context = True)

    view.item(
        label = 'DICOM header',
        shortcut = 'Ctrl+M',
        tooltip = 'View DICOM Image or series header',
        pipeline = 'View__DICOMheader',
        context = True)

    view.separator()

    view.item(
        label = 'Export to NIfTI',
        pipeline = 'ExportToNIfTI',
        shortcut = 'Ctrl+S',
        tooltip = 'Save selected series as NIfTI',
        context = True)