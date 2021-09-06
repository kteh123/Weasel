def main(weasel):
   
    menu = weasel.menu("View")

    menu.item(
        label = 'Series or Image',
        shortcut = 'Ctrl+V',
        tooltip = 'View DICOM Image or series',
        pipeline = 'View__DisplayImages',
        context = True)
    menu.item(
        label = 'Series or Image (multiple sliders)',
        shortcut = 'Ctrl+M',
        tooltip = 'View DICOM Image or series with multiple sliders',
        pipeline = 'ViewImageMultiSlider',
        context = True)
    menu.item(
        label = 'Series or Image with ROI(multiple sliders)',
        shortcut = 'Ctrl+M',
        tooltip = 'View DICOM Image or series and draw ROI with multiple sliders',
        pipeline = 'ViewImageMultiSliderROI',
        context = True)
    menu.item(
        label = 'Draw Region of Interest',
        shortcut = 'Ctrl+R',
        tooltip = 'View DICOM Image or series with the ROI tool',
        pipeline = 'ViewROIImage',
        context = True)
    menu.item(
        label = 'DICOM header',
        shortcut = 'Ctrl+M',
        tooltip = 'View DICOM Image or series header',
        pipeline = 'View__DICOMheader',
        context = True)

    menu.separator()

    menu.item(
        label = "Tile subwindows",
        shortcut = 'Ctrl+T',
        tooltip = "Arranges subwindows to a tile pattern.",
        pipeline = 'View__TileAllSubWindows',
        context = True)
    menu.item(
        label = "Close all subwindows",
        shortcut = 'Ctrl+X',
        tooltip = "Close all subwindows.",
        pipeline = 'View__CloseAllSubWindows',
        context = True)