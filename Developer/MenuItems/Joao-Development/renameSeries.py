import Developer.DeveloperTools as tools
from Developer.DeveloperTools import UserInterfaceTools as ui
from Developer.DeveloperTools import PixelArrayDICOMTools as pixel
from Developer.DeveloperTools import GenericDICOMTools as dicom
import CoreModules.WEASEL.InterfaceDICOMXMLFile as interfaceDICOMXMLFile


def isSeriesOnly(self):
    #This functionality only applies to a series of DICOM images
    return True


def main(objWeasel):
    if tools.treeView.isASeriesSelected(objWeasel):
        imagePathList = ui.getImagesFromSeries(objWeasel)
        inputDict = {"New Series Name":"string"}
        paramList = ui.inputWindow(inputDict, title="Please type in the new series name")
        if paramList is None: return # Exit function if the user hits the "Cancel" button
        name = str(paramList[0])
        # Change it in the DICOM
        dicom.editDICOMTag(imagePathList, "SeriesDescription", name)
        # Change it in the XML
        interfaceDICOMXMLFile.renameSeriesinXMLFile(objWeasel, imagePathList, name)
        # Change it in the TreeView
        ui.refreshWeasel(objWeasel)
    else:
        ui.showMessageWindow(objWeasel, msg="Please select a series to run this script", title="ERROR: Can't rename series")
