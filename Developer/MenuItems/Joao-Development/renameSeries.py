import Developer.DeveloperTools as tools
from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import PixelArrayDICOMTools as pixel
from Developer.DeveloperTools import GenericDICOMTools as dicom
import CoreModules.WEASEL.InterfaceDICOMXMLFile as interfaceDICOMXMLFile


def isSeriesOnly(self):
    return True


def main(objWeasel):
    if tools.treeView.isASeriesSelected(objWeasel):
        seriesList = ui.getSelectedSeries(objWeasel)
        series = seriesList[0]
        inputDict = {"New Series Name":"string"}
        paramList = ui.inputWindow(inputDict, title="Please type in the new series name")
        if paramList is None: return # Exit function if the user hits the "Cancel" button
        name = str(paramList[0])
        # Perform the change
        series.Item("SeriesDescription", name)
        # Change it in the TreeView
        ui.refreshWeasel(objWeasel)
    else:
        ui.showMessageWindow(objWeasel, msg="Please select a series to run this script", title="ERROR: Can't rename series")
