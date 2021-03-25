
import logging
import CoreModules.WEASEL.TreeView  as treeView
import CoreModules.WEASEL.Menus as menus

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

        menus.setFileMenuItemEnabled(self, "Refresh DICOM folder", False)
        menus.setFileMenuItemEnabled(self, "Close DICOM folder", False)
        menus.setFileMenuItemEnabled(self,"Reset Tree View", False)
    except Exception as e:
        print('Error in function CloseTreeView.main: ' + str(e))
        logger.error('Error in function CloseTreeView.main: ' + str(e))
