import CoreModules.DeveloperTools as tools
from CoreModules.DeveloperTools import UserInterfaceTools


def isSeriesOnly(self):
    return True


def main(objWeasel):
    ui = UserInterfaceTools(objWeasel)
    if tools.treeView.isASeriesSelected(objWeasel):
        seriesList = ui.getSelectedSeries()
        series = seriesList[0] # Because the if conditional only gets the last series selected
        inputDict = {"New Series Name":"string"}
        paramList = ui.inputWindow(inputDict, title="Please type in the new series name")
        if paramList is None: return # Exit function if the user hits the "Cancel" button
        name = str(paramList[0])
        # Perform the change
        series.Item("SeriesDescription", name)
        # Change it in the TreeView
        ui.refreshWeasel()
    else:
        ui.showMessageWindow(msg="Please select a series to run this script", title="ERROR: Can't rename series")
