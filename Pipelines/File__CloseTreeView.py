import logging
import CoreModules.WEASEL.TreeView as treeView

logger = logging.getLogger(__name__)

def isEnabled(weasel):
    return True

def main(weasel):
    """
    """
    try:
        logger.info("CloseTreeView.main called")
        treeView.closeTreeView(weasel)

    except Exception as e:
        print('Error in function CloseTreeView.main: ' + str(e))
        logger.error('Error in function CloseTreeView.main: ' + str(e))
