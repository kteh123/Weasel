def main(weasel):
   
    menu = weasel.menu("View")

    menu.item(
        label = 'Series or Image',
        shortcut = 'Ctrl+M',
        tooltip = 'View DICOM Image or series with multiple sliders',
        pipeline = 'View__ImageMultiSlider',
        context = True)
    menu.item(
        label = 'Draw ROI',
        shortcut = 'Ctrl+M',
        tooltip = 'View DICOM Image or series and draw ROI with multiple sliders',
        pipeline = 'View__ImageMultiSliderROI',
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