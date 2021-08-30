def main(weasel):
   
    file = weasel.menu(label = "File")

    file.item(
        label = "Open DICOM folder",
        shortcut = 'Ctrl+O',
        tooltip = "If an XML file exists in the scan folder, open it. Otherwise create one and open it.",
        pipeline = 'File__OpenDICOM',
        context = True)

    file.item(
        label = "Read DICOM folder",
        shortcut = 'Ctrl+R',
        tooltip = "Read all DICOM images in the folder and open it",
        pipeline = 'File__ReadDICOM',
        context = False)

    file.item(
        label = "Close DICOM folder",
        shortcut = 'Ctrl+C',
        tooltip = "Closes the tree view and removes reference to the DICOM folder.",
        pipeline = 'File__CloseDICOM',
        context = True)

    file.item(
        label = "Tile subwindows",
        shortcut = 'Ctrl+T',
        tooltip = "Arranges subwindows to a tile pattern.",
        pipeline = 'File__TileAllSubWindows',
        context = True)

    file.item(
        label = "Close all subwindows",
        shortcut = 'Ctrl+X',
        tooltip = "Close all subwindows.",
        pipeline = 'File__CloseAllSubWindows',
        context = True)

    file.item(
        label = "Clear selections",
        shortcut = 'Ctrl+E',
        tooltip = "Uncheck all checkboxes on the tree view.",
        pipeline = 'File__ResetTreeView',
        context = True)

    file.item(
        label = "Save selections",
        shortcut = 'Ctrl+P',
        tooltip = "Saves the current state of the checkboxes on the tree view.",
        pipeline = 'File__SaveTreeView',
        context = True)

