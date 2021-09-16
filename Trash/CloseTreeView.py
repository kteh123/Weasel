
import logging
import CoreModules.TreeView  as treeView
import CoreModules.WEASEL.XMLMenuBuilder as xmlMenuBuilder

logger = logging.getLogger(__name__)

def main(self):
    """This function is executed when the Load DICOM menu item is selected.
    It displays a folder dialog box.  After the user has selected the folder
    containing the DICOM file, an existing XML is searched for.  If one is 
    found then the user is given the option of using it, rather than build
    a new one from scratch.
    """
    try:
        logger.info("CloseTreeView.main called")
        treeView.closeTreeView(self)

        xmlMenuBuilder.setFileMenuItemEnabled(self, "Refresh DICOM folder", False)
        xmlMenuBuilder.setFileMenuItemEnabled(self, "Close DICOM folder", False)
        xmlMenuBuilder.setFileMenuItemEnabled(self,"Reset Tree View", False)
        xmlMenuBuilder.setFileMenuItemEnabled(self,"Save Tree View", False)
    except Exception as e:
        print('Error in function CloseTreeView.main: ' + str(e))
        logger.error('Error in function CloseTreeView.main: ' + str(e))
