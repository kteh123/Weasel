def main(weasel):
   
    menu = weasel.menu("File")

    menu.item(
        label = "Open DICOM folder",
        shortcut = 'Ctrl+O',
        tooltip = "Open a DICOM folder. If this is the first time, the folder will be read first.",
        pipeline = 'File__OpenDICOM',
        context = True)
    menu.item(
        label = "Reload DICOM folder",
        shortcut = 'Ctrl+R',
        tooltip = "Read all images in the DICOM folder",
        pipeline = 'File__ReadDICOM',
        context = False)
    menu.item(
        label = "Close DICOM folder",
        shortcut = 'Ctrl+C',
        tooltip = "Close the DICOM folder.",
        pipeline = 'File__CloseDICOM',
        context = True)

    menu.separator()

    menu.item(
        label = "Clear selections",
        shortcut = 'Ctrl+E',
        tooltip = "Uncheck all images",
        pipeline = 'File__ResetTreeView',
        context = True)

    menu.separator()

    menu.item(
        label = 'Export to NIfTI',
        shortcut = 'Ctrl+S',
        tooltip = 'Save selected series as NIfTI',
        pipeline = 'File__ExportToNIfTI',
        context = True)

    menu.item(
        label = 'Export to CSV',
        shortcut = 'Ctrl+V',
        tooltip = 'Save selected series as CSV',
        pipeline = 'File__ExportToCSV',
        context = True)