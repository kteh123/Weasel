def main(weasel):
   
    file = weasel.menu(label = "File")

    file.item(
        label = "Open DICOM folder",
        shortcut = 'Ctrl+O',
        tooltip = "If an XML file exists in the scan folder, open it. Otherwise create one and open it.",
        pipeline = 'File__LoadDICOM',
        context = True)

    file.item(
        label = "Refresh DICOM folder",
        shortcut = 'Ctrl+R',
        tooltip = "Create a new XML file for the DICOM images in the scan folder and open it.",
        pipeline = 'File__RefreshDICOM',
        context = False)

    file.item(
        label = "Tile subwindows",
        shortcut = 'Ctrl+T',
        tooltip = "Arranges subwindows to a tile pattern.",
        pipeline = 'File__TileAllSubWindows',
        context = True)

    file.item(
        label = "Close all subindows",
        shortcut = 'Ctrl+X',
        tooltip = "Close all subwindows.",
        pipeline = 'File__CloseAllSubWindows',
        context = True)

    file.item(
        label = "Reset Tree View",
        shortcut = 'Ctrl+E',
        tooltip = "Uncheck all checkboxes on the tree view.",
        pipeline = 'File__CallUnCheckTreeViewItems',
        context = True)

    file.item(
        label = "Save Tree View",
        shortcut = 'Ctrl+P',
        tooltip = "Saves the current state of the checkboxes on the tree view.",
        pipeline = 'File__RefreshDICOMStudiesTreeView',
        context = True)

    file.item(
        label = "Close DICOM folder",
        shortcut = 'Ctrl+C',
        tooltip = "Closes the tree view and removes reference to the DICOM folder.",
        pipeline = 'File__CloseTreeView',
        context = True)